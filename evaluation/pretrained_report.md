# Evaluation Report

AI mode: `pretrained`
Cases passed: 3 / 3

| Case | File | Expected | Observed | Scores | Pass |
| --- | --- | --- | --- | --- | --- |
| registered-original | `samples/authentic_reference.png` | blockchain=VERIFIED, metadata=CONSISTENT | blockchain=VERIFIED, reference=EXACT_MATCH, metadata=CONSISTENT, ai=UNCERTAIN, trust=HIGH_TRUST | blockchain=100%, reference=100%, metadata=88%, ai=66%, trust=84% | PASS |
| edited-reference-comparison | `samples/edited_variant.jpg` | blockchain=UNREGISTERED, reference=DERIVATIVE_CHECK, metadata=PARTIAL | blockchain=UNREGISTERED, reference=DERIVATIVE_CHECK, metadata=PARTIAL, ai=UNCERTAIN, trust=LOW_TRUST | blockchain=0%, reference=65%, metadata=67%, ai=63%, trust=39% | PASS |
| synthetic-unknown | `samples/synthetic_stress_test.png` | blockchain=UNREGISTERED | blockchain=UNREGISTERED, metadata=CONSISTENT, ai=UNCERTAIN, trust=LOW_TRUST | blockchain=0%, metadata=75%, ai=73%, trust=44% | PASS |

## AI Layer Caveat

The AI layer is an assistive evidence source. It should be interpreted alongside provenance and metadata, not as a standalone real/fake oracle.
