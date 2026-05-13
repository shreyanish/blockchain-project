from __future__ import annotations

from time import perf_counter

from authenticity_lab.core.ai import AuthenticityAnalyzer, build_authenticity_analyzer
from authenticity_lab.core.hashing import sha256_bytes
from authenticity_lab.core.metadata import MetadataAnalyzer
from authenticity_lab.core.models import (
    EvidenceFactor,
    LayerResult,
    ProvenanceRecord,
    SystemMetrics,
    VerificationReport,
    utc_now_iso,
)
from authenticity_lab.core.provenance import ProvenanceService
from authenticity_lab.core.trust import TrustScoreEngine


class VerificationPipeline:
    stages = (
        "SHA-256 Hash Engine",
        "Blockchain Provenance Layer",
        "Metadata Analysis Layer",
        "AI Authenticity Analysis Layer",
        "Trust Score Engine",
        "Verification Report UI",
    )

    def __init__(
        self,
        provenance: ProvenanceService,
        metadata_analyzer: MetadataAnalyzer | None = None,
        ai_analyzer: AuthenticityAnalyzer | None = None,
        trust_engine: TrustScoreEngine | None = None,
    ) -> None:
        self.provenance = provenance
        self.metadata_analyzer = metadata_analyzer or MetadataAnalyzer()
        self.ai_analyzer = ai_analyzer or build_authenticity_analyzer()
        self.trust_engine = trust_engine or TrustScoreEngine()

    def register(self, content: bytes, file_name: str, owner: str = "research-demo") -> ProvenanceRecord:
        started = perf_counter()
        media_hash = sha256_bytes(content)
        hash_finished = perf_counter()
        media_profile = self.metadata_analyzer.inspect_profile(content, file_name)
        metadata = {
            "file_name": file_name,
            "byte_size": len(content),
            "registered_by": owner,
            "storage_policy": "hash-only",
            "media_profile": media_profile,
        }
        record = self.provenance.register(media_hash=media_hash, owner=owner, metadata=metadata)
        transaction_finished = perf_counter()
        registration_metrics = {
            "hash_generation_ms": round((hash_finished - started) * 1000, 3),
            "transaction_confirmation_ms": round((transaction_finished - hash_finished) * 1000, 3),
        }
        if record.metadata.get("registration_metrics") == registration_metrics:
            return record
        return ProvenanceRecord(
            media_hash=record.media_hash,
            owner=record.owner,
            timestamp=record.timestamp,
            metadata={**record.metadata, "registration_metrics": registration_metrics},
            transaction_id=record.transaction_id,
            block_number=record.block_number,
            chain_id=record.chain_id,
        )

    def verify(self, content: bytes, file_name: str, reference_hash: str | None = None) -> VerificationReport:
        verification_started = perf_counter()
        media_hash = sha256_bytes(content)
        hash_finished = perf_counter()
        blockchain_result, provenance_record = self.provenance.verify(media_hash)
        blockchain_finished = perf_counter()
        reference_record = self.provenance.lookup(reference_hash) if reference_hash else None
        reference_result = self._compare_reference(media_hash, reference_hash, reference_record)
        reference_profile = self._select_reference_profile(provenance_record, reference_record)
        metadata_result = self.metadata_analyzer.analyze(content, file_name, reference_profile=reference_profile)
        metadata_finished = perf_counter()
        ai_result = self.ai_analyzer.analyze(content)
        ai_finished = perf_counter()
        trust_result = self.trust_engine.score(
            blockchain=blockchain_result,
            metadata=metadata_result,
            ai=ai_result,
        )
        trust_finished = perf_counter()

        return VerificationReport(
            file_name=file_name,
            media_hash=media_hash,
            generated_at=utc_now_iso(),
            blockchain=blockchain_result,
            reference=reference_result,
            metadata=metadata_result,
            ai=ai_result,
            trust=trust_result,
            provenance_record=provenance_record.to_dict() if provenance_record else None,
            reference_record=reference_record.to_dict() if reference_record else None,
            system_metrics=SystemMetrics(
                hash_generation_ms=(hash_finished - verification_started) * 1000,
                blockchain_lookup_ms=(blockchain_finished - hash_finished) * 1000,
                metadata_analysis_ms=(metadata_finished - blockchain_finished) * 1000,
                ai_analysis_ms=(ai_finished - metadata_finished) * 1000,
                trust_scoring_ms=(trust_finished - ai_finished) * 1000,
                total_verification_ms=(trust_finished - verification_started) * 1000,
            ),
            pipeline=self.stages,
        )

    def _select_reference_profile(
        self,
        provenance_record: ProvenanceRecord | None,
        reference_record: ProvenanceRecord | None,
    ) -> dict | None:
        if reference_record:
            return reference_record.metadata.get("media_profile")
        if provenance_record:
            return provenance_record.metadata.get("media_profile")
        return None

    def _compare_reference(
        self,
        media_hash: str,
        reference_hash: str | None,
        reference_record: ProvenanceRecord | None,
    ) -> LayerResult | None:
        if not reference_hash:
            return None

        if reference_record is None:
            return LayerResult(
                layer="Selected Reference Comparison",
                status="REFERENCE_NOT_FOUND",
                score=0.0,
                summary="A reference hash was supplied, but no registered record was found.",
                factors=(
                    EvidenceFactor(
                        name="Reference lookup",
                        status="MISS",
                        explanation="The selected reference hash is not present in the provenance ledger.",
                        score=0.0,
                    ),
                ),
                raw={"reference_hash": reference_hash},
            )

        exact_same_file = media_hash == reference_hash
        has_profile = bool(reference_record.metadata.get("media_profile"))
        return LayerResult(
            layer="Selected Reference Comparison",
            status="EXACT_MATCH" if exact_same_file else "DERIVATIVE_CHECK",
            score=1.0 if exact_same_file else 0.65 if has_profile else 0.35,
            summary="The uploaded media is being compared against a user-selected registered original.",
            factors=(
                EvidenceFactor(
                    name="Reference lookup",
                    status="FOUND",
                    explanation="The selected reference exists in the provenance ledger.",
                    score=1.0,
                ),
                EvidenceFactor(
                    name="Hash relationship",
                    status="SAME_HASH" if exact_same_file else "DIFFERENT_HASH",
                    explanation="Uploaded hash matches the selected reference hash."
                    if exact_same_file
                    else "Uploaded hash differs from the selected reference, so this is not exact provenance verification.",
                    score=1.0 if exact_same_file else 0.35,
                ),
                EvidenceFactor(
                    name="Reference metadata profile",
                    status="AVAILABLE" if has_profile else "MISSING",
                    explanation="The reference includes a captured metadata profile for drift comparison."
                    if has_profile
                    else "The reference was registered before metadata profiles were captured; re-register it to upgrade the local demo record.",
                    score=1.0 if has_profile else 0.25,
                ),
            ),
            raw={
                "uploaded_hash": media_hash,
                "reference_hash": reference_hash,
                "reference_transaction_id": reference_record.transaction_id,
            },
        )
