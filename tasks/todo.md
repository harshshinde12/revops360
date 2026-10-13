# RevOps360 — Build Plan (goal: 100% production-ready, Streamlit Cloud deployable)

Goal state: `streamlit run app.py` works from fresh clone, ETL is idempotent,
all rows validated, tests pass, dashboard has loading/error/empty states, exports work.

## RESULT: GOAL ACHIEVED (verified 2026-09-22)
- ETL: 2942 rows in -> 2600 fact rows, 0 quarantined, rerun = skipped + byte-identical
- Tests: 7 passed (`pytest -q`)
- Dashboard: headless boot OK, health endpoint 200
- Deploy: push to GitHub, Streamlit Cloud main file `app.py` (auto-bootstraps data)

## UI UPGRADE — 3 iterations, screenshot-verified (2026-09-22)
- ITER1 goal (formal shell): navy sidebar, KPI cards, shared palette, formatted tables — verified via iter1 screenshots; fixed $West axis bug + duplicate header.
- ITER2 goal (deeper analytics): conversion-leak chart (REJECTED on review: snapshot ratios hit 129%, replaced with honest open-by-stage), cohort heatmap, aging histogram, scenario bars, MAPE/bias cards, mix donut, skill-vs-scale scatter — verified via iter2/iter2b screenshots.
- ITER3 goal (polish + hardening): fixed $$ axis bug, bar-label clipping, boardroom column labels, DQ summary cards, README/.gitignore — verified via iter3/iter4 screenshots, 7 tests green.
- Dev-only: tools/screenshot.py (Playwright, not deployed, not in requirements).

## Verified decisions
- [x] Real CRM downloads (Maven/Kaggle) require login -> cannot be a hard runtime dependency.
- Decision: deterministic seed generator (SEED=42) mirroring Maven `sales_pipeline` schema,
  extended with `segment`, `lead_source`, full 7-stage funnel, 2023-01..2024-12.
  Real CSV drop-in supported via same contract (`docs/data_contract.md`).
- [x] Stack: Python + Pandas + Pydantic + Streamlit + Plotly. No Pandera/Great Expectations
  (too heavy for Streamlit Cloud free tier).

## Work loop: think -> search -> verify -> plan -> verify -> implement -> verify

### 1. ETL (industry practices, not student practices)
- [ ] Medallion: `data/raw/` immutable -> `data/staging/` typed -> `data/processed/marts/` star schema
- [ ] Data contract enforced with Pydantic before any logic (`src/schemas.py`)
- [ ] Quarantine pattern: bad rows -> `data/processed/_quarantine/` with reason, never silently dropped
- [ ] Content-hash idempotency: `manifest.json` (sha256 per file + generator version); rerun = byte-identical output
- [ ] Audit log: `data/processed/_audit/etl_runs.csv` (run_id, timestamps, in/out counts, quarantine rate, duration)
- [ ] Config-driven: `config/config.yaml` (stage probs, targets, scenarios) — zero magic numbers in code
- [ ] Surrogate keys via stable hash (SCD Type 1 dims)
- Verify: run ETL twice, `sha256` of marts identical; quarantine rate < 2%; audit row appended

### 2. Analytics engine
- [ ] `src/metrics.py`: win_rate, avg/median deal, cycle time, coverage, funnel conversion, cohorts, bottlenecks
- [ ] `src/forecast.py`: weighted pipeline + linear-trend + ensemble, 3 scenarios, backtest MAPE, alerts
- [ ] `tests/`: invariants (rates in [0,1], forecast >= 0), idempotency, no-NaN marts
- Verify: `pytest -q` all green

### 3. Dashboard
- [ ] `app.py`: Overview / Funnel / Forecast / Teams / Data Quality tabs, sidebar filters
- [ ] Production Streamlit: `@st.cache_data`, auto-bootstrap data on Cloud, empty states, error boundaries
- [ ] Export: filtered CSV download + board summary markdown download
- Verify: smoke test `python -c "import app"` + manual filter check

### 4. Deploy readiness
- [ ] `requirements.txt` pinned, `.streamlit/config.toml`, `.gitignore`, `README.md` with Cloud steps
- [ ] `docs/kpi_dictionary.md`, `docs/data_contract.md`
- Verify: fresh `pip install -r requirements.txt` + `python -m src.etl` + `pytest` pass

## Lessons captured in tasks/lessons.md
