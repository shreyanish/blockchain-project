from __future__ import annotations

from authenticity_lab.core.models import EvidenceFactor, LayerResult


class TrustScoreEngine:
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "blockchain": 0.40,
            "ai": 0.40,
            "metadata": 0.20,
        }

    def score(self, blockchain: LayerResult, metadata: LayerResult, ai: LayerResult) -> LayerResult:
        weighted_score = (
            blockchain.score * self.weights["blockchain"]
            + ai.score * self.weights["ai"]
            + metadata.score * self.weights["metadata"]
        )

        if weighted_score >= 0.80:
            status = "HIGH_TRUST"
        elif weighted_score >= 0.55:
            status = "MEDIUM_TRUST"
        elif weighted_score >= 0.30:
            status = "LOW_TRUST"
        else:
            status = "UNVERIFIED"

        factors = (
            EvidenceFactor(
                name="Blockchain provenance",
                status=blockchain.status,
                explanation=f"Contribution: {self.weights['blockchain']:.0%} x {blockchain.score:.0%}.",
                score=blockchain.score * self.weights["blockchain"],
            ),
            EvidenceFactor(
                name="AI authenticity analysis",
                status=ai.status,
                explanation=f"Contribution: {self.weights['ai']:.0%} x {ai.score:.0%}.",
                score=ai.score * self.weights["ai"],
            ),
            EvidenceFactor(
                name="Metadata integrity",
                status=metadata.status,
                explanation=f"Contribution: {self.weights['metadata']:.0%} x {metadata.score:.0%}.",
                score=metadata.score * self.weights["metadata"],
            ),
        )

        return LayerResult(
            layer="Final Trust Score",
            status=status,
            score=weighted_score,
            summary="Weighted, explainable trust score combining deterministic and probabilistic evidence.",
            factors=factors,
            raw={"weights": self.weights},
        )
