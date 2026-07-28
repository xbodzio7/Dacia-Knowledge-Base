# Bigster Technical Page 20 Ambiguity Review

Date: 2026-07-28
Status: complete

## Purpose

This package performs the first authored review from the deterministic residual-gap queue. It reviews every candidate in `residual_gap_001` against the exact archived page layout and only the evidence signatures preserved on that candidate.

## Source boundary

- source: `src_pl_bigster_brochure_20251210`;
- archived file: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`;
- verified SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`;
- reviewed page: 20;
- domain: `technical_tables`;
- input status: `ambiguous`;
- candidates: 23.

The visual table has four powertrain columns: mild hybrid-G 140, mild hybrid 140, hybrid-G 150 4x4 and hybrid 155. Adjacent extracted lines are used only to understand row labels and column layout; evidence is selected only when it is attached to the exact candidate under review.

## Outcome

| Authored decision | Candidates |
| --- | ---: |
| Covered by selected evidence | 9 |
| Partially covered | 3 |
| Context-only non-import | 7 |
| Deferred source conflict | 2 |
| Unresolved signature mismatch | 2 |
| **Total** | **23** |

The review selects 36 evidence signatures containing 143 exact records. Candidate IDs, source text, line spans, signatures and record provenance are copied unchanged to the deterministic JSON artifact.

## Material findings

- The steering row selects only `steering_type`; turning circle and chassis signatures from neighbouring rows are rejected.
- The two rear-brake specifications and four powertrain tyre specifications are separated using the visual column layout.
- Maximum kerb weight, gross train weight and unbraked trailer weight are confirmed against exact existing records.
- The second `Dopuszczalna masa całkowita` row is gross vehicle weight, not gross train weight. Its attached signatures are therefore rejected.
- `Maksymalna masa przyczepy z hamulcem` is not supported by attached unbraked-trailer signatures. Cross-attribute substitution is forbidden.
- Hybrid-G 150 4x4 cargo values `444`, `1712`, `556` and `1856` remain under the existing documented deferral because the brochure contradicts the equipment evidence on tyre-repair-kit presence. This package does not reopen or override that decision.
- Cargo measurement basis, folded-seat state and repair-kit/spare-wheel phrases are qualifiers, not independent scalar observations.

## Delivered command

```bash
python tools/dkb.py bigster-technical-page20-ambiguity-review
python tools/dkb.py bigster-technical-page20-ambiguity-review --verify
```

## Artifacts

- `data/reporting/bigster_technical_page20_ambiguity_review.json` — full candidate decisions with selected exact signatures and records;
- `data/reporting/bigster_technical_page20_ambiguity_review.md` — deterministic human-readable summary.

## Safety boundary

This package changes no file in `data/master`, creates or modifies no approved specification in `data/imports`, performs no automatic promotion and introduces no new domain or architecture decision.

## Next package

**Jogger Technical Page 19 Ambiguity Review** will review 16 ambiguous technical candidates and their 34 preserved evidence signatures under the same no-import boundary.
