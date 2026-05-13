# Test Samples

Use these local images to exercise the demo flow.

## 1. Authentic Reference

File: `authentic_reference.png`

Recommended flow:

1. Upload this file.
2. Click **Register**.
3. Upload the same file again.
4. Click **Verify**.

Expected behavior:

- provenance match
- high blockchain score
- visible SHA-256 hash
- final trust score lifted by registration

## 2. Edited Variant

File: `edited_variant.jpg`

Recommended flow:

1. Register `authentic_reference.png`.
2. Upload this edited variant.
3. Click **Verify** without registering it.

Expected behavior:

- provenance miss
- different SHA-256 hash
- lower final trust score
- metadata/AI signals still visible for comparison

## 3. Synthetic Stress Test

File: `synthetic_stress_test.png`

Recommended flow:

1. Upload this file.
2. Click **Verify** without registering it.

Expected behavior:

- no provenance record
- synthetic-looking visual evidence
- explainable AI baseline factors such as texture, luminance, and contrast

## 4. Deepfake Proxy

File: `deepfake_proxy.png`

Recommended flow:

1. Upload this file.
2. Click **Verify** without registering it.

Expected behavior:

- no provenance record
- suspicious AI baseline output
- low final trust score

## 5. Unknown Unregistered Image

File: `unknown_unregistered.png`

Recommended flow:

1. Upload this file.
2. Click **Verify** without registering it.

Expected behavior:

- no provenance record
- unregistered authenticity state
- low trust because provenance is absent even when visual evidence is not strongly suspicious

These are generated demo fixtures, not a real deepfake benchmark.
