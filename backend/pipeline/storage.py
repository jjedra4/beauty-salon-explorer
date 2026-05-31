"""Filesystem persistence for pipeline artifacts.

Raw collected records live under ``data/raw/`` (git-ignored, large and
regenerable); the curated, AI-enriched output lives under ``data/seed/`` and is
committed so the app runs without re-collecting. This module centralises those
paths and the JSON (de)serialization of :class:`RawSalon` records.
"""

import json
from pathlib import Path

from pipeline.collectors.base import RawSalon
from pipeline.enrichment.models import EnrichedSalon

# backend/data/{raw,seed}
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
SEED_DIR = DATA_DIR / "seed"

RAW_SALONS_PATH = RAW_DIR / "salons.json"
SEED_SALONS_PATH = SEED_DIR / "salons.json"


def write_raw_salons(records: list[RawSalon], path: Path = RAW_SALONS_PATH) -> int:
    """Write raw salon records to ``path`` as a JSON array.

    Returns the number of records written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [record.model_dump(mode="json") for record in records]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(payload)


def read_raw_salons(path: Path = RAW_SALONS_PATH) -> list[RawSalon]:
    """Read raw salon records previously written by :func:`write_raw_salons`."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [RawSalon.model_validate(item) for item in raw]


def write_enriched_salons(records: list[EnrichedSalon], path: Path = SEED_SALONS_PATH) -> int:
    """Write the enriched seed dataset to ``path`` as a JSON array.

    Returns the number of records written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [record.model_dump(mode="json") for record in records]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(payload)


def read_enriched_salons(path: Path = SEED_SALONS_PATH) -> list[EnrichedSalon]:
    """Read the enriched seed dataset (committed application data)."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [EnrichedSalon.model_validate(item) for item in raw]
