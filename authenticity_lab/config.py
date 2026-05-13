from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    ai_analyzer: str = "heuristic"
    ledger_path: str = "data/provenance_records.json"


def load_config() -> AppConfig:
    return AppConfig(
        ai_analyzer=os.getenv("AI_ANALYZER", "heuristic"),
        ledger_path=os.getenv("PROVENANCE_LEDGER_PATH", "data/provenance_records.json"),
    )
