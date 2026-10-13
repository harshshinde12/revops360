"""Metrics + forecast invariant tests. Run with: pytest -q"""
from __future__ import annotations

import pandas as pd

from src import MARTS, load_config
from src import metrics as M
from src import forecast as F


def _fact() -> pd.DataFrame:
    return pd.read_csv(MARTS / "fact_opportunity.csv")


def _monthly() -> pd.DataFrame:
    return pd.read_csv(MARTS / "agg_monthly.csv")


def test_kpi_invariants():
    k = M.kpi_overview(_fact())
    assert 0.0 <= k["win_rate"] <= 1.0
    assert k["avg_deal"] >= 0 and k["won_revenue"] >= 0
    assert k["weighted_pipeline"] >= 0


def test_funnel_sums_to_total():
    cfg = load_config()
    f = M.funnel(_fact(), list(cfg["funnel_order"]))
    assert int(f["deals"].sum()) == len(_fact())
    assert ((f["share"] >= 0) & (f["share"] <= 1)).all()
    assert "conv_from_prev" not in f.columns  # never fake conversion from snapshots
    o = M.open_by_stage(_fact(), list(cfg["open_stages"]))
    assert int(o["open_deals"].sum()) == int(_fact()["is_open"].sum())


def test_forecast_non_negative_and_scenarios_ordered():
    fact, monthly = _fact(), _monthly()
    months = sorted(monthly["close_month"].unique())
    target = months[-1]
    ens = F.ensemble_forecast(fact, monthly, target)
    assert ens["base"] >= 0 and ens["weighted"] >= 0 and ens["trend"] >= 0
    cfg = load_config()
    s = F.scenario_table(ens["base"], dict(cfg["scenarios"]))
    assert list(s["forecast"]) == sorted(s["forecast"])
    bt = F.backtest_trend(monthly)
    assert set(bt.columns) >= {"month", "predicted", "actual", "ape"}
    assert ((bt["ape"] >= 0)).all() if len(bt) else True


def test_forecast_vs_actual_walk_forward():
    monthly = _monthly()
    closed_months = sorted(monthly[monthly["won_revenue"] > 0]["close_month"].unique())[-6:]
    fva = F.forecast_vs_actual(monthly, closed_months)
    assert list(fva.columns) == ["month", "predicted_trend", "actual", "variance", "variance_pct"]
    assert len(fva) == len(closed_months)
    assert (fva["predicted_trend"] >= 0).all()
