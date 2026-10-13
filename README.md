# RevOps360

Sales pipeline analytics and revenue forecasting dashboard built with Python and Streamlit.

Live app: https://revops360.streamlit.app/

---

## Overview

RevOps360 is a revenue operations dashboard designed to analyze B2B sales pipelines, evaluate sales team performance, and generate revenue forecasts. It processes CRM opportunity records through a contract-enforced ETL pipeline and surfaces key revenue metrics in an interactive web interface.

The project handles the end-to-end analytics workflow:
1. Validating raw CRM exports against explicit data contracts using Pydantic.
2. Generating star-schema analytical marts (`fact_opportunity`, `dim_rep`, `agg_monthly`) with idempotent, content-hashed caching.
3. Forecasting forward revenue by combining stage-weighted open deals with historical trend extrapolation.
4. Evaluating forecast accuracy through walk-forward backtesting (MAPE and model bias).
5. Surfacing operational risks such as segment cycle skew and pipeline coverage deficits against targets.

---

## Dashboard Sections

The dashboard includes global filter controls (Region, Segment, Sales Manager) and is organized across five views:

- **Overview:** High-level executive brief covering win rates, median deal size, booked revenue, monthly quota attainment, and regional pipeline coverage.
- **Pipeline:** Funnel stage distribution, lead source conversion breakdown, open deal aging histograms, and bottleneck alerts.
- **Forecast:** Blended revenue projections (weighted pipeline + trend model), scenario ranges (Base, Bull, Bear), backtest metrics, automated coverage shortfall alerts against a 3.0x benchmark, and CSV/Markdown data exports.
- **Teams:** Sales representative leaderboard, regional revenue contribution, and a scatter analysis of win rate versus average deal size.
- **Data Quality:** ETL run history and duration telemetry, quarantine contract monitoring, and stage win probability configurations.

---

## Forecasting Methodology

The forecast engine uses a dual-model ensemble approach:

- **Stage-Weighted Pipeline:** Prices open opportunities using win probabilities defined per stage in `config/config.yaml`.
- **Trend Extrapolation:** Fits historical monthly revenue trends to project future performance.
- **Blended Ensemble:** Combines probability weighting (60%) and trend projection (40%) to balance open pipeline reality with historical momentum.
- **Walk-Forward Backtesting:** Trains models incrementally on past months to predict subsequent actuals, reporting Mean Absolute Percentage Error (MAPE) and signed forecast bias.
- **Coverage Guardrails:** Evaluates active weighted pipeline against regional monthly targets, computing exact coverage ratios and deficit gaps against a 3.0x coverage benchmark.

---

## Running Locally

### Requirements
- Python 3.10+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/harshshinde12/revops360.git
cd revops360

# Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Data Generation and ETL

```bash
# Generate deterministic raw CRM data (SEED=42)
python -m src.seed_generator

# Run data contract validation and build analytical marts
python -m src.etl
```

If you re-run the ETL script without modifying the inputs, it checks SHA-256 hashes in `manifest.json` and skips execution automatically.

### Running Tests

```bash
pytest -q
```

Validates ETL validation gates, idempotency guarantees, and analytics formulas.

### Launching the Dashboard

```bash
streamlit run app.py
```

The app will be available locally at `http://localhost:8501`.

---

## Deployment to Streamlit Cloud

The application is deployed on Streamlit Community Cloud:  
https://revops360.streamlit.app/

To deploy your own instance:
1. Fork or push this repository to your GitHub account.
2. Sign in to https://share.streamlit.io.
3. Select this repository, set the branch to `main`, and set the entry file to `app.py`.
4. Deploy. On first launch, the app automatically bootstraps seed data generation and builds the marts in memory cache (takes about 20-30 seconds on initial boot).

---

## Project Structure

```
revops360/
├── config/
│   └── config.yaml             # Stage probabilities, monthly targets, and alert thresholds
├── data/                       # Local data directory (auto-generated, gitignored)
│   ├── raw/                    # Raw CRM files (pipeline, teams, accounts, products)
│   └── processed/
│       ├── _audit/             # ETL execution logs (etl_runs.csv)
│       ├── _quarantine/        # Rows rejected by data contract checks
│       ├── marts/              # Analytical CSV/parquet marts
│       └── manifest.json       # Input file checksums for idempotent ETL
├── docs/
│   ├── data_contract.md        # CRM schema contracts and validation rules
│   └── kpi_dictionary.md       # Metric definitions and calculation grains
├── src/
│   ├── charts.py               # Shared Plotly theme and formatting helpers
│   ├── etl.py                  # Ingestion, validation, mart transformations, and logging
│   ├── export.py               # Markdown summary generator for boardroom reports
│   ├── forecast.py             # Ensemble forecasting, backtesting, and coverage alerts
│   ├── metrics.py              # Pure metric calculation functions
│   ├── schemas.py              # Pydantic models for CRM record validation
│   ├── seed_generator.py       # Deterministic CRM seed generator (SEED=42)
│   └── ui.py                   # UI styling, KPI card components, and notification banners
├── tests/
│   ├── test_analytics.py       # Unit tests for KPIs, coverage, and forecast math
│   └── test_etl.py             # Unit tests for data contracts and ETL idempotency
├── app.py                      # Main Streamlit application
├── requirements.txt            # Application dependencies
└── README.md                   # Project documentation
```

---

## Documentation

- [KPI Dictionary](docs/kpi_dictionary.md): Formulas and grains for win rates, cycles, pipeline coverage, and forecast variance.
- [Data Contract](docs/data_contract.md): Field specifications, accepted values, and quarantine rules.

---

## License

Apache 2.0
