"""Production ETL: raw (immutable) -> staging (typed) -> marts (star schema).

Industry practices implemented (rarely seen in student projects):
1. Medallion layers — raw never mutated; staging is validated+typed; marts are analytics-ready.
2. Data contracts (Pydantic) gate every row before logic; failures -> quarantine with reason.
3. Quarantine pattern — bad rows preserved, quarantine rate gated (fail loudly).
4. Content-hash idempotency — reruns with identical inputs produce byte-identical outputs;
   matching manifest short-circuits the run (still audit-logged as `skipped`).
5. Audit log — every run appended to `_audit/etl_runs.csv` (run_id, counts, duration).
6. Config-driven business logic — stage probabilities come from config.yaml, never code.
7. Stable surrogate keys (sha1 of natural key, SCD Type 1) for dims.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

import pandas as pd

from src import AUDIT, DATA_PROCESSED, DATA_RAW, DATA_STAGING, MARTS, QUARANTINE, ensure_dirs, load_config
from src.schemas import AccountRow, PipelineRow, ProductRow, TeamRow

log = logging.getLogger(__name__)

MANIFEST = DATA_PROCESSED / "manifest.json"
AUDIT_LOG = AUDIT / "etl_runs.csv"

RAW_FILES = ["sales_pipeline.csv", "sales_teams.csv", "accounts.csv", "products.csv"]


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _parse_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "y", "t"):
        return True
    if s in ("false", "0", "no", "n", "f"):
        return False
    raise ValueError(f"Cannot parse bool from {v!r}")


def _validate_frame(df: pd.DataFrame, model: Any, table: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate every row; return (clean, quarantine_with_reason)."""
    clean_rows: list[dict] = []
    quar_rows: list[dict] = []
    records = df.to_dict(orient="records")
    # Normalize bools for pipeline table before validation
    for rec in records:
        row = dict(rec)
        if table == "sales_pipeline":
            for k in ("is_closed", "is_won"):
                if k in row:
                    try:
                        row[k] = _parse_bool(row[k])
                    except ValueError as e:
                        quar_rows.append({**rec, "_quarantine_reason": str(e)})
                        row = {}
                        break
            if not row:
                continue
        try:
            obj = model.model_validate(row)
            clean_rows.append(obj.model_dump(mode="json"))
        except Exception as e:  # keep first error only — enough to triage
            quar_rows.append({**rec, "_quarantine_reason": str(e).splitlines()[0][:300]})
    clean = pd.DataFrame(clean_rows)
    quar = pd.DataFrame(quar_rows)
    return clean, quar


def _surrogate(series: pd.Series, salt: str = "revops360") -> pd.Series:
    return series.astype(str).map(
        lambda v: hashlib.sha1(f"{salt}|{v}".encode()).hexdigest()[:12]
    )


def run_etl(raw_dir: Path = DATA_RAW) -> dict[str, Any]:
    t0 = time.time()
    ensure_dirs()
    cfg = load_config()
    run_id = uuid.uuid4().hex[:8]

    # 0. Raw presence — auto-seed for fresh clones / Streamlit Cloud
    missing = [f for f in RAW_FILES if not (raw_dir / f).exists()]
    if missing:
        log.info("Raw files missing %s — generating deterministic seed data", missing)
        from src.seed_generator import generate_all
        generate_all(raw_dir)

    input_hashes = {f: _sha256(raw_dir / f) for f in RAW_FILES}

    # 1. Idempotency short-circuit
    if MANIFEST.exists():
        try:
            prev = json.loads(MANIFEST.read_text(encoding="utf-8"))
            if prev.get("inputs") == input_hashes and prev.get("config_version") == str(
                cfg["generator"]["version"]
            ):
                _audit(run_id, "skipped", 0, 0, 0.0, time.time() - t0, "inputs unchanged")
                log.info("ETL skipped (run %s): inputs unchanged", run_id)
                return {"status": "skipped", "run_id": run_id}
        except Exception as e:
            log.warning("Could not read manifest, rebuilding: %s", e)

    # 2. Extract
    raw = {f: pd.read_csv(raw_dir / f) for f in RAW_FILES}
    n_in = int(sum(len(v) for v in raw.values()))

    # 3. Validate -> staging + quarantine
    specs = [
        ("sales_pipeline.csv", PipelineRow),
        ("sales_teams.csv", TeamRow),
        ("accounts.csv", AccountRow),
        ("products.csv", ProductRow),
    ]
    staged: dict[str, pd.DataFrame] = {}
    total_quar = 0
    for fname, model in specs:
        clean, quar = _validate_frame(raw[fname], model, fname.replace(".csv", ""))
        clean = clean.sort_values(list(clean.columns)).reset_index(drop=True)
        table = fname.replace(".csv", "")
        staged[table] = clean
        # Deterministic staging write (fixed float format, ISO dates already strings)
        clean.to_csv(DATA_STAGING / fname, index=False)
        if len(quar):
            quar.to_csv(QUARANTINE / f"quarantine_{fname}", index=False)
            total_quar += len(quar)
        else:
            qp = QUARANTINE / f"quarantine_{fname}"
            if qp.exists():
                qp.unlink()
        log.info("%s: %d clean, %d quarantined", table, len(clean), len(quar))

    quar_rate = (total_quar / n_in) if n_in else 0.0
    max_q = float(cfg["quality"]["max_quarantine_rate"])
    if quar_rate > max_q:
        _audit(run_id, "failed", n_in, 0, quar_rate, time.time() - t0,
               f"quarantine {quar_rate:.2%} > {max_q:.2%}")
        raise RuntimeError(
            f"ETL failed loudly: quarantine rate {quar_rate:.2%} exceeds {max_q:.2%}. "
            f"Inspect {QUARANTINE}/ — refusing to corrupt marts."
        )

    # 4. Transform -> marts (star schema)
    pipe = staged["sales_pipeline"].copy()
    teams = staged["sales_teams"].copy()
    accts = staged["accounts"].copy()
    prods = staged["products"].copy()

    pipe["engage_date"] = pd.to_datetime(pipe["engage_date"])
    pipe["close_date"] = pd.to_datetime(pipe["close_date"])
    pipe["cycle_days"] = (pipe["close_date"] - pipe["engage_date"]).dt.days
    pipe["close_month"] = pipe["close_date"].dt.strftime("%Y-%m")
    probs: dict[str, float] = dict(cfg["stage_probability"])
    pipe["stage_prob"] = pipe["deal_stage"].map(probs).fillna(0.0)
    pipe["is_open"] = ~pipe["is_closed"].astype(bool)
    pipe["expected_value"] = (pipe["close_value"] * pipe["stage_prob"]).round(2)

    fact = pipe.merge(teams, on="sales_agent", how="left", validate="many_to_one")
    fact["region"] = fact["regional_office"]
    fact = fact.sort_values("opportunity_id").reset_index(drop=True)
    # Fixed precision for byte-identical reruns
    fact["close_value"] = fact["close_value"].round(2)
    fact["engage_date"] = fact["engage_date"].dt.strftime("%Y-%m-%d")
    fact["close_date"] = fact["close_date"].dt.strftime("%Y-%m-%d")

    dim_rep = (
        teams.assign(rep_key=_surrogate(teams["sales_agent"]))
        .sort_values("sales_agent").reset_index(drop=True)
    )
    dim_account = (
        accts.assign(account_key=_surrogate(accts["account"]))
        .sort_values("account").reset_index(drop=True)
    )
    dim_product = (
        prods.assign(product_key=_surrogate(prods["product"]))
        .sort_values("product").reset_index(drop=True)
    )

    monthly = (
        fact.assign(
            won_value=fact["close_value"].where(fact["is_won"], 0.0),
            won_n=fact["is_won"].astype(int),
            open_expected=fact["expected_value"].where(fact["is_open"], 0.0),
        )
        .groupby(["close_month", "region"], as_index=False)
        .agg(
            won_revenue=("won_value", "sum"),
            deals_won=("won_n", "sum"),
            deals_total=("opportunity_id", "count"),
            open_expected=("open_expected", "sum"),
        )
        .sort_values(["close_month", "region"]).reset_index(drop=True)
    )
    monthly["won_revenue"] = monthly["won_revenue"].round(2)
    monthly["open_expected"] = monthly["open_expected"].round(2)

    outputs = {
        "fact_opportunity.csv": fact,
        "dim_rep.csv": dim_rep,
        "dim_account.csv": dim_account,
        "dim_product.csv": dim_product,
        "agg_monthly.csv": monthly,
    }
    out_hashes: dict[str, dict] = {}
    for fname, df in outputs.items():
        p = MARTS / fname
        df.to_csv(p, index=False)
        out_hashes[fname] = {"sha256": _sha256(p), "rows": int(len(df))}

    manifest = {
        "config_version": str(cfg["generator"]["version"]),
        "inputs": input_hashes,
        "outputs": out_hashes,
        "quarantine_rate": quar_rate,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    dur = time.time() - t0
    _audit(run_id, "success", n_in, int(len(fact)), quar_rate, dur, "")
    log.info("ETL success (run %s): %d -> %d fact rows in %.1fs", run_id, n_in, len(fact), dur)
    return {"status": "success", "run_id": run_id, "fact_rows": int(len(fact)),
            "quarantine_rate": quar_rate}


def _audit(run_id: str, status: str, n_in: int, n_out: int,
           quar_rate: float, dur: float, note: str) -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    row = pd.DataFrame([{
        "run_id": run_id,
        "utc_time": pd.Timestamp.utcnow().isoformat(),
        "status": status,
        "rows_in": n_in,
        "rows_out": n_out,
        "quarantine_rate": round(float(quar_rate), 5),
        "duration_s": round(float(dur), 2),
        "note": note,
    }])
    header = not AUDIT_LOG.exists()
    row.to_csv(AUDIT_LOG, mode="a", header=header, index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    print(run_etl())
