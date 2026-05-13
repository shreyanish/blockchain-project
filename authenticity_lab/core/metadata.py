from __future__ import annotations

from io import BytesIO

from authenticity_lab.core.models import EvidenceFactor, LayerResult


class MetadataAnalyzer:
    """Forensic metadata checks with graceful degradation when Pillow is absent."""

    def inspect_profile(self, content: bytes, file_name: str) -> dict:
        try:
            from PIL import Image, ExifTags
        except ImportError:
            return {"file_name": file_name, "byte_size": len(content), "parser": "unavailable"}

        raw: dict = {"file_name": file_name, "byte_size": len(content)}
        try:
            with Image.open(BytesIO(content)) as image:
                image.verify()
            with Image.open(BytesIO(content)) as image:
                raw.update(
                    {
                        "format": image.format,
                        "mode": image.mode,
                        "width": image.width,
                        "height": image.height,
                        "megapixels": round((image.width * image.height) / 1_000_000, 4),
                    }
                )
                exif = image.getexif()
                exif_map = {
                    ExifTags.TAGS.get(tag, str(tag)): value
                    for tag, value in exif.items()
                    if isinstance(value, (str, int, float))
                }
                raw["exif"] = exif_map
                raw["exif_tag_count"] = len(exif_map)
                if image.format == "JPEG":
                    raw["jpeg_quality_indicator"] = self._jpeg_quality_indicator(image, len(content))
        except Exception as exc:
            raw["parser_error"] = str(exc)

        return raw

    def analyze(self, content: bytes, file_name: str, reference_profile: dict | None = None) -> LayerResult:
        try:
            from PIL import Image
        except ImportError:
            return LayerResult(
                layer="Metadata Integrity",
                status="PARTIAL",
                score=0.5,
                summary="Pillow is not installed, so only byte-level metadata analysis is available.",
                factors=(
                    EvidenceFactor(
                        name="Image parser",
                        status="UNAVAILABLE",
                        explanation="Install Pillow to inspect image format, dimensions, and EXIF tags.",
                        score=0.5,
                    ),
                ),
                raw={"file_name": file_name, "byte_size": len(content)},
            )

        factors: list[EvidenceFactor] = []
        raw = self.inspect_profile(content, file_name)

        if "parser_error" in raw:
            return LayerResult(
                layer="Metadata Integrity",
                status="INVALID",
                score=0.0,
                summary="The file could not be parsed as a supported image.",
                factors=(
                    EvidenceFactor(
                        name="Image parser",
                        status="FAILED",
                        explanation=f"Parser error: {raw['parser_error']}",
                        score=0.0,
                    ),
                ),
                raw=raw,
            )

        exif_map = raw.get("exif", {})
        has_dimensions = raw.get("width", 0) > 0 and raw.get("height", 0) > 0
        factors.append(
            EvidenceFactor(
                name="Image structure",
                status="VALID" if has_dimensions else "SUSPICIOUS",
                explanation="The image opened successfully and exposed usable dimensions."
                if has_dimensions
                else "The image opened, but dimensions were missing or invalid.",
                score=1.0 if has_dimensions else 0.2,
            )
        )

        if exif_map:
            factors.append(
                EvidenceFactor(
                    name="EXIF presence",
                    status="PRESENT",
                    explanation="EXIF metadata was found, which can support provenance interpretation.",
                    score=0.8,
                )
            )
        else:
            factors.append(
                EvidenceFactor(
                    name="EXIF presence",
                    status="MISSING",
                    explanation="Missing EXIF is common online, but it reduces forensic context.",
                    score=0.45,
                )
            )

        software = str(exif_map.get("Software", "")).lower()
        if software:
            suspicious_terms = ("photoshop", "gimp", "snapseed", "lightroom", "editor")
            edited = any(term in software for term in suspicious_terms)
            factors.append(
                EvidenceFactor(
                    name="Editing software trace",
                    status="SUSPICIOUS" if edited else "OBSERVED",
                    explanation=f"Software tag reports: {exif_map.get('Software')}",
                    score=0.25 if edited else 0.75,
                )
            )
        else:
            factors.append(
                EvidenceFactor(
                    name="Editing software trace",
                    status="ABSENT",
                    explanation="No editing software tag was found.",
                    score=0.65,
                )
            )

        suffix = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        format_name = str(raw.get("format", "")).lower()
        expected = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(suffix)
        consistent_format = expected is None or expected == format_name
        factors.append(
            EvidenceFactor(
                name="Extension and format",
                status="CONSISTENT" if consistent_format else "MISMATCH",
                explanation="File extension matches the parsed image format."
                if consistent_format
                else f"Extension .{suffix} does not match parsed format {raw.get('format')}.",
                score=1.0 if consistent_format else 0.2,
            )
        )

        format_name = str(raw.get("format", "")).upper()
        jpeg_quality = raw.get("jpeg_quality_indicator")
        if format_name == "JPEG" and jpeg_quality:
            compressed = jpeg_quality["score"] < 0.55
            factors.append(
                EvidenceFactor(
                    name="Compression signal",
                    status="HEAVY_COMPRESSION" if compressed else "NORMAL",
                    explanation=jpeg_quality["explanation"],
                    score=jpeg_quality["score"],
                )
            )
        elif format_name in {"PNG", "TIFF"}:
            factors.append(
                EvidenceFactor(
                    name="Compression signal",
                    status="LOSSLESS_CONTAINER",
                    explanation=f"{format_name} is a lossless-oriented container, so recompression suspicion is low.",
                    score=0.9,
                )
            )
        else:
            factors.append(
                EvidenceFactor(
                    name="Compression signal",
                    status="UNASSESSED",
                    explanation="No format-specific compression signal was available.",
                    score=0.6,
                )
            )

        if reference_profile:
            factors.extend(self._compare_reference(raw, reference_profile))
        else:
            factors.append(
                EvidenceFactor(
                    name="Registered metadata profile",
                    status="NO_REFERENCE",
                    explanation="No matching provenance record was available for metadata-profile comparison.",
                    score=0.5,
                )
            )

        score = sum(factor.score or 0.0 for factor in factors) / len(factors)
        if score >= 0.75:
            status = "CONSISTENT"
        elif score >= 0.45:
            status = "PARTIAL"
        else:
            status = "SUSPICIOUS"

        return LayerResult(
            layer="Metadata Integrity",
            status=status,
            score=score,
            summary="Metadata checks produced interpretable forensic signals.",
            factors=tuple(factors),
            raw=raw,
        )

    def _compare_reference(self, current: dict, reference: dict) -> tuple[EvidenceFactor, ...]:
        factors: list[EvidenceFactor] = []
        current_format = current.get("format")
        reference_format = reference.get("format")
        format_match = current_format == reference_format
        factors.append(
            EvidenceFactor(
                name="Registered format match",
                status="MATCH" if format_match else "MISMATCH",
                explanation="Parsed format matches the registered media profile."
                if format_match
                else f"Current format {current_format} differs from registered format {reference_format}.",
                score=1.0 if format_match else 0.1,
            )
        )

        current_dimensions = (current.get("width"), current.get("height"))
        reference_dimensions = (reference.get("width"), reference.get("height"))
        dimensions_match = current_dimensions == reference_dimensions
        factors.append(
            EvidenceFactor(
                name="Registered dimension match",
                status="MATCH" if dimensions_match else "MISMATCH",
                explanation="Dimensions match the registered media profile."
                if dimensions_match
                else f"Current dimensions {current_dimensions} differ from registered dimensions {reference_dimensions}.",
                score=1.0 if dimensions_match else 0.15,
            )
        )

        current_size = current.get("byte_size") or 0
        reference_size = reference.get("byte_size") or 0
        if reference_size:
            size_delta = abs(current_size - reference_size) / reference_size
            stable_size = size_delta <= 0.05
            factors.append(
                EvidenceFactor(
                    name="Registered byte-size drift",
                    status="STABLE" if stable_size else "DRIFT",
                    explanation=f"Byte size changed by {size_delta:.1%} from the registered media profile.",
                    score=1.0 if stable_size else max(0.1, 1 - size_delta),
                )
            )

        return tuple(factors)

    def _jpeg_quality_indicator(self, image: Image.Image, byte_size: int) -> dict:
        megapixels = max((image.width * image.height) / 1_000_000, 0.01)
        bytes_per_megapixel = byte_size / megapixels

        if bytes_per_megapixel < 90_000:
            return {
                "score": 0.25,
                "bytes_per_megapixel": round(bytes_per_megapixel, 2),
                "explanation": "JPEG byte density is very low, which suggests aggressive recompression.",
            }
        if bytes_per_megapixel < 180_000:
            return {
                "score": 0.55,
                "bytes_per_megapixel": round(bytes_per_megapixel, 2),
                "explanation": "JPEG byte density is modest, which may indicate recompression.",
            }
        return {
            "score": 0.8,
            "bytes_per_megapixel": round(bytes_per_megapixel, 2),
            "explanation": "JPEG byte density is not unusually low for this image size.",
        }
