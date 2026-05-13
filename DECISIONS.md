# Architectural Decisions

This log records major implementation decisions, tradeoffs, rejected alternatives, and dependency rationale. `PROJECT_NORTH_STAR.md` remains the authoritative project source.

## Decision 1: Start With a Modular Flask Prototype

**Choice:** Use a small Flask app with separate core modules for hashing, provenance, metadata analysis, AI authenticity analysis, trust scoring, and reporting.

**Tradeoff:** Flask provides less built-in structure than a larger framework, but it keeps the prototype lightweight, inspectable, and easy to run on macOS.

**Simpler alternative considered:** A single Python script. Rejected because it would make the verification pipeline harder to explain, test, and present academically.

**Heavier alternative considered:** Django or a full SPA/API stack. Rejected because it would add ceremony without improving the research contribution.

**Rationale:** The project needs transparent architecture more than production infrastructure.

## Decision 2: Use a Local Research Ledger as the Default Provenance Store

**Choice:** Use an append-only JSON ledger by default, with a separate Ganache/Web3 adapter and Solidity contract for blockchain-backed runs.

**Tradeoff:** The default path is not a true blockchain, but it makes the demo deterministic and usable even when Ganache is not running.

**Simpler alternative considered:** Store provenance only in memory. Rejected because the demo needs persistent records and provenance exploration.

**Heavier alternative considered:** Require Ganache and deployed contracts for every run. Rejected because that creates setup friction and weakens demo reliability on student machines.

**Rationale:** The architecture exposes the blockchain boundary while keeping the prototype feasible. The UI and report label the default as a local research ledger, not production immutability.

## Decision 3: Store Hashes and Provenance Metadata Only

**Choice:** Store SHA-256 hash, owner identifier, timestamp, transaction identifier, block number, and small provenance metadata.

**Tradeoff:** The system cannot recover media content from provenance records, but that is a deliberate privacy and scope constraint.

**Rejected alternative:** Store media files or thumbnails inside the provenance layer. Rejected because the north star explicitly forbids storing media on-chain.

**Rationale:** This keeps the project aligned with blockchain provenance principles and avoids unnecessary storage complexity.

## Decision 4: Use an Explainable AI Baseline Adapter First

**Choice:** Implement a lightweight heuristic authenticity analyzer behind an AI-layer interface.

**Tradeoff:** The current analyzer is not a pretrained deepfake model, so it should not be used as a final claim about AI detection performance.

**Simpler alternative considered:** Return a fixed placeholder score. Rejected because it would hide the role of visual evidence and make the demo less educational.

**Heavier alternative considered:** Add a GPU-heavy or transformer-based deepfake detector. Rejected because the project must remain macOS-compatible and should not train models from scratch.

**Rationale:** The adapter makes the pipeline demoable now and creates a clean replacement point for a lightweight pretrained model later.

## Decision 5: Weighted Trust Score With Visible Contributions

**Choice:** Use the north-star weighting: 40% blockchain provenance, 40% AI authenticity analysis, 20% metadata integrity.

**Tradeoff:** A weighted score is simple and explainable, but it is not statistically calibrated.

**Simpler alternative considered:** Binary real/fake output. Rejected because the project explicitly prioritizes interpretability over binary classification.

**Heavier alternative considered:** Bayesian fusion or learned score calibration. Rejected for the first prototype because it would require a larger labeled dataset and reduce immediate explainability.

**Rationale:** The weighted score directly supports research-demo clarity and lets users inspect each contribution.

## Dependency Rationale

| Dependency | Necessity | Maintainability | macOS Compatibility | Demo Value |
| --- | --- | --- | --- | --- |
| Flask | Serves the web UI and API with minimal framework overhead. | Mature and simple. | Strong. | High: makes the prototype interactive. |
| Pillow | Reads image dimensions, format, and EXIF metadata. | Mature and common. | Strong, including Apple Silicon wheels. | High: enables visible forensic checks. |
| web3 | Connects to Ganache and the Solidity provenance contract. | Standard Python Ethereum client. | Good, but optional at runtime. | Medium-high: enables blockchain-backed provenance demonstrations. |
| blo | Browser-only Ethereum identicons for provenance records. | Tiny, zero-dependency library loaded from ESM CDN with graceful fallback. | Browser-compatible. | Medium: makes hash/record identity easier to scan and gives the explorer a web3-native feel. |
| torch/torchvision | Optional MobileNetV3 pretrained adapter. | Mature but large, so excluded from default install. | Works on macOS CPU/Apple Silicon, but install size is significant. | Medium-high when enabled: supports a stronger pretrained-inference story. |

## Decision 6: Use Standard-Library Tests for the First Pass

**Choice:** Use `unittest` for the initial deterministic tests.

**Tradeoff:** `unittest` is less ergonomic than `pytest`, but it avoids adding a test-only dependency before the project needs fixtures or plugins.

**Rejected alternative:** Add `pytest` immediately. Rejected because the current tests are simple enough to run with Python alone.

**Rationale:** Lower setup friction improves local demo reliability and keeps the first prototype easy for students to execute.

## Decision 7: Add Metadata Profile Comparison to the Local Demo Ledger

**Choice:** Store a parsed media profile during registration and compare later verification attempts against it when the hash has a provenance match.

**Tradeoff:** Metadata comparison becomes more useful and demonstrable, but it depends on having a reference profile from registration.

**Simpler alternative considered:** Keep metadata analysis fully standalone. Rejected because valid images with missing EXIF can otherwise receive similar scores even when one has been recompressed or transformed.

**Heavier alternative considered:** Add full forensic image tamper analysis immediately. Rejected because that would expand scope before the core explainable pipeline is mature.

**Rationale:** Profile comparison makes metadata integrity visibly explainable while staying lightweight and macOS-friendly.

**Prototype note:** The local JSON ledger can upgrade older records with a newly captured media profile when the same file is re-registered. This is a demo convenience for the local ledger only; true blockchain records remain append-only/immutable.

## Decision 8: Separate Exact Provenance From Selected Reference Comparison

**Choice:** Add an explicit reference selector instead of trying to infer that an edited file came from a registered original.

**Tradeoff:** The user must select the original record, but the report becomes more honest and interpretable.

**Simpler alternative considered:** Only verify exact hashes. Rejected because it cannot demonstrate tamper analysis against a known original.

**Heavier alternative considered:** Automatic perceptual matching or image similarity search. Rejected for this phase because it adds algorithmic uncertainty and distracts from the provenance/trust pipeline.

**Rationale:** Exact hash provenance remains deterministic, while derivative/tamper comparison is presented as a separate forensic mode with explicit user intent.

## Decision 9: Keep the Pretrained AI Adapter Optional

**Choice:** Add an optional MobileNetV3 Small adapter behind `AI_ANALYZER=pretrained`, while keeping the transparent heuristic analyzer as the default.

**Tradeoff:** The default demo remains lightweight, but users must install optional dependencies to exercise pretrained inference.

**Simpler alternative considered:** Keep only the heuristic baseline. Rejected because the research positioning benefits from a concrete pretrained-model integration point.

**Heavier alternative considered:** Install PyTorch/Torchvision by default or add a dedicated deepfake model immediately. Rejected because that increases disk usage, setup time, and fragility before evaluation design is mature.

**Rationale:** The project gains a credible pretrained-model path without violating the macOS/lightweight prototype constraint.

## Decision 10: Use `blo` for Web3 Identicons, Not a Wallet Stack

**Choice:** Use the small `blo` Ethereum identicon library in the browser to render hash-derived record icons.

**Tradeoff:** This is visual provenance affordance, not wallet connectivity.

**Simpler alternative considered:** Plain hashes only. Rejected because long hashes are hard to visually distinguish in demos.

**Heavier alternative considered:** Reown AppKit or a wallet modal. Rejected for this phase because wallet onboarding does not improve the local forensic verification pipeline.

**Rationale:** Identicons make provenance records feel more web3-native while preserving the app's research focus.

## Decision 11: Add a Repeatable Evaluation Harness

**Choice:** Add `scripts/run_evaluation.py` to run fixed fixture cases and write Markdown/JSON reports.

**Tradeoff:** The current fixture set is small, but it is explicit and repeatable.

**Simpler alternative considered:** Manual UI-only testing. Rejected because it does not produce report-ready evidence.

**Heavier alternative considered:** Full benchmark dataset ingestion. Rejected because it would create scope and storage pressure before the project needs a large empirical study.

**Rationale:** A small evaluation harness improves academic credibility and creates a place to grow metrics incrementally.

## Decision 12: Move to a No-Scroll Marketplace-Style Desktop UI

**Choice:** Redesign the interface as a single-screen forensic workspace with controls on the left, evidence in the center, and provenance records on the right.

**Tradeoff:** The UI shows less prose at once, but it communicates hierarchy more quickly through compact cards, score tokens, identicons, and structured evidence rows.

**Simpler alternative considered:** Keep the previous stacked document-like interface. Rejected because the system had grown beyond a simple linear report and needed stronger information architecture.

**Heavier alternative considered:** Add a full React design system or clone a marketplace UI. Rejected because the current Flask prototype should remain lightweight and research-focused.

**Rationale:** The marketplace-inspired layout makes registered media feel like inspectable provenance assets while preserving the lab's verification workflow.

## Decision 13: Remove NeoPOP Treatment and Redundant Pipeline Chrome

**Choice:** Return to the cleaner light interface and remove the left-side static pipeline step list.

**Tradeoff:** The interface has less decorative personality, but it is calmer and gives more attention to the actual verification controls, report, and provenance records.

**Rejected alternative:** Keep NeoPOP-inspired styling. Rejected because the requested design system was no longer desired and the stronger visual treatment was not improving research clarity.

**Rejected alternative:** Keep the pipeline steps as static orientation. Rejected because the report cards already expose the verification layers with status, score, and rationale.

**Rationale:** The UI should keep only elements that actively support the task: upload/register/verify, selected reference, evidence report, and provenance explorer.

## Decision 14: Add Minimal Hardhat/Ganache Tooling

**Choice:** Add a small Hardhat config and deploy script for `MediaProvenance.sol`, targeting Ganache by default.

**Tradeoff:** The default Python app still uses the local research ledger for frictionless demos, but the Solidity contract now has a repeatable local-chain deployment path.

**Rejected alternative:** Make Ganache mandatory for every app run. Rejected because the prototype should remain easy to demonstrate without running multiple services.

**Rationale:** This completes the blockchain technology constraint while preserving the project’s educational, local-first workflow.

## Decision 15: Expand Evaluation Metrics and Required Cases

**Choice:** Add fixture cases for a deepfake/synthetic proxy and an unknown unregistered image, then report AI classification metrics, system timing metrics, and framework-level consistency rates.

**Tradeoff:** The fixture dataset is still intentionally small and synthetic, so the metrics demonstrate evaluation structure rather than benchmark-grade model validity.

**Rationale:** The north-star evaluation section asks for more than pass/fail tests. Explicit metrics make the framework easier to discuss academically without overstating AI accuracy.
