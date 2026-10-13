"""Central paths + config loading. Single import point for all modules."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.yaml"
DATA_RAW = ROOT / "data" / "raw"
DATA_STAGING = ROOT / "data" / "staging"
DATA_PROCESSED = ROOT / "data" / "processed"
MARTS = DATA_PROCESSED / "marts"
QUARANTINE = DATA_PROCESSED / "_quarantine"
AUDIT = DATA_PROCESSED / "_audit"


@lru_cache(maxsize=1)
def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"Invalid config at {path}: expected mapping")
    return cfg


def ensure_dirs() -> None:
    for d in (DATA_RAW, DATA_STAGING, MARTS, QUARANTINE, AUDIT):
        d.mkdir(parents=True, exist_ok=True)
