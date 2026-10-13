# RevOps360 · Revenue Intelligence & Forecasting Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://revops360.streamlit.app/)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-3776AB?logo=python&logoColor=white)
![Data Contracts](https://img.shields.io/badge/Validation-Pydantic%20v2-E92063?logo=pydantic&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-0E7C7B)

> 🚀 **Live Production Dashboard:** [https://revops360.streamlit.app/](https://revops360.streamlit.app/)

**RevOps360** is a production-grade sales pipeline analytics, forecasting, and data governance platform built with Python, Pydantic, Plotly, and Streamlit. It delivers deterministic CRM data modeling, contract-enforced ETL pipelines, dual-model ensemble forecasting, and an executive-ready enterprise dashboard.

---

## Key Capabilities

- **Contract-Enforced ETL Pipeline:** Pydantic validation gate rejects malformed CRM records into quarantine (`data/processed/_quarantine/`) without data loss. SHA-256 input checksums guarantee idempotent runs with zero-cost re-execution skips.
- **Dual-Model Ensemble Forecasting:** Blends probability-weighted open pipeline deals (stage-specific data contract weights) with statistical time-series trend extrapolation.
- **Walk-Forward Forecast Backtesting:** Evaluates predictive accuracy with historical Mean Absolute Percentage Error (MAPE) and signed forecast bias metrics.
- **Automated Guardrail Alerts:** Proactively detects pipeline under-coverage against the boardroom 3.0× benchmark (computing exact multiplier deficits, required pipeline, and quota shortfalls) and flags cycle skew bottlenecks across operating segments.
- **Enterprise Design System:** Built with a permanent clean light theme, curated financial color tokens (Teal `#0E7C7B`, Deep Navy `#0F1E3D`, Indigo `#4F46E5`), zero decorative emojis/raw glyphs, hoverable metric tooltips, and high-contrast notification banners.
- **One-Click Boardroom Exports:** Exports filtered opportunity microdata as CSV and auto-generates boardroom-ready executive summaries in Markdown.

---

## Dashboard Architecture & Modules

The platform is organized into 5 executive tabs powered by a global 3-way filter command bar (**Region Scope**, **Segment Scope**, **Sales Manager**):

| Tab | Focus Area | Key Metrics & Visualizations |
|---|---|---|
| **1. Overview** | Executive Boardroom Brief | Win rate, average won deal size, won revenue, weighted pipeline, revenue velocity vs. monthly quota targets, and regional pipeline coverage charts. |
| **2. Pipeline** | Deal Velocity & Funnel Health | Stage funnel breakdown, lead source conversion matrix, open pipeline aging distribution histogram, and bottleneck diagnosis notification banners. |
| **3. Forecast** | Predictive Revenue & Scenario Modeling | Dual-model ensemble forecasts, scenario sensitivity stress-testing (Bull/Base/Bear), walk-forward backtest MAPE & bias table, automated 3.0× coverage alerts, and CSV/Markdown export suite. |
| **4. Teams** | Territory & Rep Benchmarking | Sales agent leaderboard, regional revenue mix donut chart, and Skill vs. Scale diagnostic scatter matrix (win rate vs. average deal size). |
| **5. Data Quality** | Governance & Audit Telemetry | ETL execution audit telemetry table with zebra-striping, quarantine contract monitoring, and transparent stage win probability assumptions. |

---

## Quickstart (Local Development)

### Prerequisites
- Python 3.10+ (tested up to Python 3.14)
- Git

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/harshshinde12/revops360.git
cd revops360

python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Seed Data & Run ETL

```bash
# Generate deterministic raw CRM seed data (SEED=42)
python -m src.seed_generator

# Run data contract validation and build dimensional marts
python -m src.etl
```

> **Note on Idempotency:** Rerunning the ETL script with unchanged input datasets automatically prints `status: skipped` and preserves byte-identical parquet and CSV marts without redundant compute.

### 4. Run the Test Suite

```bash
pytest -q
```
All 7 unit tests validate ETL contract idempotency, revenue reconciliation invariants, and analytics logic.

### 5. Launch the Streamlit Dashboard

```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Deployment to Streamlit Cloud

RevOps360 is deployed live on **Streamlit Community Cloud** at:  
👉 **[https://revops360.streamlit.app/](https://revops360.streamlit.app/)**

To deploy your own fork or instance with zero configuration:

1. **Push to GitHub:** Ensure your latest commits are pushed to your remote repository:
   ```bash
   git add .
   git commit -m "Elevate enterprise UI and finalize RevOps360 platform"
   git push origin main
   ```
   *(Note: The `data/` directory is gitignored; the application automatically bootstraps raw data generation and ETL on first boot).*
2. **Connect to Streamlit Cloud:**
   - Navigate to [share.streamlit.io](https://share.streamlit.io/) and click **New app**.
   - Select repository: `harshshinde12/revops360`.
   - Branch: `main`.
   - Main file path: `app.py`.
3. **Advanced Settings:**
   - Python Version: `3.11` or `3.12`.
   - No external secrets or environment variables required.
4. **Deploy:** Click **Deploy**. The initial startup runs the bootstrap process (~20–30s), after which all marts and sessions are cached.

---

## Project Structure

```
revops360/
├── config/
│   └── config.yaml             # Single source of truth for business parameters (targets, stage weights, scenarios)
├── data/                       # Local data storage (gitignored; generated automatically)
│   ├── raw/                    # Raw CRM seed tables (sales_pipeline, sales_teams, accounts, products)
│   └── processed/
│       ├── _audit/             # Execution telemetry logs (etl_runs.csv)
│       ├── _quarantine/        # Contract schema quarantine tables
│       ├── marts/              # Star-schema analytical marts (fact_opportunity, agg_monthly, dim_rep)
│       └── manifest.json       # SHA-256 dataset hash manifest
├── docs/
│   ├── data_contract.md        # CRM data contract specifications & enum schemas
│   └── kpi_dictionary.md       # Definitive RevOps KPI definitions, formulas, and grains
├── src/
│   ├── charts.py               # Standardized Plotly financial visualization tokens & layouts
│   ├── etl.py                  # Contract validation, staging, star-schema creation & audit logging
│   ├── export.py               # Boardroom executive markdown summary generator
│   ├── forecast.py             # Dual-model ensemble engine, scenario modeling & alert logic
│   ├── metrics.py              # Pure analytic functions: KPIs, funnel conversions, bottlenecks
│   ├── schemas.py              # Pydantic schema contracts for incoming records
│   ├── seed_generator.py       # Deterministic CRM seed generator (SEED=42)
│   └── ui.py                   # Executive design system tokens, KPI cards, banners & telemetry tables
├── tests/
│   ├── test_analytics.py       # Analytic metric and invariant test suite
│   └── test_etl.py             # ETL validation gate and idempotency test suite
├── app.py                      # Main executive Streamlit application
├── requirements.txt            # Production dependencies
└── README.md                   # Project documentation & deployment guide
```

---

## Data Governance & Contract Specifications

- **Documentation:** Review [docs/data_contract.md](docs/data_contract.md) for full field definitions, valid enum ranges, and quarantine policies.
- **Metric Definitions:** Review [docs/kpi_dictionary.md](docs/kpi_dictionary.md) for exact mathematical formulas for win rates, deal cycles, pipeline coverage, and forecast variance.

---

## License

This project is licensed under the Apache 2.0 License.
