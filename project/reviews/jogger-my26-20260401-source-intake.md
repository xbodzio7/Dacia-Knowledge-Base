# Jogger MY26 2026-04-01 Source Intake

## Decision status

`ACCEPTED`

The supplied document is accepted as the first authoritative Polish Jogger source.
It is an official nine-page Dacia price list for model year 2026 and contains a
price matrix, trim-equipment matrices, powertrain technical data, dimensions,
accessories and legal terms.

## Provenance

- Planned source code: `src_pl_jogger_price_my26_20260401`
- Publisher: Dacia
- Market: Poland
- Canonical document date: `2026-04-01`
- Original PDF SHA-256: `a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b`
- Pages: 9
- Expected archive path: `PDF/Cenniki/DACIA JOGGER cennik MY26 20260401.pdf`
- Machine-readable intake record: `project/sources/jogger-my26-20260401.json`

The PDF binary was supplied in the project conversation and its hash was verified.
The connected GitHub writer available for this package accepts UTF-8 text only,
so this PR does not claim that the binary has been archived in the repository.
The expected path and exact original hash are reserved for a later binary upload.

## Date resolution

The canonical date is **1 April 2026**. The page 1 footer says that the price list
is valid from `1.04.2026`, and page 9 repeats that the offer state is dated
`01.04.2026`.

A sentence on page 1 still mentions `19.12.2025`. It belongs to a carried-over
promotional paragraph and conflicts with both the page footer and the legal
section. It is therefore retained as source text but is not used as the document
date.

## Source coverage candidate

The price matrix contains four trims:

- Essential;
- Expression;
- Extreme;
- Journey.

It distinguishes five- and seven-seat cars and four powertrain/transmission
groups:

- Eco-G 120 manual;
- Eco-G 120 automatic;
- TCe 110 manual;
- Hybrid 155 automatic.

The non-empty price cells form **22 configuration candidates**:

| Group | Five seats | Seven seats | Total |
| --- | ---: | ---: | ---: |
| Eco-G 120 manual | 3 | 3 | 6 |
| Eco-G 120 automatic | 2 | 2 | 4 |
| TCe 110 manual | 3 | 3 | 6 |
| Hybrid 155 automatic | 3 | 3 | 6 |
| **Total** | **11** | **11** | **22** |

## Evidence boundaries

The next review must preserve these boundaries:

1. Five- and seven-seat vehicles are separate configuration candidates. Their
   catalogue prices, acceleration, mass and cargo observations differ.
2. Financing instalments on pages 1-2 are not catalogue prices.
3. Technical ranges on page 6 apply to powertrain/seat variants, not individual
   trims, unless the source explicitly identifies a trim.
4. The equipment matrix is primarily trim-level, but several rows are conditional
   on Hybrid 155, seat count or optional packages. Such cells must not be flattened
   into unconditional availability.
5. The accessories page is outside the first vehicle-configuration package.
6. The existing `jogger` model row is reusable; the source does not justify a
   parallel model entity.

## Next package

Proceed to **Jogger Catalogue Reporting Scope Review**. That package will decide
whether the first active entity foundation covers all 22 priced cells or a smaller
homogeneous subset, and will define how seat count is represented without changing
the meaning of `powertrain_label`.
