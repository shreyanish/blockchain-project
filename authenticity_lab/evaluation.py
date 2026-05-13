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


def default_cases(root: Path) -> list[EvaluationCase]:
    return [
        EvaluationCase(
            name="registered-original",
            file_path=root / "samples" / "authentic_reference.png",
            action="verify",
            reference="authentic_reference.png",
            expected={"blockchain": "VERIFIED", "metadata": "CONSISTENT"},
        ),
        EvaluationCase(
            name="edited-reference-comparison",
            file_path=root / "samples" / "edited_variant.jpg",
            action="verify",
            reference="authentic_reference.png",
            expected={"blockchain": "UNREGISTERED", "reference": "DERIVATIVE_CHECK", "metadata": "PARTIAL"},
        ),
        EvaluationCase(
            name="synthetic-unknown",
            file_path=root / "samples" / "synthetic_stress_test.png",
            action="verify",
            reference=None,
            expected={"blockchain": "UNREGISTERED"},
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
                    "passed": passed,
                    "ai_model": report.ai.raw.get("model"),
                    "ai_mode": report.ai.raw.get("mode"),
                    "ai_limitations": report.ai.raw.get("limitations"),
                }
            )

    return {
        "ai_mode": ai_mode,
        "summary": {
            "cases": len(case_results),
            "passed": sum(1 for result in case_results if result["passed"]),
        },
        "cases": case_results,
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
        "| Case | File | Expected | Observed | Scores | Pass |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in payload["cases"]:
        expected = ", ".join(f"{key}={value}" for key, value in result["expected"].items())
        observed = ", ".join(f"{key}={value}" for key, value in result["observed"].items() if value)
        scores = ", ".join(
            f"{key}={value:.0%}" for key, value in result["scores"].items() if value is not None
        )
        lines.append(
            f"| {result['name']} | `{result['file']}` | {expected} | {observed} | {scores} | "
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
