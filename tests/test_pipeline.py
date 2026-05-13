import tempfile
import unittest
from pathlib import Path

from authenticity_lab.core.hashing import sha256_bytes
from authenticity_lab.core.metadata import MetadataAnalyzer
from authenticity_lab.core.pipeline import VerificationPipeline
from authenticity_lab.core.provenance import LocalResearchLedger, ProvenanceService


class PipelineTests(unittest.TestCase):
    def test_sha256_bytes_is_deterministic(self):
        content = b"research prototype"

        self.assertEqual(sha256_bytes(content), sha256_bytes(content))
        self.assertNotEqual(sha256_bytes(content), sha256_bytes(b"edited prototype"))

    def test_register_then_verify_reports_provenance_match(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = LocalResearchLedger(Path(directory) / "records.json")
            pipeline = VerificationPipeline(ProvenanceService(ledger))
            content = b"not an image yet, but hashable"

            record = pipeline.register(content=content, file_name="sample.bin", owner="tester")
            report = pipeline.verify(content=content, file_name="sample.bin")

            self.assertEqual(record.media_hash, report.media_hash)
            self.assertEqual(report.blockchain.status, "VERIFIED")
            self.assertIsNotNone(report.provenance_record)
            self.assertGreater(report.trust.score, 0)

    def test_unknown_media_is_unregistered(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = LocalResearchLedger(Path(directory) / "records.json")
            pipeline = VerificationPipeline(ProvenanceService(ledger))

            report = pipeline.verify(content=b"unknown", file_name="unknown.bin")

            self.assertEqual(report.blockchain.status, "UNREGISTERED")
            self.assertIsNone(report.provenance_record)

    def test_existing_local_record_can_be_upgraded_with_media_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = LocalResearchLedger(Path(directory) / "records.json")
            content = b"legacy record content"
            media_hash = sha256_bytes(content)

            legacy = ledger.register(media_hash, "tester", {"storage_policy": "hash-only"})
            upgraded = ledger.register(
                media_hash,
                "tester",
                {"storage_policy": "hash-only", "media_profile": {"format": "PNG"}},
            )

            self.assertEqual(legacy.transaction_id, upgraded.transaction_id)
            self.assertEqual(upgraded.metadata["media_profile"]["format"], "PNG")

    def test_sample_metadata_changes_between_reference_and_edited_variant(self):
        root = Path(__file__).resolve().parents[1]
        reference_path = root / "samples" / "authentic_reference.png"
        edited_path = root / "samples" / "edited_variant.jpg"
        analyzer = MetadataAnalyzer()

        reference_content = reference_path.read_bytes()
        edited_content = edited_path.read_bytes()
        reference_profile = analyzer.inspect_profile(reference_content, reference_path.name)

        reference_result = analyzer.analyze(
            reference_content,
            reference_path.name,
            reference_profile=reference_profile,
        )
        edited_result = analyzer.analyze(
            edited_content,
            edited_path.name,
            reference_profile=reference_profile,
        )

        self.assertLess(edited_result.score, reference_result.score)
        self.assertTrue(
            any(factor.status == "MISMATCH" for factor in edited_result.factors),
            "Edited sample should expose registered-profile mismatches.",
        )

    def test_edited_sample_can_be_compared_against_registered_reference(self):
        root = Path(__file__).resolve().parents[1]
        reference_path = root / "samples" / "authentic_reference.png"
        edited_path = root / "samples" / "edited_variant.jpg"

        with tempfile.TemporaryDirectory() as directory:
            ledger = LocalResearchLedger(Path(directory) / "records.json")
            pipeline = VerificationPipeline(ProvenanceService(ledger))
            reference_content = reference_path.read_bytes()
            edited_content = edited_path.read_bytes()

            reference_record = pipeline.register(
                content=reference_content,
                file_name=reference_path.name,
                owner="tester",
            )
            report = pipeline.verify(
                content=edited_content,
                file_name=edited_path.name,
                reference_hash=reference_record.media_hash,
            )

            self.assertEqual(report.blockchain.status, "UNREGISTERED")
            self.assertIsNotNone(report.reference)
            self.assertEqual(report.reference.status, "DERIVATIVE_CHECK")
            self.assertIsNotNone(report.reference_record)
            self.assertLess(report.metadata.score, 0.75)


if __name__ == "__main__":
    unittest.main()
