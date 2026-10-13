# RevOps360

Sales Pipeline & Revenue Forecasting Suite — deterministic CRM analytics,
weighted + trend ensemble forecasting, executive Streamlit dashboard.

## Quickstart (local)

```bash
pip install -r requirements.txt
python -m src.seed_generator   # deterministic raw data -> data/raw/
python -m src.etl              # validate -> stage -> marts (+ audit + manifest)
pytest -q                      # ETL idempotency + analytics invariants
streamlit run app.py
```

Rerunning ETL with unchanged inputs prints `status: skipped` and leaves
`data/processed/marts/*.csv` byte-identical (verify: run twice, compare sha256).

## Deploy to Streamlit Cloud

1. Push this folder to GitHub (include `app.py`, `requirements.txt`, `src/`, `config/`).
   Do NOT commit `data/` — the app auto-generates it on first launch.
2. https://share.streamlit.io -> New app -> repo/branch -> Main file: `app.py`.
3. Python 3.12, install from `requirements.txt`. No secrets needed.
4. First load takes ~30s (seed + ETL bootstrap), then caches.

## Structure

```
config/config.yaml      # stage probs, targets, scenarios — only place business numbers live
src/seed_generator.py   # deterministic CRM seed (SEED=42), mirrors Maven schema
src/schemas.py          # Pydantic data contracts (validation gate)
src/etl.py              # raw -> staging -> marts + quarantine + manifest + audit
src/metrics.py          # KPIs, funnel, cohorts, bottlenecks (pure functions)
src/forecast.py         # weighted + trend + ensemble, scenarios, backtest, alerts
src/export.py           # board summary markdown
src/ui.py               # fintech visual system: theme CSS, KPI cards, table labels
src/charts.py           # shared Plotly palette + layout (one style, every chart)
app.py                  # Streamlit dashboard (5 tabs, filters, exports)
tests/                  # pytest: idempotency + invariants
docs/                   # kpi_dictionary, data_contract
tools/screenshot.py     # dev-only Playwright screenshot harness (not deployed)
```

## Deliverables mapped to brief

1. GitHub repo with ETL scripts + dashboard configs — this repo.
2. KPI dictionary — `docs/kpi_dictionary.md`.
3. Forecast dashboard with region/team filters — `app.py` Forecast + Teams tabs,
   export via Download buttons (CSV + board Markdown).
