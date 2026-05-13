# Evaluation Report

AI mode: `heuristic`
Cases passed: 5 / 5

## Metrics

| Group | Metric | Value |
| --- | --- | ---: |
| ai | accuracy | 60.0% |
| ai | precision | 100.0% |
| ai | recall | 33.3% |
| ai | f1_score | 50.0% |
| ai | true_positive | 1 |
| ai | true_negative | 2 |
| ai | false_positive | 0 |
| ai | false_negative | 2 |
| system | mean_hash_generation_ms | 0.021 ms |
| system | mean_blockchain_lookup_ms | 0.067 ms |
| system | mean_metadata_analysis_ms | 1.936 ms |
| system | mean_ai_analysis_ms | 6.072 ms |
| system | mean_trust_scoring_ms | 0.007 ms |
| system | mean_total_verification_ms | 8.102 ms |
| framework | trust_score_consistency | 100.0% |
| framework | provenance_verification_success_rate | 100.0% |
| framework | tamper_detection_rate | 100.0% |

## Cases

| Case | File | Expected | Observed | Scores | Latency | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| registered-original | `samples/authentic_reference.png` | blockchain=VERIFIED, metadata=CONSISTENT, trust=HIGH_TRUST | blockchain=VERIFIED, reference=EXACT_MATCH, metadata=CONSISTENT, ai=UNCERTAIN, trust=HIGH_TRUST | blockchain=100%, reference=100%, metadata=88%, ai=66%, trust=84% | 9.350 ms | PASS |
| edited-reference-comparison | `samples/edited_variant.jpg` | blockchain=UNREGISTERED, reference=DERIVATIVE_CHECK, metadata=PARTIAL, trust=LOW_TRUST | blockchain=UNREGISTERED, reference=DERIVATIVE_CHECK, metadata=PARTIAL, ai=UNCERTAIN, trust=LOW_TRUST | blockchain=0%, reference=65%, metadata=67%, ai=63%, trust=39% | 7.106 ms | PASS |
| deepfake-synthetic-proxy | `samples/deepfake_proxy.png` | blockchain=UNREGISTERED, ai=SUSPICIOUS, trust=LOW_TRUST | blockchain=UNREGISTERED, metadata=CONSISTENT, ai=SUSPICIOUS, trust=LOW_TRUST | blockchain=0%, metadata=75%, ai=40%, trust=31% | 7.752 ms | PASS |
| unknown-unregistered-image | `samples/unknown_unregistered.png` | blockchain=UNREGISTERED, trust=LOW_TRUST | blockchain=UNREGISTERED, metadata=CONSISTENT, ai=UNCERTAIN, trust=LOW_TRUST | blockchain=0%, metadata=75%, ai=48%, trust=34% | 7.875 ms | PASS |
| synthetic-stress-unknown | `samples/synthetic_stress_test.png` | blockchain=UNREGISTERED, trust=LOW_TRUST | blockchain=UNREGISTERED, metadata=CONSISTENT, ai=UNCERTAIN, trust=LOW_TRUST | blockchain=0%, metadata=75%, ai=73%, trust=44% | 8.426 ms | PASS |

## AI Layer Caveat

The AI layer is an assistive evidence source. It should be interpreted alongside provenance and metadata, not as a standalone real/fake oracle.
