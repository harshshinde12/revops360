# Data Contract — RevOps360

Mirrors Maven/Kaggle `CRM Sales Opportunities` (Public Domain) extended for forecasting.
Any CRM export with these columns is accepted by `src/etl.py` — no code change needed.

## `sales_pipeline.csv`
`opportunity_id` (unique, e.g. OPP-00001), `sales_agent` (FK -> sales_teams),
`product` (FK -> products), `account` (FK -> accounts),
`segment` in {SMB, Mid-Market, Enterprise}, `lead_source` in
{Referral, Partner, Outbound, Inbound, Event, Paid Ads, Website, Renewal},
`deal_stage` in {Prospecting, Qualification, Proposal, Negotiation, Commit, Closed Won, Closed Lost},
`engage_date`, `close_date` (ISO YYYY-MM-DD, close >= engage),
`close_value` in [100, 500000], `is_closed` bool, `is_won` bool (won => closed, closed+won => stage Closed Won).

## `sales_teams.csv`
`sales_agent` (unique), `manager`, `regional_office` in {West, East, Central, South}.

## `accounts.csv`
`account` (unique), `sector`, `year_established` 1900..2025, `employees` >= 1,
`annual_revenue` >= 0, `office_location`.

## `products.csv`
`product` (unique), `series`, `list_price` >= 0.

## Rules
- Unknown enum / bad date / out-of-range value -> row quarantined to
  `data/processed/_quarantine/quarantine_<table>.csv` with `_quarantine_reason`, never dropped silently.
- Quarantine rate above `quality.max_quarantine_rate` (2%) fails the run loudly.
- Seed data (`src/seed_generator.py`, SEED=42, version in config) embeds documented patterns:
  August dip, Q-end pushes, SMB 34% > Mid 28% > Enterprise 16% win hierarchy,
  Referral 1.5x / Paid Ads 0.75x source lifts, rep skill lognormal, EoQ discounting.
