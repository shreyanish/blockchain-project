from __future__ import annotations

from io import BytesIO
from math import log
from statistics import mean
from typing import Protocol

from authenticity_lab.core.models import EvidenceFactor, LayerResult


class AuthenticityAnalyzer(Protocol):
    def analyze(self, content: bytes) -> LayerResult:
        ...


class HeuristicAuthenticityAnalyzer:
    """Lightweight explainable baseline for the AI layer.

    The project architecture treats this as a replaceable adapter. It does not
    claim state-of-the-art deepfake detection; it provides transparent signals
    for early demo and evaluation work until a pretrained image model is added.
    """

    def analyze(self, content: bytes) -> LayerResult:
        try:
            from PIL import Image, ImageStat
        except ImportError:
            return LayerResult(
                layer="AI Authenticity Analysis",
                status="MODEL_UNAVAILABLE",
                score=0.5,
                summary="No pretrained model is configured; returning a neutral explainable baseline.",
                factors=(
                    EvidenceFactor(
                        name="Model adapter",
                        status="UNAVAILABLE",
                        explanation="Install and configure a lightweight pretrained model for stronger AI evidence.",
                        score=0.5,
                    ),
                ),
                raw={"model": "heuristic-baseline"},
            )

        try:
            with Image.open(BytesIO(content)) as image:
                rgb_image = image.convert("RGB")
                grayscale = image.convert("L")
                stat = ImageStat.Stat(rgb_image)
                gray_stat = ImageStat.Stat(grayscale)
        except Exception as exc:
            return LayerResult(
                layer="AI Authenticity Analysis",
                status="UNREADABLE",
                score=0.0,
                summary="The AI analysis layer could not read the image.",
                factors=(
                    EvidenceFactor(
                        name="Image preprocessing",
                        status="FAILED",
                        explanation=f"Preprocessing error: {exc}",
                        score=0.0,
                    ),
                ),
                raw={"model": "heuristic-baseline"},
            )

        channel_means = stat.mean
        channel_std = stat.stddev
        brightness = mean(channel_means) / 255
        texture = mean(channel_std) / 128
        contrast = (gray_stat.extrema[0][1] - gray_stat.extrema[0][0]) / 255

        brightness_score = 1 - min(abs(brightness - 0.5) * 1.6, 0.8)
        texture_score = max(0.2, min(texture, 1.0))
        contrast_score = max(0.2, min(contrast * 1.2, 1.0))
        authenticity_probability = (brightness_score * 0.25) + (texture_score * 0.35) + (contrast_score * 0.40)

        factors = (
            EvidenceFactor(
                name="Luminance distribution",
                status="BALANCED" if brightness_score >= 0.65 else "ATYPICAL",
                explanation="Extreme brightness can indicate aggressive editing or poor acquisition conditions.",
                score=brightness_score,
            ),
            EvidenceFactor(
                name="Texture variation",
                status="RICH" if texture_score >= 0.55 else "LOW",
                explanation="Low texture variation may indicate smoothing, compression, or synthetic artifacts.",
                score=texture_score,
            ),
            EvidenceFactor(
                name="Contrast range",
                status="NATURAL_RANGE" if contrast_score >= 0.55 else "LIMITED",
                explanation="Limited tonal range can reduce confidence in visual authenticity.",
                score=contrast_score,
            ),
        )

        if authenticity_probability >= 0.75:
            status = "LIKELY_AUTHENTIC"
        elif authenticity_probability >= 0.45:
            status = "UNCERTAIN"
        else:
            status = "SUSPICIOUS"

        return LayerResult(
            layer="AI Authenticity Analysis",
            status=status,
            score=authenticity_probability,
            summary="A lightweight explainable baseline estimated visual authenticity likelihood.",
            factors=factors,
            raw={
                "model": "heuristic-baseline",
                "mode": "inference",
                "limitations": "Explainable baseline only; not trained for deepfake detection.",
                "note": "Replaceable adapter; not a claim of production deepfake accuracy.",
                "brightness": round(brightness, 4),
                "texture": round(texture, 4),
                "contrast": round(contrast, 4),
            },
        )


class PretrainedMobileNetAuthenticityAnalyzer:
    """Optional CPU-friendly pretrained adapter using torchvision MobileNetV3.

    This model is pretrained for ImageNet classification, not deepfake
    detection. In this prototype it contributes visual-distribution evidence
    such as confidence concentration and entropy, while the report clearly
    exposes that limitation.
    """

    def analyze(self, content: bytes) -> LayerResult:
        try:
            import torch
            from PIL import Image
            from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small
        except ImportError:
            return LayerResult(
                layer="AI Authenticity Analysis",
                status="MODEL_UNAVAILABLE",
                score=0.5,
                summary="Pretrained mode was requested, but torch/torchvision is not installed.",
                factors=(
                    EvidenceFactor(
                        name="Pretrained adapter",
                        status="UNAVAILABLE",
                        explanation="Install optional torch and torchvision dependencies to enable MobileNetV3 inference.",
                        score=0.5,
                    ),
                ),
                raw={
                    "model": "mobilenet_v3_small",
                    "mode": "unavailable",
                    "limitations": "Pretrained ImageNet model; not a dedicated deepfake detector.",
                },
            )

        try:
            image = Image.open(BytesIO(content)).convert("RGB")
            weights = MobileNet_V3_Small_Weights.DEFAULT
            model = mobilenet_v3_small(weights=weights)
            model.eval()
            preprocess = weights.transforms()
            batch = preprocess(image).unsqueeze(0)
            with torch.no_grad():
                probabilities = torch.nn.functional.softmax(model(batch)[0], dim=0)
            top_probabilities, top_indices = torch.topk(probabilities, 5)
            categories = weights.meta.get("categories", [])
        except Exception as exc:
            return LayerResult(
                layer="AI Authenticity Analysis",
                status="MODEL_ERROR",
                score=0.35,
                summary="Pretrained model inference failed.",
                factors=(
                    EvidenceFactor(
                        name="Pretrained inference",
                        status="FAILED",
                        explanation=f"Inference error: {exc}",
                        score=0.35,
                    ),
                ),
                raw={"model": "mobilenet_v3_small", "mode": "error"},
            )

        top_values = [float(value) for value in top_probabilities]
        entropy = -sum(value * log(max(value, 1e-12)) for value in probabilities.tolist())
        normalized_entropy = min(entropy / log(len(probabilities)), 1.0)
        confidence_concentration = top_values[0]
        distribution_score = (normalized_entropy * 0.45) + ((1 - min(confidence_concentration, 0.95)) * 0.35) + 0.20
        distribution_score = max(0.15, min(distribution_score, 0.9))

        if distribution_score >= 0.70:
            status = "LIKELY_NATURAL_DISTRIBUTION"
        elif distribution_score >= 0.45:
            status = "UNCERTAIN"
        else:
            status = "SUSPICIOUS_DISTRIBUTION"

        labels = [
            categories[index] if index < len(categories) else str(index)
            for index in [int(index) for index in top_indices]
        ]

        return LayerResult(
            layer="AI Authenticity Analysis",
            status=status,
            score=distribution_score,
            summary="Optional pretrained MobileNetV3 adapter analyzed visual distribution signals.",
            factors=(
                EvidenceFactor(
                    name="Pretrained inference",
                    status="COMPLETED",
                    explanation="MobileNetV3 Small ran in local inference mode.",
                    score=1.0,
                ),
                EvidenceFactor(
                    name="Prediction concentration",
                    status="DIFFUSE" if confidence_concentration < 0.55 else "CONCENTRATED",
                    explanation="Overly concentrated predictions can indicate narrow or artificial visual evidence.",
                    score=1 - min(confidence_concentration, 0.95),
                ),
                EvidenceFactor(
                    name="Class-distribution entropy",
                    status="BROAD" if normalized_entropy >= 0.55 else "NARROW",
                    explanation="Entropy summarizes how broadly the pretrained model distributes confidence.",
                    score=normalized_entropy,
                ),
            ),
            raw={
                "model": "mobilenet_v3_small",
                "weights": "MobileNet_V3_Small_Weights.DEFAULT",
                "mode": "pretrained-inference",
                "limitations": "ImageNet-pretrained evidence only; not calibrated for deepfake detection.",
                "top_predictions": [
                    {"label": label, "probability": round(probability, 4)}
                    for label, probability in zip(labels, top_values)
                ],
                "normalized_entropy": round(normalized_entropy, 4),
            },
        )


class FallbackAuthenticityAnalyzer:
    def __init__(self, primary: AuthenticityAnalyzer, fallback: AuthenticityAnalyzer | None = None) -> None:
        self.primary = primary
        self.fallback = fallback or HeuristicAuthenticityAnalyzer()

    def analyze(self, content: bytes) -> LayerResult:
        result = self.primary.analyze(content)
        if result.status not in {"MODEL_UNAVAILABLE", "MODEL_ERROR"}:
            return result

        fallback = self.fallback.analyze(content)
        return LayerResult(
            layer=fallback.layer,
            status=fallback.status,
            score=fallback.score,
            summary=f"{fallback.summary} Pretrained adapter was unavailable, so the transparent baseline was used.",
            factors=(
                EvidenceFactor(
                    name="Pretrained adapter",
                    status=result.status,
                    explanation=result.summary,
                    score=result.score,
                ),
                *fallback.factors,
            ),
            raw={
                **fallback.raw,
                "requested_model": result.raw,
                "fallback_used": True,
            },
        )


def build_authenticity_analyzer(mode: str = "heuristic") -> AuthenticityAnalyzer:
    normalized = mode.strip().lower()
    if normalized == "pretrained":
        return FallbackAuthenticityAnalyzer(PretrainedMobileNetAuthenticityAnalyzer())
    return HeuristicAuthenticityAnalyzer()
