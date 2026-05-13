from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    ai_analyzer: str = "heuristic"
    ledger_path: str = "data/provenance_records.json"
    provenance_gateway: str = "local"
    ganache_rpc_url: str = "http://127.0.0.1:7545"
    ganache_contract_address: str = ""
    ganache_contract_abi_path: str = "artifacts/contracts/MediaProvenance.sol/MediaProvenance.json"
    ganache_account: str = ""


def load_config() -> AppConfig:
    return AppConfig(
        ai_analyzer=os.getenv("AI_ANALYZER", "heuristic"),
        ledger_path=os.getenv("PROVENANCE_LEDGER_PATH", "data/provenance_records.json"),
        provenance_gateway=os.getenv("PROVENANCE_GATEWAY", "local"),
        ganache_rpc_url=os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:7545"),
        ganache_contract_address=os.getenv("GANACHE_CONTRACT_ADDRESS", ""),
        ganache_contract_abi_path=os.getenv(
            "GANACHE_CONTRACT_ABI_PATH",
            "artifacts/contracts/MediaProvenance.sol/MediaProvenance.json",
        ),
        ganache_account=os.getenv("GANACHE_ACCOUNT", ""),
    )
