"""Deterministic CRM seed generator (versioned, reproducible).

Why synthetic instead of a Kaggle download?
- The closest real dataset (Maven/Kaggle `CRM Sales Opportunities`, Public Domain)
  sits behind a login wall, so it cannot be a hard runtime dependency —
  Streamlit Cloud would fail on fresh clone.
- This generator mirrors that schema exactly (sales_pipeline, sales_teams,
  accounts, products) and extends it with `segment` + `lead_source` + a full
  7-stage funnel, with documented embedded patterns (seasonality, segment win
  hierarchy, rep skill heterogeneity, source effects, EoQ discounting).
- Output is deterministic (fixed seed) and content-hashed, so reruns are
  byte-identical — an industry requirement for reproducible pipelines.

Real CRM drop-in: export your CRM to the same columns
(see docs/data_contract.md) and place files in data/raw/ — ETL accepts them as-is.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src import DATA_RAW, ensure_dirs, load_config

log = logging.getLogger(__name__)

FIRST = [
    "Aarav", "Maya", "Rohan", "Priya", "Arjun", "Neha", "Karan", "Divya",
    "Aditya", "Ishita", "Vikram", "Ananya", "Sahil", "Riya", "Manav", "Sara",
]
LAST = [
    "Sharma", "Patel", "Mehta", "Iyer", "Gupta", "Reddy", "Nair", "Khan",
    "Joshi", "Das", "Kulkarni", "Menon", "Bose", "Chopra", "Rao", "Verma",
]
MANAGERS = ["Anita Desai", "Rahul Verma", "Kavita Rao", "Suresh Menon"]
REGIONS = ["West", "East", "Central", "South"]
PRODUCTS = [
    ("GTX Pro Server", "GTX", 25000.0),
    ("GTX Edge Node", "GTX", 12000.0),
    ("Nexus Storage Array", "Nexus", 18000.0),
    ("Nexus Backup Unit", "Nexus", 8000.0),
    ("Vertex Workstation", "Vertex", 5500.0),
    ("Vertex Thin Client", "Vertex", 2200.0),
]
SECTORS = ["Technology", "Finance", "Healthcare", "Manufacturing", "Retail", "Education"]
SOURCES = ["Referral", "Partner", "Outbound", "Inbound", "Event", "Paid Ads", "Website", "Renewal"]
SOURCE_W = np.array([0.10, 0.12, 0.18, 0.15, 0.10, 0.12, 0.13, 0.10])
SOURCE_LIFT = {
    "Referral": 1.5, "Partner": 1.25, "Renewal": 1.3, "Event": 1.1,
    "Inbound": 1.0, "Website": 0.95, "Outbound": 0.85, "Paid Ads": 0.75,
}
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
SEG_W = np.array([0.50, 0.35, 0.15])
SEG_BASE_WIN = {"SMB": 0.34, "Mid-Market": 0.28, "Enterprise": 0.16}
SEG_VALUE = {"SMB": (2500, 9000), "Mid-Market": (9000, 35000), "Enterprise": (35000, 120000)}
SEG_CYCLE = {"SMB": 28, "Mid-Market": 52, "Enterprise": 95}


def _rng(seed: int) -> np.random.RandomState:
    return np.random.RandomState(seed)


def _seasonal_month_weights(rng: np.random.RandomState) -> np.ndarray:
    # August dip (~40% below avg), Dec slowdown, Q-end pushes. Documented in data_contract.
    w = np.ones(12)
    w[7] = 0.6   # August
    w[11] = 0.8  # December
    w[2] = 1.25; w[5] = 1.25; w[8] = 1.25  # Mar/Jun/Sep pushes
    return w / w.sum()


def generate_all(raw_dir: Path = DATA_RAW) -> dict[str, Path]:
    ensure_dirs()
    cfg = load_config()
    seed: int = int(cfg["generator"]["seed"])
    version: str = str(cfg["generator"]["version"])
    start = date.fromisoformat(str(cfg["generator"]["start_date"]))
    end = date.fromisoformat(str(cfg["generator"]["end_date"]))
    n_opp: int = int(cfg["generator"]["n_opportunities"])
    n_acc: int = int(cfg["generator"]["n_accounts"])
    rng = _rng(seed)

    # --- reps / teams ---
    reps: list[dict] = []
    rep_names: list[str] = []
    for i in range(int(cfg["generator"]["n_reps"])):
        name = f"{FIRST[i % len(FIRST)]} {LAST[(i * 5 + 3) % len(LAST)]}"
        rep_names.append(name)
        reps.append({
            "sales_agent": name,
            "manager": MANAGERS[i // 4],
            "regional_office": REGIONS[i // 4],
            "skill": float(np.clip(rng.lognormal(mean=0.0, sigma=0.35), 0.5, 2.0)),
            "quota": 380000 + int(rng.normal(0, 40000)),
        })
    teams_df = pd.DataFrame(
        [{"sales_agent": r["sales_agent"], "manager": r["manager"],
          "regional_office": r["regional_office"]} for r in reps]
    ).sort_values("sales_agent").reset_index(drop=True)

    # --- products / accounts ---
    products_df = pd.DataFrame(
        [{"product": p, "series": s, "list_price": pr} for p, s, pr in PRODUCTS]
    ).sort_values("product").reset_index(drop=True)

    accounts: list[dict] = []
    for i in range(n_acc):
        accounts.append({
            "account": f"Acct-{i + 1:04d} {'Systems' if i % 3 == 0 else 'Labs' if i % 3 == 1 else 'Works'}",
            "sector": str(rng.choice(SECTORS)),
            "year_established": int(rng.randint(1979, 2018)),
            "employees": int(np.clip(int(rng.lognormal(4.2, 1.0)), 5, 8000)),
            "annual_revenue": round(float(rng.lognormal(14.5, 1.1)), 2),
            "office_location": str(rng.choice(REGIONS)),
        })
    accounts_df = pd.DataFrame(accounts).sort_values("account").reset_index(drop=True)

    # --- opportunities ---
    month_w = _seasonal_month_weights(rng)
    total_days = (end - start).days
    day_grid = [start + timedelta(days=d) for d in range(total_days + 1)]
    day_w = np.array([month_w[d.month - 1] for d in day_grid])
    day_w = day_w / day_w.sum()

    prod_names = products_df["product"].tolist()
    acct_names = accounts_df["account"].tolist()
    rows: list[dict] = []
    for i in range(n_opp):
        rep = reps[int(rng.randint(0, len(reps)))]
        segment = str(rng.choice(SEGMENTS, p=SEG_W))
        source = str(rng.choice(SOURCES, p=SOURCE_W / SOURCE_W.sum()))
        engage = day_grid[int(rng.choice(len(day_grid), p=day_w))]
        # Win probability with embedded lifts (skill x source x segment base)
        p_win = SEG_BASE_WIN[segment] * SOURCE_LIFT[source] * rep["skill"]
        p_win = float(np.clip(p_win, 0.03, 0.85))
        is_won = bool(rng.rand() < p_win)
        # Open pipeline: recent engages stay open (so forecast has something to score)
        cutoff = end - timedelta(days=75)
        if engage >= cutoff and rng.rand() < 0.55:
            is_closed = False
            is_won = False
        else:
            is_closed = True
        lo, hi = SEG_VALUE[segment]
        value = float(np.clip(rng.lognormal(np.log((lo + hi) / 2), 0.55), lo, hi))
        # End-of-quarter discount concentration (documented pattern)
        eoq = engage.month in (3, 6, 9, 12) and engage.day >= 17
        if eoq and rng.rand() < 0.55:
            value *= float(rng.uniform(0.82, 0.95))
        value = round(value, 2)
        cycle = int(np.clip(rng.lognormal(np.log(SEG_CYCLE[segment]), 0.5), 5, 240))
        close = engage + timedelta(days=cycle)
        if close > end + timedelta(days=120):
            close = end + timedelta(days=int(rng.randint(1, 90)))
        # Contract guarantee: engage <= close always; closed deals close within window.
        if close < engage:
            close = engage + timedelta(days=int(rng.randint(5, 30)))
        if is_closed and close > end:
            close = end
            if close < engage:
                engage = close - timedelta(days=int(rng.randint(5, 30)))

        if is_closed:
            stage = "Closed Won" if is_won else "Closed Lost"
        else:
            stage = str(rng.choice(
                ["Prospecting", "Qualification", "Proposal", "Negotiation", "Commit"],
                p=[0.22, 0.26, 0.24, 0.16, 0.12],
            ))
        rows.append({
            "opportunity_id": f"OPP-{i + 1:05d}",
            "sales_agent": rep["sales_agent"],
            "product": str(rng.choice(prod_names)),
            "account": str(rng.choice(acct_names)),
            "segment": segment,
            "lead_source": source,
            "deal_stage": stage,
            "engage_date": engage.isoformat(),
            "close_date": close.isoformat(),
            "close_value": value,
            "is_closed": is_closed,
            "is_won": is_won,
        })

    pipe_df = pd.DataFrame(rows).sort_values("opportunity_id").reset_index(drop=True)

    raw_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "sales_pipeline.csv": pipe_df,
        "sales_teams.csv": teams_df,
        "accounts.csv": accounts_df,
        "products.csv": products_df,
    }
    written: dict[str, Path] = {}
    manifest_files: dict[str, dict] = {}
    for fname, df in out.items():
        p = raw_dir / fname
        df.to_csv(p, index=False)
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest_files[fname] = {"sha256": h, "rows": int(len(df))}
        written[fname] = p
    manifest = {
        "generator": "seed_generator",
        "version": version,
        "seed": seed,
        "created_utc": pd.Timestamp.utcnow().isoformat(),
        "files": manifest_files,
    }
    with open(raw_dir / "seed_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    log.info("Seed data written to %s (%d opportunities)", raw_dir, len(pipe_df))
    return written


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_all()
