"""KPI + funnel + cohort engine. Pure functions over marts — no IO, no LLM, deterministic."""
from __future__ import annotations

import pandas as pd


def kpi_overview(fact: pd.DataFrame) -> dict:
    if fact.empty:
        return {k: 0 for k in (
            "opps", "won", "win_rate", "avg_deal", "median_deal",
            "median_cycle", "won_revenue", "open_value", "weighted_pipeline")}
    closed = fact[fact["is_closed"]]
    won = fact[fact["is_won"]]
    open_deals = fact[fact["is_open"]]
    return {
        "opps": int(len(fact)),
        "won": int(len(won)),
        "win_rate": round(len(won) / len(closed), 4) if len(closed) else 0.0,
        "avg_deal": round(float(won["close_value"].mean()), 2) if len(won) else 0.0,
        "median_deal": round(float(won["close_value"].median()), 2) if len(won) else 0.0,
        "median_cycle": round(float(won["cycle_days"].median()), 1) if len(won) else 0.0,
        "won_revenue": round(float(won["close_value"].sum()), 2),
        "open_value": round(float(open_deals["close_value"].sum()), 2),
        "weighted_pipeline": round(float(open_deals["expected_value"].sum()), 2),
    }


def funnel(fact: pd.DataFrame, order: list[str]) -> pd.DataFrame:
    """Stage mix snapshot: counts + share of all deals in scope.

    Deliberately NO stage-to-stage conversion column: a flat CRM export has no
    stage_history, so dividing snapshot counts fabricates ratios above 100%
    (e.g. 36 Qualification / 28 Prospecting = 129%). Real conversion needs
    as-of stage transitions — documented, not faked.
    """
    counts = fact["deal_stage"].value_counts()
    rows = [{"stage": s, "deals": int(counts.get(s, 0))} for s in order]
    df = pd.DataFrame(rows)
    total = int(df["deals"].sum()) or 1
    df["share"] = (df["deals"] / total).round(4)
    return df


def open_by_stage(fact: pd.DataFrame, open_stages: list[str]) -> pd.DataFrame:
    """Where current effort sits: open deals per open stage + share of open."""
    open_deals = fact[fact["is_open"]]
    counts = open_deals["deal_stage"].value_counts()
    rows = [{"stage": s, "open_deals": int(counts.get(s, 0))} for s in open_stages]
    df = pd.DataFrame(rows)
    total = int(df["open_deals"].sum()) or 1
    df["share_of_open"] = (df["open_deals"] / total).round(4)
    return df


def cohort_table(fact: pd.DataFrame, by: str) -> pd.DataFrame:
    g = fact.groupby(by, as_index=False).agg(
        deals=("opportunity_id", "count"),
        won=("is_won", "sum"),
        revenue=("close_value", lambda s: float(s[fact.loc[s.index, "is_won"]].sum())),
        avg_cycle=("cycle_days", "mean"),
    )
    g["win_rate"] = (g["won"] / g["deals"]).round(4)
    g["avg_cycle"] = g["avg_cycle"].round(1)
    g["revenue"] = g["revenue"].round(2)
    return g.sort_values("deals", ascending=False).reset_index(drop=True)


def bottleneck_flags(fact: pd.DataFrame) -> list[str]:
    """Detect where pipeline stalls. No stage_history table, so use proxies operators trust:
    early-stage pile-up share + segment cycle outliers."""
    flags: list[str] = []
    open_deals = fact[fact["is_open"]]
    if open_deals.empty:
        return ["No open pipeline — nothing to diagnose."]
    early = open_deals[open_deals["deal_stage"].isin(["Prospecting", "Qualification"])]
    share = len(early) / len(open_deals)
    if share > 0.55:
        flags.append(
            f"Qualification bottleneck: {share:.0%} of open deals still in "
            f"Prospecting/Qualification — tighten entry criteria or add SDR capacity."
        )
    med = open_deals.groupby("segment")["cycle_days"].median()
    if len(med) >= 2 and med.max() > 2 * med.min():
        slow = str(med.idxmax())
        flags.append(
            f"Cycle skew: {slow} median open age {med.max():.0f}d vs "
            f"{med.min():.0f}d fastest segment — review proposal approvals for {slow}."
        )
    commit = open_deals[open_deals["deal_stage"] == "Commit"]
    if not commit.empty and float(commit["expected_value"].sum()) < 0.15 * float(
        open_deals["expected_value"].sum()
    ):
        flags.append("Late-stage thin: <15% of weighted pipeline in Commit — close plans missing.")
    if not flags:
        flags.append("No bottleneck detected — funnel shape healthy.")
    return flags


def team_leaderboard(fact: pd.DataFrame) -> pd.DataFrame:
    g = fact.groupby(["region", "sales_agent", "manager"], as_index=False).agg(
        deals=("opportunity_id", "count"),
        won=("is_won", "sum"),
        revenue=("close_value", lambda s: float(s[fact.loc[s.index, "is_won"]].sum())),
    )
    g["win_rate"] = (g["won"] / g["deals"]).round(4)
    g["revenue"] = g["revenue"].round(2)
    return g.sort_values("revenue", ascending=False).reset_index(drop=True)


def coverage_by_region(monthly: pd.DataFrame, targets: dict[str, float],
                       month: str) -> pd.DataFrame:
    m = monthly[monthly["close_month"] == month].copy()
    rows = []
    for region, target in targets.items():
        r = m[m["region"] == region]
        open_exp = float(r["open_expected"].sum()) if not r.empty else 0.0
        won_rev = float(r["won_revenue"].sum()) if not r.empty else 0.0
        rows.append({
            "region": region,
            "target": target,
            "won_revenue": round(won_rev, 2),
            "open_expected": round(open_exp, 2),
            "coverage": round(open_exp / target, 2) if target else 0.0,
        })
    return pd.DataFrame(rows).sort_values("coverage", ascending=False).reset_index(drop=True)
