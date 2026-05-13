from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Protocol

from authenticity_lab.core.models import EvidenceFactor, LayerResult, ProvenanceRecord, utc_now_iso


class ProvenanceGateway(Protocol):
    def register(self, media_hash: str, owner: str, metadata: dict) -> ProvenanceRecord:
        ...

    def lookup(self, media_hash: str) -> ProvenanceRecord | None:
        ...

    def list_records(self) -> list[ProvenanceRecord]:
        ...


class LocalResearchLedger:
    """Small append-only JSON ledger for demos and tests.

    This is intentionally transparent and inspectable. It simulates the shape of
    blockchain provenance records when Ganache is unavailable, but it does not
    claim immutability or production security.
    """

    def __init__(self, path: str | Path = "data/provenance_records.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register(self, media_hash: str, owner: str, metadata: dict) -> ProvenanceRecord:
        records = self.list_records()
        existing = next((record for record in records if record.media_hash == media_hash), None)
        if existing:
            if "media_profile" not in existing.metadata and "media_profile" in metadata:
                upgraded = ProvenanceRecord(
                    media_hash=existing.media_hash,
                    owner=existing.owner,
                    timestamp=existing.timestamp,
                    metadata={**existing.metadata, "media_profile": metadata["media_profile"]},
                    transaction_id=existing.transaction_id,
                    block_number=existing.block_number,
                    chain_id=existing.chain_id,
                )
                records = [upgraded if record.media_hash == media_hash else record for record in records]
                self._write(records)
                return upgraded
            return existing

        block_number = len(records) + 1
        transaction_id = f"local-{block_number:06d}-{secrets.token_hex(8)}"
        record = ProvenanceRecord(
            media_hash=media_hash,
            owner=owner,
            timestamp=utc_now_iso(),
            metadata=metadata,
            transaction_id=transaction_id,
            block_number=block_number,
        )
        records.append(record)
        self._write(records)
        return record

    def lookup(self, media_hash: str) -> ProvenanceRecord | None:
        return next((record for record in self.list_records() if record.media_hash == media_hash), None)

    def list_records(self) -> list[ProvenanceRecord]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return [ProvenanceRecord(**item) for item in payload.get("records", [])]

    def _write(self, records: list[ProvenanceRecord]) -> None:
        payload = {"records": [record.to_dict() for record in records]}
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)


class ProvenanceService:
    def __init__(self, gateway: ProvenanceGateway) -> None:
        self.gateway = gateway

    def register(self, media_hash: str, owner: str, metadata: dict) -> ProvenanceRecord:
        return self.gateway.register(media_hash=media_hash, owner=owner, metadata=metadata)

    def verify(self, media_hash: str) -> tuple[LayerResult, ProvenanceRecord | None]:
        record = self.gateway.lookup(media_hash)
        if record is None:
            return (
                LayerResult(
                    layer="Blockchain Provenance",
                    status="UNREGISTERED",
                    score=0.0,
                    summary="No provenance record matched the media hash.",
                    factors=(
                        EvidenceFactor(
                            name="Hash lookup",
                            status="MISS",
                            explanation="The SHA-256 digest was not found in the configured provenance ledger.",
                            score=0.0,
                        ),
                    ),
                ),
                None,
            )

        return (
            LayerResult(
                layer="Blockchain Provenance",
                status="VERIFIED",
                score=1.0,
                summary="The media hash matches a registered provenance record.",
                factors=(
                    EvidenceFactor(
                        name="Hash lookup",
                        status="MATCH",
                        explanation="The SHA-256 digest matched a stored provenance record.",
                        score=1.0,
                    ),
                    EvidenceFactor(
                        name="Stored payload",
                        status="HASH_ONLY",
                        explanation="Only hash and provenance metadata are stored; media bytes are not stored on-chain.",
                    ),
                ),
                raw=record.to_dict(),
            ),
            record,
        )

    def lookup(self, media_hash: str) -> ProvenanceRecord | None:
        return self.gateway.lookup(media_hash)

    def list_records(self) -> list[ProvenanceRecord]:
        return self.gateway.list_records()
