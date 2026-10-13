# KPI Dictionary — RevOps360 (all definitions verified against `src/metrics.py`)

| KPI | Formula | Grain | Notes |
|---|---|---|---|
| Win rate | `Won / Closed` where Closed = Won + Lost | overall / region / rep / cohort | Closed Lost includes rows keeping last open stage; only hard contradiction (closed+won without stage Closed Won) is quarantined |
| Avg deal size | `mean(close_value)` over Won | overall / cohort | USD, rounded to 2dp in marts |
| Median deal | `median(close_value)` over Won | overall | robust to Enterprise outliers |
| Sales cycle | `median(close_date - engage_date)` in days, Won only | overall / segment | bottleneck tab compares open-age medians by segment |
| Won revenue | `sum(close_value)` over Won | month x region (`agg_monthly`) | source for trend model |
| Open pipeline value | `sum(close_value)` over `is_closed=false` | overall | unweighted — for sizing |
| Weighted pipeline | `sum(close_value * stage_prob)` over open | month / region | `stage_prob` from `config/config.yaml`, never hardcoded |
| Coverage | `open_expected / monthly_target` | region-month | flag if `< alerts.min_coverage_ratio` (3.0x) |
| Stage mix | `deals(stage) / all deals`, `open(stage) / all open` | funnel order in config | snapshot shares only — stage-to-stage conversion is NOT reported (flat export has no stage_history; snapshot ratios exceed 100% and would mislead) |
| Forecast variance | `(predicted_trend - actual) / actual`, walk-forward (trained only on prior months) | month | weighted pipeline cannot backtest past months from a flat export (past deals are closed by construction); see `forecast.forecast_vs_actual` docstring |
| Backtest MAPE | `mean(abs(predicted-actual)/actual)` over last 3 closed months | global | reported honestly on dashboard; naive trend underperforms in Q4 push months — weighted pipeline is the primary forward forecast |
