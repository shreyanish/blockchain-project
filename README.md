# Authenticity Verification Lab

Research-oriented prototype for multi-layer media authenticity verification using SHA-256 hashing, provenance registration, metadata analysis, lightweight authenticity analysis, and explainable trust scoring.

This project follows [PROJECT_NORTH_STAR.md](PROJECT_NORTH_STAR.md): it is a transparent digital forensics laboratory, not a generic deepfake detector.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m authenticity_lab.web.app
```

Open `http://127.0.0.1:5000`.

The default AI mode is the transparent heuristic baseline:

```bash
AI_ANALYZER=heuristic python3 -m authenticity_lab.web.app
```

An optional pretrained MobileNetV3 adapter is available, but it requires heavier dependencies:

```bash
pip install -r optional-requirements.txt
AI_ANALYZER=pretrained python3 -m authenticity_lab.web.app
```

## Current Prototype Path

1. Upload an image.
2. Generate a SHA-256 hash.
3. Register or verify hash-only provenance.
4. Optionally compare an upload against a selected registered original.
5. Inspect metadata consistency signals and reference-profile drift.
6. Run a lightweight explainable authenticity baseline.
7. Combine evidence into a weighted trust score.

## Demo Flow

1. Register `samples/authentic_reference.png`.
2. Refresh the provenance explorer if needed.
3. Select the registered reference in **Compare against registered original**.
4. Upload `samples/edited_variant.jpg`.
5. Click **Verify**.

Expected behavior: exact provenance should miss because the edited file has a different hash, while selected-reference comparison should show a derivative check and metadata drift.

## Blockchain Notes

The default app uses a local research ledger in `data/provenance_records.json` so the demo works without external services. The Solidity contract in [contracts/MediaProvenance.sol](contracts/MediaProvenance.sol) and the Web3 adapter in [authenticity_lab/adapters/web3_gateway.py](authenticity_lab/adapters/web3_gateway.py) provide the intended Ganache integration point.

## Research Caveat

The current AI layer is an explainable baseline adapter, not a production deepfake detector. It exists to keep the verification pipeline demoable and transparent while leaving a clean replacement point for a lightweight pretrained model.

The optional pretrained mode uses MobileNetV3 Small as visual-distribution evidence. It is still not a dedicated deepfake detector, and the UI exposes that limitation.

## Tests

The deterministic core tests use the Python standard library:

```bash
python3 -m unittest discover tests
```

## Evaluation

Generate the current fixture report:

```bash
python3 scripts/run_evaluation.py
```

Outputs:

- `evaluation/latest_report.md`
- `evaluation/latest_report.json`
- `evaluation/heuristic_report.md`
- `evaluation/heuristic_report.json`

Run the same harness with the optional pretrained adapter:

```bash
python3 scripts/run_evaluation.py --ai-mode pretrained
```
