"""ETL + idempotency tests. Run with: pytest -q"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from src import MARTS
from src.etl import run_etl


def _hash_marts() -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(MARTS.glob("*.csv"))}


def test_etl_success_and_required_marts():
    out = run_etl()
    assert out["status"] in ("success", "skipped")
    for f in ("fact_opportunity.csv", "dim_rep.csv", "dim_account.csv",
              "dim_product.csv", "agg_monthly.csv"):
        assert (MARTS / f).exists(), f"missing mart {f}"


def test_etl_idempotent_byte_identical():
    run_etl()
    before = _hash_marts()
    out = run_etl()
    after = _hash_marts()
    assert before == after
    assert out["status"] == "skipped"


def test_fact_has_no_null_keys():
    fact = pd.read_csv(MARTS / "fact_opportunity.csv")
    assert len(fact) > 0
    assert fact["opportunity_id"].is_unique
    assert fact[["opportunity_id", "sales_agent", "region",
                 "deal_stage", "close_value"]].notna().all().all()
