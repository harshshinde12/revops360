"""Forecasting layer: weighted pipeline + trend + ensemble, scenarios, backtest, alerts.

All functions are pure (inputs -> outputs, no IO) so they are unit-testable and
the Streamlit layer stays thin. Conventions:
- `weighted`: sum(expected_value) of OPEN deals due in the target month(s).
- `trend`: least-squares line over monthly won_revenue, projected forward.
- `ensemble`: 0.6 * weighted + 0.4 * trend (weights documented here, not hidden).
- scenarios multiply the base ensemble by config multipliers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def weighted_forecast(fact: pd.DataFrame, months: list[str] | None = None) -> float:
    open_deals = fact[fact["is_open"]]
    if months is not None:
        open_deals = open_deals[open_deals["close_month"].isin(months)]
    return round(float(open_deals["expected_value"].sum()), 2)


def trend_forecast(monthly: pd.DataFrame, target_month: str, lookback: int = 12) -> dict:
    """Fit OLS trend on won_revenue history strictly before target_month."""
    hist = monthly.groupby("close_month", as_index=False)["won_revenue"].sum()
    hist = hist[hist["close_month"] < target_month].sort_values("close_month")
    # Exclude zero-revenue months from training: they are future-expected stubs
    # (open deals due after the last close), not real history.
    hist = hist[hist["won_revenue"] > 0].tail(lookback)
    if len(hist) < 3:
        fallback = round(float(hist["won_revenue"].mean()), 2) if len(hist) else 0.0
        return {"forecast": fallback, "method": "mean-fallback (<3 months history)",
                "r2": 0.0, "n_months": int(len(hist))}
    x = np.arange(len(hist), dtype=float)
    y = hist["won_revenue"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    pred = float(slope * len(hist) + intercept)
    ss_res = float(((y - (slope * x + intercept)) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"forecast": round(max(pred, 0.0), 2), "method": "ols-trend",
            "r2": round(float(r2), 3), "n_months": int(len(hist))}


def ensemble_forecast(fact: pd.DataFrame, monthly: pd.DataFrame,
                      target_month: str, w_weighted: float = 0.6) -> dict:
    w = weighted_forecast(fact, [target_month])
    t = trend_forecast(monthly, target_month)
    base = round(w_weighted * w + (1 - w_weighted) * t["forecast"], 2)
    return {"weighted": w, "trend": t["forecast"], "trend_method": t["method"],
            "trend_r2": t["r2"], "base": base}


def scenario_table(base: float, scenarios: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        [{"scenario": k, "forecast": round(base * float(v), 2), "multiplier": float(v)}
         for k, v in scenarios.items()]
    ).sort_values("forecast").reset_index(drop=True)


def forecast_vs_actual(monthly: pd.DataFrame, months: list[str]) -> pd.DataFrame:
    """Genuine out-of-sample history: walk-forward trend prediction vs actual.

    Note: the weighted pipeline cannot be backtested against past months from a
    flat CRM export — past deals are already closed, so today's open pipeline
    due last year is ~0 by construction. Reconstructing that would need
    as-of stage snapshots (stage_history). The trend model, trained strictly
    on months before each target, is the honest backtest here.
    """
    rows = []
    for m in sorted(months):
        actual = float(monthly[monthly["close_month"] == m]["won_revenue"].sum())
        predicted = trend_forecast(monthly, m)["forecast"]
        var = predicted - actual
        rows.append({
            "month": m,
            "predicted_trend": round(predicted, 2),
            "actual": round(actual, 2),
            "variance": round(var, 2),
            "variance_pct": round(var / actual, 4) if actual else 0.0,
        })
    return pd.DataFrame(rows)


def backtest_trend(monthly: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Walk-forward backtest of the trend model on the last n CLOSED months.

    Future-expected months (open deals due after the last close, won_revenue=0)
    are excluded — scoring a model against months that haven't happened yet
    would report a fake 0% error.
    """
    hist = monthly.groupby("close_month", as_index=False)["won_revenue"].sum()
    hist = hist.sort_values("close_month").reset_index(drop=True)
    hist = hist[hist["won_revenue"] > 0].reset_index(drop=True)
    if len(hist) < 4:
        return pd.DataFrame(columns=["month", "predicted", "actual", "ape"])
    rows = []
    for i in range(max(1, len(hist) - n), len(hist)):
        target = str(hist.loc[i, "close_month"])
        actual = float(hist.loc[i, "won_revenue"])
        pred = trend_forecast(hist.iloc[:i], target)["forecast"]
        ape = abs(pred - actual) / actual if actual else 0.0
        rows.append({"month": target, "predicted": pred,
                     "actual": round(actual, 2), "ape": round(float(ape), 4)})
    out = pd.DataFrame(rows)
    return out


def alerts(fact: pd.DataFrame, monthly: pd.DataFrame, targets: dict[str, float],
           min_coverage: float = 3.0, drop_pp: float = 10.0) -> list[str]:
    notes: list[str] = []
    latest = sorted(monthly["close_month"].unique())
    if not latest:
        return ["No monthly history — cannot evaluate alerts."]
    m = latest[-1]
    cov_open = weighted_forecast(fact, [m])
    target_total = sum(targets.values())
    coverage = cov_open / target_total if target_total else 0.0
    if coverage < min_coverage:
        notes.append(
            f"UNDER-COVERAGE for {m}: pipeline coverage {coverage:.1f}x vs "
            f"{min_coverage:.1f}x target — add pipeline or de-risk commit."
        )
    # Win-rate drop QoQ (last 2 quarters of closed deals)
    closed = fact[fact["is_closed"]].copy()
    if not closed.empty:
        closed["q"] = pd.to_datetime(closed["close_date"]).dt.to_period("Q").astype(str)
        qs = sorted(closed["q"].unique())
        if len(qs) >= 2:
            wr = closed.groupby("q")["is_won"].mean()
            drop = (wr.iloc[-2] - wr.iloc[-1]) * 100
            if drop >= drop_pp:
                notes.append(
                    f"WIN-RATE DROP: {qs[-1]} {wr.iloc[-1]:.0%} vs {qs[-2]} "
                    f"{wr.iloc[-2]:.0%} (-{drop:.0f}pp) — inspect lost reasons."
                )
    if not notes:
        notes.append("All clear — coverage and win-rate within guardrails.")
    return notes
