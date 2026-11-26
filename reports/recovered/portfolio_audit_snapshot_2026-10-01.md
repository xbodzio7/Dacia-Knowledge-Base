# Dacia Knowledge Base — Portfolio audit snapshot

Snapshot date: 2026-10-01

## Verified repository-level findings

- Active configurations: 94
- Model families: 6
- Source documents/records: 108
- Explicit source-to-configuration relationships: 402
- Configurations without source links: 0

## Model-family snapshot

| Model | Configurations | Versions | Recorded price range | Sources |
|---|---:|---:|---:|---:|
| Sandero | 9 | 3 | 63,900–90,200 PLN | 18 |
| Sandero Stepway | 10 | 3 | 71,700–96,800 PLN | 22 |
| Jogger | 22 | 4 | 77,900–118,050 PLN | 26 |
| Duster | 30 | 5 | 82,000–126,100 PLN | 25 |
| Bigster | 20 | 4 | 101,400–137,600 PLN | 17 |
| Spring | 3 | 3 | 73,500–85,900 PLN | 7 |

## Interpretation / boundary

This snapshot verifies the active configuration portfolio, recorded catalogue prices, and explicit source relationships. It does **not** prove completeness of all technical parameters or equipment for every configuration. The repository explicitly reports that unknown values remain `not_stated`; this summary does not infer values, generate recommendations, or establish a model-wide completeness percentage.

The generated model-family comparison matrix is an older snapshot (2026-08-09) and contains 84 configurations, so it must not be treated as current coverage for the 94-configuration portfolio.

## Validation

`python tools/dkb.py project-state --check` passed: 1,950 tests recorded by project state; master table contains 21,560 rows. This is a project-state check, not a fresh execution of all 1,950 tests.