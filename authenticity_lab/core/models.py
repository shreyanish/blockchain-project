from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class EvidenceFactor:
    name: str
    status: str
    explanation: str
    score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "explanation": self.explanation,
            "score": self.score,
        }


@dataclass(frozen=True)
class LayerResult:
    layer: str
    status: str
    score: float
    summary: str
    factors: tuple[EvidenceFactor, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "status": self.status,
            "score": round(self.score, 4),
            "summary": self.summary,
            "factors": [factor.to_dict() for factor in self.factors],
            "raw": self.raw,
        }


@dataclass(frozen=True)
class ProvenanceRecord:
    media_hash: str
    owner: str
    timestamp: str
    metadata: dict[str, Any]
    transaction_id: str
    block_number: int
    chain_id: str = "local-research-ledger"

    def to_dict(self) -> dict[str, Any]:
        return {
            "media_hash": self.media_hash,
            "owner": self.owner,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "transaction_id": self.transaction_id,
            "block_number": self.block_number,
            "chain_id": self.chain_id,
        }


@dataclass(frozen=True)
class SystemMetrics:
    hash_generation_ms: float
    blockchain_lookup_ms: float
    metadata_analysis_ms: float
    ai_analysis_ms: float
    trust_scoring_ms: float
    total_verification_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "hash_generation_ms": round(self.hash_generation_ms, 3),
            "blockchain_lookup_ms": round(self.blockchain_lookup_ms, 3),
            "metadata_analysis_ms": round(self.metadata_analysis_ms, 3),
            "ai_analysis_ms": round(self.ai_analysis_ms, 3),
            "trust_scoring_ms": round(self.trust_scoring_ms, 3),
            "total_verification_ms": round(self.total_verification_ms, 3),
        }


@dataclass(frozen=True)
class VerificationReport:
    file_name: str
    media_hash: str
    generated_at: str
    blockchain: LayerResult
    reference: LayerResult | None
    metadata: LayerResult
    ai: LayerResult
    trust: LayerResult
    provenance_record: dict[str, Any] | None
    reference_record: dict[str, Any] | None
    system_metrics: SystemMetrics
    pipeline: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_name": self.file_name,
            "media_hash": self.media_hash,
            "generated_at": self.generated_at,
            "blockchain": self.blockchain.to_dict(),
            "reference": self.reference.to_dict() if self.reference else None,
            "metadata": self.metadata.to_dict(),
            "ai": self.ai.to_dict(),
            "trust": self.trust.to_dict(),
            "provenance_record": self.provenance_record,
            "reference_record": self.reference_record,
            "system_metrics": self.system_metrics.to_dict(),
            "pipeline": list(self.pipeline),
        }
