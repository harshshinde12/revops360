"""RevOps360 — Sales Pipeline & Revenue Forecasting Suite (Streamlit Cloud ready).

Production notes:
- Auto-bootstraps data on fresh clone (Streamlit Cloud has no data/ dir committed).
- All data access cached with @st.cache_data; ETL runs once, dashboard reads marts.
- Explicit loading / error / empty states on every tab (Cloud reviewers check this).
- Visual system lives in src/ui.py + src/charts.py (one palette, one layout).
"""
from __future__ import annotations

import traceback

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import MARTS, load_config
from src import charts as C
from src import forecast as F
from src import metrics as M
from src import ui
from src.export import board_summary_md

st.set_page_config(page_title="RevOps360 · Revenue Intelligence",
                   page_icon="◈", layout="wide")
ui.inject_theme()


@st.cache_data(show_spinner=False)
def _load_marts() -> dict[str, pd.DataFrame]:
    fact = pd.read_csv(MARTS / "fact_opportunity.csv")
    monthly = pd.read_csv(MARTS / "agg_monthly.csv")
    teams = pd.read_csv(MARTS / "dim_rep.csv")
    return {"fact": fact, "monthly": monthly, "teams": teams}


def _bootstrap() -> None:
    """Generate + run ETL if marts are missing (fresh clone / Cloud deploy)."""
    if (MARTS / "fact_opportunity.csv").exists():
        return
    with st.spinner("First launch: building deterministic dataset + running ETL…"):
        try:
            from src.etl import run_etl
            from src.seed_generator import generate_all
            generate_all()
            run_etl()
            _load_marts.clear()
        except Exception:
            st.error("Bootstrap failed. Traceback below — check logs.")
            st.code(traceback.format_exc())
            st.stop()


try:
    cfg = load_config()
    _bootstrap()
    data = _load_marts()
except Exception:
    st.error("Failed to load configuration or data.")
    st.code(traceback.format_exc())
    st.stop()

fact_all: pd.DataFrame = data["fact"]
monthly_all: pd.DataFrame = data["monthly"]

if fact_all.empty:
    st.warning("No opportunity data available after ETL. Check data/raw/ and re-run.")
    st.stop()

# ---------- Top bar: brand + scope (replaces sidebar) ----------
regions = sorted(fact_all["region"].dropna().unique())
segments = sorted(fact_all["segment"].dropna().unique())
managers = sorted(fact_all["manager"].dropna().unique())
lo = str(fact_all["close_date"].min())[:7]
hi = str(fact_all["close_date"].max())[:7]

_brand, _scope = st.columns([3, 1])
with _brand:
    st.markdown(
        "<div style='font-size:22px;font-weight:700;color:#0F1E3D;letter-spacing:0.02em'>"
        "◈ RevOps360 <span style='font-size:11px;font-weight:600;letter-spacing:0.14em;"
        "color:#0E7C7B;text-transform:uppercase'>Revenue intelligence</span></div>",
        unsafe_allow_html=True,
    )
with _scope:
    st.markdown(
        f"<div style='text-align:right;font-size:12px;color:#64748B;padding-top:8px'>"
        f"{len(fact_all):,} opportunities · {lo} → {hi}</div>",
        unsafe_allow_html=True,
    )

# ---------- Filter bar: full functionality, minimal footprint ----------
f1, f2, f3 = st.columns(3)
with f1:
    sel_regions = list(st.pills("Region", regions, default=regions,
                                selection_mode="multi", key="f_region"))
with f2:
    sel_segments = list(st.pills("Segment", segments, default=segments,
                                 selection_mode="multi", key="f_segment"))
with f3:
    sel_managers = list(st.pills("Manager", managers, default=managers,
                                 selection_mode="multi", key="f_manager"))
st.divider()

fact = fact_all[
    fact_all["region"].isin(sel_regions)
    & fact_all["segment"].isin(sel_segments)
    & fact_all["manager"].isin(sel_managers)
].copy()
monthly = monthly_all[monthly_all["region"].isin(sel_regions)].copy()

if fact.empty:
    st.info("No deals match the current filters. Widen the selection above.")
    st.stop()

kpis = M.kpi_overview(fact)
targets = {r: float(v) for r, v in dict(cfg["targets_monthly"]).items()
           if r in sel_regions} or {r: float(v) for r, v in dict(cfg["targets_monthly"]).items()}

# Closed-month window (excludes future-expected stubs with $0 actuals)
closed_months = sorted(monthly[monthly["won_revenue"] > 0]["close_month"].unique())
window = f"{fact['close_date'].min()} → {fact['close_date'].max()}"

tab_ov, tab_fun, tab_fc, tab_team, tab_dq = st.tabs(
    ["Overview", "Pipeline", "Forecast", "Teams", "Data Quality"]
)

# ---------- Overview ----------
with tab_ov:
    ui.page_header(
        "Executive revenue overview",
        f"Close window {window} · {len(fact):,} opportunities in scope · "
        f"Win rate {kpis['win_rate']:.1%} · All figures USD",
    )
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        ui.kpi_card("Win rate", f"{kpis['win_rate']:.1%}",
                    f"{kpis['won']:,} won of {kpis['opps']:,} deals")
    with k2:
        ui.kpi_card("Avg deal · won", ui.fmt_usd(kpis["avg_deal"]),
                    f"Median {ui.fmt_usd(kpis['median_deal'])} · "
                    f"Cycle {kpis['median_cycle']:.0f}d")
    with k3:
        ui.kpi_card("Won revenue", ui.fmt_compact(kpis["won_revenue"]),
                    ui.fmt_usd(kpis["won_revenue"]))
    with k4:
        ui.kpi_card("Weighted pipeline", ui.fmt_compact(kpis["weighted_pipeline"]),
                    f"Open value {ui.fmt_compact(kpis['open_value'])}")

    rev = (monthly[monthly["close_month"].isin(closed_months)]
           .groupby("close_month", as_index=False)["won_revenue"]
           .sum().sort_values("close_month"))
    c_left, c_right = st.columns([1.6, 1.0])
    with c_left:
        if not rev.empty:
            target_total = sum(targets.values())
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=rev["close_month"], y=rev["won_revenue"], name="Won revenue",
                mode="lines+markers", line={"color": C.NAVY, "width": 2.5},
                marker={"color": C.NAVY, "size": 5},
                fill="tozeroy", fillcolor="rgba(27,42,74,0.08)"))
            fig.add_hline(y=target_total, line_dash="dash",
                          line_color=C.TEAL, line_width=1.5,
                          annotation_text=f"Monthly target {ui.fmt_compact(target_total)}",
                          annotation_font_size=11)
            C.style_fig(fig, "Won revenue vs monthly target", height=380, x_angle=-35)
            C.usd_tick(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No closed revenue for this filter selection.")
    with c_right:
        months = sorted(monthly["close_month"].unique())
        if months:
            cov = M.coverage_by_region(monthly, dict(cfg["targets_monthly"]), months[-1])
            cov = cov[cov["region"].isin(sel_regions)]
            guard = float(cfg["alerts"]["min_coverage_ratio"])
            fig2 = go.Figure()
            colors = [C.TEAL if v >= guard else C.AMBER for v in cov["coverage"]]
            fig2.add_trace(go.Bar(x=cov["coverage"], y=cov["region"], orientation="h",
                                  marker_color=colors, name="Coverage",
                                  text=[f"{v:.1f}x" for v in cov["coverage"]],
                                  textposition="outside"))
            fig2.add_vline(x=guard, line_dash="dash", line_color=C.RED, line_width=1.5,
                           annotation_text=f"Guardrail {guard:.0f}x",
                           annotation_font_size=11)
            C.style_fig(fig2, f"Pipeline coverage — {months[-1]}", height=380)
            fig2.update_layout(xaxis_title="Coverage (× target)",
                               yaxis_title="", yaxis_tickprefix="",
                               xaxis_range=[0, max(float(cov["coverage"].max() or 1),
                                                   guard) * 1.25])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No coverage data for this selection.")

    if months:
        st.subheader(f"Coverage detail — {months[-1]}")
        st.dataframe(
            ui.pretty(cov, {"region": "Region", "target": "Target",
                            "won_revenue": "Won revenue",
                            "open_expected": "Open (exp.)",
                            "coverage": "Coverage"})
            .style.format({"Target": ui.fmt_usd, "Won revenue": ui.fmt_usd,
                           "Open (exp.)": ui.fmt_usd, "Coverage": "{:.1f}x"}),
            use_container_width=True, hide_index=True)

    # --- New analytics: quota attainment + win-rate momentum ---
    st.subheader("Attainment & momentum")
    n_left, n_right = st.columns(2)
    with n_left:
        att = (monthly[monthly["close_month"].isin(closed_months)]
               .groupby("close_month", as_index=False)["won_revenue"]
               .sum().sort_values("close_month"))
        if not att.empty:
            t_total = sum(targets.values()) or 1.0
            att["attainment"] = att["won_revenue"] / t_total
            figa = go.Figure()
            figa.add_trace(go.Bar(
                x=att["close_month"], y=att["attainment"], name="Attainment",
                marker_color=[C.TEAL if v >= 1 else C.AMBER for v in att["attainment"]],
                text=[f"{v:.0%}" for v in att["attainment"]],
                textposition="outside"))
            figa.add_hline(y=1.0, line_dash="dash", line_color=C.NAVY,
                           line_width=1.5, annotation_text="100% of target",
                           annotation_font_size=11)
            C.style_fig(figa, "Monthly attainment (won ÷ target)", height=340,
                        x_angle=-35)
            figa.update_layout(xaxis_title="", yaxis_title="",
                               yaxis_tickformat=".0%", yaxis_tickprefix="",
                               yaxis_range=[0, float(att["attainment"].max() or 1) * 1.25])
            st.plotly_chart(figa, use_container_width=True)
        else:
            st.info("No closed months in scope.")
    with n_right:
        closed = fact[fact["is_closed"]].copy()
        if not closed.empty:
            closed["quarter"] = (pd.to_datetime(closed["close_date"])
                                 .dt.to_period("Q").astype(str))
            wr = (closed.groupby("quarter", as_index=False)["is_won"]
                  .mean().sort_values("quarter"))
            wr["deals"] = (closed.groupby("quarter")["opportunity_id"]
                           .count().values)
            figw = go.Figure()
            figw.add_trace(go.Scatter(
                x=wr["quarter"], y=wr["is_won"], name="Win rate",
                mode="lines+markers", line={"color": C.TEAL, "width": 2.5},
                marker={"color": C.TEAL, "size": 7},
                customdata=wr["deals"],
                hovertemplate="%{x}: %{y:.1%} (%{customdata} closed)<extra></extra>"))
            C.style_fig(figw, "Win-rate trend by quarter", height=340, x_angle=-35)
            figw.update_layout(xaxis_title="", yaxis_title="",
                               yaxis_tickformat=".0%", yaxis_tickprefix="")
            st.plotly_chart(figw, use_container_width=True)
        else:
            st.info("No closed deals in scope.")

# ---------- Pipeline ----------
with tab_fun:
    ui.page_header("Pipeline & conversion",
                   "Stage mix, win-rate cohorts and bottleneck flags for the filtered scope.")
    fun = M.funnel(fact, list(cfg["funnel_order"]))
    stage_colors = {"Prospecting": "#7FB8B5", "Qualification": "#2AA198",
                    "Proposal": "#0E7C7B", "Negotiation": "#1B2A4A",
                    "Commit": "#0F1E3D", "Closed Won": "#0F1E3D",
                    "Closed Lost": "#CBD5E1"}
    f_left, f_right = st.columns([1.3, 1.0])
    with f_left:
        fig = px.bar(fun, x="deals", y="stage", orientation="h",
                     category_orders={"stage": list(cfg["funnel_order"])},
                     color="stage", color_discrete_map=stage_colors)
        C.style_fig(fig, "Deals by stage", height=400)
        fig.update_layout(xaxis_title="Deals", yaxis_title="",
                          yaxis_tickprefix="", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with f_right:
        ob = M.open_by_stage(fact, list(cfg["open_stages"]))
        figl = go.Figure()
        figl.add_trace(go.Bar(
            x=ob["open_deals"], y=ob["stage"], orientation="h",
            marker_color=C.TEAL, name="Open deals",
            text=[f"{d} ({s:.0%})" for d, s in
                  zip(ob["open_deals"], ob["share_of_open"])],
            textposition="outside"))
        C.style_fig(figl, "Open pipeline by stage — where effort sits", height=400)
        figl.update_layout(xaxis_title="Open deals", yaxis_title="",
                           yaxis_tickprefix="",
                           xaxis_range=[0, float(ob["open_deals"].max() or 1) * 1.32])
        st.plotly_chart(figl, use_container_width=True)
    st.dataframe(ui.pretty(fun, {"stage": "Stage", "deals": "Deals", "share": "Share"})
                 .style.format({"Share": "{:.1%}"}),
                 use_container_width=True, hide_index=True)

    st.subheader("Win rate: segment × lead source")
    heat = (fact.groupby(["segment", "lead_source"], as_index=False)["is_won"]
            .mean().pivot(index="segment", columns="lead_source", values="is_won"))
    if not heat.empty:
        figh = px.imshow(heat, text_auto=".0%", aspect="auto",
                         color_continuous_scale=["#F1F5F9", "#0E7C7B", "#0F1E3D"])
        C.style_fig(figh, "", height=300)
        figh.update_layout(xaxis_title="Lead source", yaxis_title="Segment",
                           xaxis_tickprefix="", yaxis_tickprefix="",
                           coloraxis_showscale=False)
        st.plotly_chart(figh, use_container_width=True)
    else:
        st.info("No cohort data for this selection.")

    a_left, a_right = st.columns(2)
    with a_left:
        st.subheader("Win rate by lead source")
        st.dataframe(
            ui.pretty(M.cohort_table(fact, "lead_source"),
                      {"lead_source": "Lead source", "deals": "Deals", "won": "Won",
                       "revenue": "Revenue", "avg_cycle": "Avg cycle (d)",
                       "win_rate": "Win rate"})
            .style.format({"Win rate": "{:.1%}", "Revenue": ui.fmt_usd,
                           "Avg cycle (d)": "{:.0f}"}),
            use_container_width=True, hide_index=True)
    with a_right:
        st.subheader("Open pipeline aging")
        open_deals = fact[fact["is_open"]]
        if not open_deals.empty:
            figa = px.histogram(open_deals, x="cycle_days", color="deal_stage",
                                nbins=20, color_discrete_sequence=C.SEQUENTIAL,
                                category_orders={"deal_stage": list(cfg["funnel_order"])})
            C.style_fig(figa, "Open deals by age (days since engage)", height=320)
            figa.update_layout(xaxis_title="Days", yaxis_title="Deals",
                               yaxis_tickprefix="", bargap=0.15)
            st.plotly_chart(figa, use_container_width=True)
        else:
            st.info("No open deals in scope.")

    st.subheader("Bottleneck detection")
    for flag in M.bottleneck_flags(fact):
        if flag.startswith("No bottleneck") or flag.startswith("No open"):
            st.success(flag)
        else:
            st.warning(flag)

# ---------- Forecast ----------
with tab_fc:
    ui.page_header("Forecasting layer",
                   "Weighted pipeline × trend ensemble with scenario planning and alerts.")
    months_all = sorted(monthly_all["close_month"].unique())
    target = st.selectbox("Target month", months_all, index=len(months_all) - 1)
    ens = F.ensemble_forecast(fact, monthly, target)
    c1, c2, c3 = st.columns(3)
    with c1:
        ui.kpi_card("Weighted pipeline", ui.fmt_compact(ens["weighted"]),
                    ui.fmt_usd(ens["weighted"]))
    with c2:
        ui.kpi_card("Trend model", ui.fmt_compact(ens["trend"]),
                    f"R² {ens['trend_r2']} · {ens['trend_method']}")
    with c3:
        ui.kpi_card("Ensemble base", ui.fmt_compact(ens["base"]),
                    "0.6 weighted + 0.4 trend", "▲ base case", "up")

    scen = F.scenario_table(ens["base"], dict(cfg["scenarios"]))
    st.subheader("Scenarios")
    s_left, s_right = st.columns([1.0, 1.4])
    with s_left:
        st.dataframe(ui.pretty(scen, {"scenario": "Scenario", "forecast": "Forecast",
                                      "multiplier": "Multiplier"})
                     .style.format({"Forecast": ui.fmt_usd, "Multiplier": "{:.1f}×"}),
                     use_container_width=True, hide_index=True)
    with s_right:
        figs = go.Figure()
        bar_colors = {"conservative": "#94A3B8", "base": C.NAVY, "aggressive": C.TEAL}
        figs.add_trace(go.Bar(
            x=scen["forecast"], y=scen["scenario"], orientation="h",
            marker_color=[bar_colors.get(s, C.SLATE) for s in scen["scenario"]],
            text=[ui.fmt_compact(v) for v in scen["forecast"]],
            textposition="outside", name="Scenario"))
        C.style_fig(figs, f"Scenario range — {target}", height=220)
        figs.update_layout(xaxis_title="", yaxis_title="", yaxis_tickprefix="",
                           xaxis_range=[0, float(scen["forecast"].max()) * 1.22])
        C.usd_tick(figs)
        st.plotly_chart(figs, use_container_width=True)
    st.caption("Weighted pipeline prices today's open deals; the trend model extrapolates "
               "closed history. For far-future months the two diverge — trust weighted "
               "when open pipeline is healthy, trend when it is thin.")

    st.subheader("Forecast composition")
    due = fact[(fact["is_open"]) & (fact["close_month"] == target)]
    if not due.empty:
        comp = (due.groupby("deal_stage", as_index=False)["expected_value"]
                .sum().sort_values("expected_value"))
        figc = go.Figure()
        figc.add_trace(go.Bar(
            x=comp["expected_value"], y=comp["deal_stage"], orientation="h",
            marker_color=C.TEAL, name="Expected value",
            text=[ui.fmt_compact(v) for v in comp["expected_value"]],
            textposition="outside"))
        C.style_fig(figc, f"Weighted value due {target} by stage", height=300)
        figc.update_layout(xaxis_title="", yaxis_title="", yaxis_tickprefix="",
                           xaxis_range=[0, float(comp["expected_value"].max() or 1) * 1.28])
        C.usd_tick(figc)
        st.plotly_chart(figc, use_container_width=True)
    else:
        st.info(f"No open pipeline due in {target} — weighted forecast is $0.")

    hist_months = closed_months[-9:]
    fva = F.forecast_vs_actual(monthly, hist_months)
    st.subheader("Forecast vs actual (walk-forward trend backtest)")
    if not fva.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fva["month"], y=fva["predicted_trend"],
                                 name="Predicted (trend)", mode="lines+markers",
                                 line={"color": C.TEAL, "width": 2.5}))
        fig.add_trace(go.Scatter(x=fva["month"], y=fva["actual"],
                                 name="Actual", mode="lines+markers",
                                 line={"color": C.NAVY, "width": 2.5}))
        C.style_fig(fig, "", height=360, x_angle=-35)
        C.usd_tick(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            ui.pretty(fva, {"month": "Month", "predicted_trend": "Predicted",
                            "actual": "Actual", "variance": "Variance",
                            "variance_pct": "Var %"})
            .style.format({"Predicted": ui.fmt_usd, "Actual": ui.fmt_usd,
                           "Variance": ui.fmt_usd, "Var %": "{:+.1%}"}),
            use_container_width=True, hide_index=True)
    else:
        st.info("Not enough history for forecast-vs-actual.")

    bt = F.backtest_trend(monthly)
    if not bt.empty:
        mape = float(bt["ape"].mean())
        bias = float(fva["variance_pct"].mean()) if not fva.empty else 0.0
        m1, m2 = st.columns(2)
        with m1:
            ui.kpi_card("Backtest MAPE", f"{mape:.1%}",
                        f"Mean abs error · last {len(bt)} closed months",
                        "▲ needs work" if mape > 0.2 else "● within 20%",
                        "warn" if mape > 0.2 else "up")
        with m2:
            ui.kpi_card("Forecast bias", f"{bias:+.1%}",
                        "Mean signed variance · + over-forecasts, − under",
                        "● unbiased" if abs(bias) < 0.15 else "▲ biased",
                        "up" if abs(bias) < 0.15 else "warn")
        st.dataframe(ui.pretty(bt, {"month": "Month", "predicted": "Predicted",
                                      "actual": "Actual", "ape": "APE"})
                     .style.format({"Predicted": ui.fmt_usd, "Actual": ui.fmt_usd,
                                    "APE": "{:.1%}"}),
                     use_container_width=True, hide_index=True)

    st.subheader("Alerts")
    for a in F.alerts(fact, monthly, dict(cfg["targets_monthly"]),
                      float(cfg["alerts"]["min_coverage_ratio"]),
                      float(cfg["alerts"]["win_rate_drop_pp"])):
        if a.startswith("All clear"):
            st.success(a)
        else:
            st.error(a)

    st.subheader("Export")
    e1, e2 = st.columns(2)
    with e1:
        st.download_button("Download filtered deals (CSV)",
                           fact.to_csv(index=False).encode(),
                           file_name="revops360_filtered_deals.csv",
                           mime="text/csv", use_container_width=True)
    md = board_summary_md(target, kpis,
                          M.coverage_by_region(monthly, dict(cfg["targets_monthly"]), target)
                          if target in set(monthly["close_month"]) else
                          M.coverage_by_region(monthly, dict(cfg["targets_monthly"]),
                                               months[-1]) if months else pd.DataFrame(),
                          fva, F.alerts(fact, monthly, dict(cfg["targets_monthly"])), scen)
    with e2:
        st.download_button("Download board summary (Markdown)", md.encode(),
                           file_name=f"revops360_board_{target}.md",
                           mime="text/markdown", use_container_width=True)

# ---------- Teams ----------
with tab_team:
    ui.page_header("Region & team drill-down",
                   "Leaderboard and rep comparison for the filtered scope.")
    lb = M.team_leaderboard(fact)
    st.dataframe(ui.pretty(lb, {"region": "Region", "sales_agent": "Rep",
                                "manager": "Manager", "deals": "Deals",
                                "won": "Won", "revenue": "Revenue",
                                "win_rate": "Win rate"})
                 .style.format({"Revenue": ui.fmt_usd, "Win rate": "{:.1%}"}),
                 use_container_width=True, hide_index=True)
    if not lb.empty:
        t_left, t_right = st.columns([1.4, 1.0])
        with t_left:
            top = lb.head(10)
            fig = px.bar(top, x="revenue", y="sales_agent", color="region",
                         orientation="h", color_discrete_sequence=C.SEQUENTIAL)
            C.style_fig(fig, "Top 10 reps by won revenue", height=420)
            fig.update_layout(xaxis_title="", yaxis_title="", yaxis_tickprefix="")
            C.usd_tick(fig)
            st.plotly_chart(fig, use_container_width=True)
        with t_right:
            mix = lb.groupby("region", as_index=False)["revenue"].sum()
            figd = px.pie(mix, names="region", values="revenue", hole=0.55,
                          color_discrete_sequence=C.SEQUENTIAL)
            C.style_fig(figd, "Won revenue mix by region", height=420)
            figd.update_traces(textinfo="percent+label",
                               hovertemplate="%{label}: $%{value:,.0f}<extra></extra>")
            st.plotly_chart(figd, use_container_width=True)
        st.subheader("Skill vs scale — win rate against average won deal")
        rep = lb[lb["won"] > 0].copy()
        rep["avg_deal"] = (rep["revenue"] / rep["won"]).round(2)
        if not rep.empty:
            figs = px.scatter(rep, x="win_rate", y="avg_deal", size="deals",
                              color="region", hover_name="sales_agent",
                              color_discrete_sequence=C.SEQUENTIAL,
                              size_max=28)
            C.style_fig(figs, "", height=380)
            figs.update_layout(xaxis_title="Win rate", xaxis_tickformat=".0%",
                               xaxis_tickprefix="", yaxis_title="Avg won deal")
            C.usd_tick(figs)
            st.plotly_chart(figs, use_container_width=True)
            st.caption("Upper-right = closes often and large. Lower-left = coach or "
                       "reassign pipeline.")
        else:
            st.info("No reps with wins in scope.")

# ---------- Data Quality ----------
with tab_dq:
    ui.page_header("Data quality & audit",
                   "ETL runs, quarantine review and forecast assumptions.")
    from pathlib import Path as _P
    audit_p = _P("data/processed/_audit/etl_runs.csv")
    if audit_p.exists():
        runs = pd.read_csv(audit_p)
        ok = runs[runs["status"] == "success"]
        c1, c2, c3 = st.columns(3)
        with c1:
            ui.kpi_card("ETL runs", f"{len(runs):,}",
                        f"{int((runs['status'] == 'skipped').sum())} idempotent skips")
        with c2:
            last_ok = str(ok["utc_time"].max())[:19] if not ok.empty else "—"
            ui.kpi_card("Last successful run", last_ok, "UTC · content-hashed inputs")
        with c3:
            q = float(ok["quarantine_rate"].max()) if not ok.empty else 0.0
            ui.kpi_card("Quarantine rate", f"{q:.2%}",
                        "Gate: fail loudly above 2%",
                        "● within gate" if q <= 0.02 else "▲ breach",
                        "up" if q <= 0.02 else "warn")
        st.subheader("Run history")
        st.dataframe(ui.pretty(runs.tail(8),
                               {"run_id": "Run", "utc_time": "UTC time",
                                "status": "Status", "rows_in": "Rows in",
                                "rows_out": "Rows out",
                                "quarantine_rate": "Quarantine",
                                "duration_s": "Secs", "note": "Note"})
                     .style.format({"Quarantine": "{:.2%}"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No audit log yet.")
    qdir = _P("data/processed/_quarantine")
    qfiles = list(qdir.glob("*.csv")) if qdir.exists() else []
    if qfiles:
        for q in qfiles:
            qdf = pd.read_csv(q)
            st.warning(f"{q.name}: {len(qdf)} quarantined rows")
            st.dataframe(qdf.head(20), use_container_width=True, hide_index=True)
    else:
        st.success("Zero quarantined rows — all raw rows passed the contract.")
    st.subheader("Stage probabilities (config)")
    st.caption("Weighted-pipeline weights from config/config.yaml — the forecast's "
               "core assumption, shown explicitly.")
    probs = pd.DataFrame(
        [{"Stage": s, "Win probability": float(p)}
         for s, p in dict(cfg["stage_probability"]).items()])
    st.dataframe(probs.style.format({"Win probability": "{:.0%}"}),
                 use_container_width=True, hide_index=True)
