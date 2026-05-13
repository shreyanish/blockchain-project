from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from authenticity_lab.core.ai import build_authenticity_analyzer
from authenticity_lab.core.pipeline import VerificationPipeline
from authenticity_lab.core.provenance import LocalResearchLedger, ProvenanceService


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    file_path: Path
    action: str
    reference: str | None
    expected: dict[str, str]
    ai_ground_truth: str
    framework_ground_truth: str


def default_cases(root: Path) -> list[EvaluationCase]:
    return [
        EvaluationCase(
            name="registered-original",
            file_path=root / "samples" / "authentic_reference.png",
            action="verify",
            reference="authentic_reference.png",
            expected={"blockchain": "VERIFIED", "metadata": "CONSISTENT", "trust": "HIGH_TRUST"},
            ai_ground_truth="authentic",
            framework_ground_truth="registered_authentic",
        ),
        EvaluationCase(
            name="edited-reference-comparison",
            file_path=root / "samples" / "edited_variant.jpg",
            action="verify",
            reference="authentic_reference.png",
            expected={"blockchain": "UNREGISTERED", "reference": "DERIVATIVE_CHECK", "metadata": "PARTIAL", "trust": "LOW_TRUST"},
            ai_ground_truth="manipulated",
            framework_ground_truth="tampered_derivative",
        ),
        EvaluationCase(
            name="deepfake-synthetic-proxy",
            file_path=root / "samples" / "deepfake_proxy.png",
            action="verify",
            reference=None,
            expected={"blockchain": "UNREGISTERED", "ai": "SUSPICIOUS", "trust": "LOW_TRUST"},
            ai_ground_truth="manipulated",
            framework_ground_truth="synthetic_unregistered",
        ),
        EvaluationCase(
            name="unknown-unregistered-image",
            file_path=root / "samples" / "unknown_unregistered.png",
            action="verify",
            reference=None,
            expected={"blockchain": "UNREGISTERED", "trust": "LOW_TRUST"},
            ai_ground_truth="authentic",
            framework_ground_truth="unknown_unregistered",
        ),
        EvaluationCase(
            name="synthetic-stress-unknown",
            file_path=root / "samples" / "synthetic_stress_test.png",
            action="verify",
            reference=None,
            expected={"blockchain": "UNREGISTERED", "trust": "LOW_TRUST"},
            ai_ground_truth="manipulated",
            framework_ground_truth="synthetic_unregistered",
        ),
    ]


def run_evaluation(root: Path, ai_mode: str = "heuristic") -> dict[str, Any]:
    with TemporaryDirectory() as directory:
        ledger = LocalResearchLedger(Path(directory) / "records.json")
        pipeline = VerificationPipeline(
            ProvenanceService(ledger),
            ai_analyzer=build_authenticity_analyzer(ai_mode),
        )
        reference_path = root / "samples" / "authentic_reference.png"
        reference_record = pipeline.register(
            content=reference_path.read_bytes(),
            file_name=reference_path.name,
            owner="evaluation-fixture",
        )
        references = {reference_path.name: reference_record.media_hash}
        case_results = []

        for case in default_cases(root):
            reference_hash = references.get(case.reference) if case.reference else None
            report = pipeline.verify(
                content=case.file_path.read_bytes(),
                file_name=case.file_path.name,
                reference_hash=reference_hash,
            )
            observed = {
                "blockchain": report.blockchain.status,
                "reference": report.reference.status if report.reference else None,
                "metadata": report.metadata.status,
                "ai": report.ai.status,
                "trust": report.trust.status,
            }
            passed = all(observed.get(layer) == expected for layer, expected in case.expected.items())
            case_results.append(
                {
                    "name": case.name,
                    "file": str(case.file_path.relative_to(root)),
                    "expected": case.expected,
                    "observed": observed,
                    "scores": {
                        "blockchain": round(report.blockchain.score, 4),
                        "reference": round(report.reference.score, 4) if report.reference else None,
                        "metadata": round(report.metadata.score, 4),
                        "ai": round(report.ai.score, 4),
                        "trust": round(report.trust.score, 4),
                    },
                    "system_metrics": report.system_metrics.to_dict(),
                    "ai_ground_truth": case.ai_ground_truth,
                    "framework_ground_truth": case.framework_ground_truth,
                    "passed": passed,
                    "ai_model": report.ai.raw.get("model"),
                    "ai_mode": report.ai.raw.get("mode"),
                    "ai_limitations": report.ai.raw.get("limitations"),
                }
            )

    ai_metrics = _classification_metrics(
        expected=[result["ai_ground_truth"] == "manipulated" for result in case_results],
        observed=[
            _is_ai_suspicious(result["observed"]["ai"], result["scores"]["ai"])
            for result in case_results
        ],
    )

    return {
        "ai_mode": ai_mode,
        "summary": {
            "cases": len(case_results),
            "passed": sum(1 for result in case_results if result["passed"]),
        },
        "metrics": {
            "ai": ai_metrics,
            "system": _system_metrics(case_results),
            "framework": _framework_metrics(case_results),
        },
        "cases": case_results,
    }


def _is_ai_suspicious(status: str | None, score: float | None) -> bool:
    normalized = (status or "").upper()
    return "SUSPICIOUS" in normalized or (score is not None and score < 0.45)


def _classification_metrics(expected: list[bool], observed: list[bool]) -> dict[str, float | int]:
    true_positive = sum(1 for exp, obs in zip(expected, observed) if exp and obs)
    true_negative = sum(1 for exp, obs in zip(expected, observed) if not exp and not obs)
    false_positive = sum(1 for exp, obs in zip(expected, observed) if not exp and obs)
    false_negative = sum(1 for exp, obs in zip(expected, observed) if exp and not obs)

    accuracy = (true_positive + true_negative) / len(expected) if expected else 0.0
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def _system_metrics(case_results: list[dict[str, Any]]) -> dict[str, float]:
    metric_keys = (
        "hash_generation_ms",
        "blockchain_lookup_ms",
        "metadata_analysis_ms",
        "ai_analysis_ms",
        "trust_scoring_ms",
        "total_verification_ms",
    )
    return {
        f"mean_{key}": round(
            sum(result["system_metrics"][key] for result in case_results) / len(case_results),
            3,
        )
        for key in metric_keys
    }


def _framework_metrics(case_results: list[dict[str, Any]]) -> dict[str, float]:
    expected_trust = {
        "registered_authentic": "HIGH_TRUST",
        "tampered_derivative": "LOW_TRUST",
        "synthetic_unregistered": "LOW_TRUST",
        "unknown_unregistered": "LOW_TRUST",
    }
    trust_consistent = [
        result["observed"]["trust"] == expected_trust[result["framework_ground_truth"]]
        for result in case_results
    ]
    registered_cases = [
        result for result in case_results
        if result["framework_ground_truth"] == "registered_authentic"
    ]
    tamper_cases = [
        result for result in case_results
        if result["framework_ground_truth"] in {"tampered_derivative", "synthetic_unregistered"}
    ]
    provenance_success = [
        result["observed"]["blockchain"] == "VERIFIED"
        for result in registered_cases
    ]
    tamper_detected = [
        result["observed"]["blockchain"] == "UNREGISTERED" and result["observed"]["trust"] != "HIGH_TRUST"
        for result in tamper_cases
    ]

    return {
        "trust_score_consistency": round(sum(trust_consistent) / len(trust_consistent), 4),
        "provenance_verification_success_rate": round(sum(provenance_success) / len(provenance_success), 4) if provenance_success else 0.0,
        "tamper_detection_rate": round(sum(tamper_detected) / len(tamper_detected), 4) if tamper_detected else 0.0,
    }


def write_reports(payload: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    mode = str(payload["ai_mode"]).replace("/", "_").replace(" ", "_")
    json_path = output_dir / "latest_report.json"
    md_path = output_dir / "latest_report.md"
    mode_json_path = output_dir / f"{mode}_report.json"
    mode_md_path = output_dir / f"{mode}_report.md"

    json_payload = json.dumps(payload, indent=2)
    json_path.write_text(json_payload, encoding="utf-8")
    mode_json_path.write_text(json_payload, encoding="utf-8")
    lines = [
        "# Evaluation Report",
        "",
        f"AI mode: `{payload['ai_mode']}`",
        f"Cases passed: {payload['summary']['passed']} / {payload['summary']['cases']}",
        "",
        "## Metrics",
        "",
        "| Group | Metric | Value |",
        "| --- | --- | ---: |",
    ]
    for group, metrics in payload["metrics"].items():
        for key, value in metrics.items():
            if group in {"ai", "framework"} and isinstance(value, float) and value <= 1:
                rendered = f"{value:.1%}"
            elif group == "system" and isinstance(value, float):
                rendered = f"{value:.3f} ms"
            else:
                rendered = str(value)
            lines.append(f"| {group} | {key} | {rendered} |")
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| Case | File | Expected | Observed | Scores | Latency | Pass |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in payload["cases"]:
        expected = ", ".join(f"{key}={value}" for key, value in result["expected"].items())
        observed = ", ".join(f"{key}={value}" for key, value in result["observed"].items() if value)
        scores = ", ".join(
            f"{key}={value:.0%}" for key, value in result["scores"].items() if value is not None
        )
        latency = f"{result['system_metrics']['total_verification_ms']:.3f} ms"
        lines.append(
            f"| {result['name']} | `{result['file']}` | {expected} | {observed} | {scores} | "
            f"{latency} | "
            f"{'PASS' if result['passed'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "## AI Layer Caveat",
            "",
            "The AI layer is an assistive evidence source. It should be interpreted alongside provenance and metadata, not as a standalone real/fake oracle.",
        ]
    )
    markdown_payload = "\n".join(lines) + "\n"
    md_path.write_text(markdown_payload, encoding="utf-8")
    mode_md_path.write_text(markdown_payload, encoding="utf-8")
    return json_path, md_path
