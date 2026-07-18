# Jogger Injection-Type Import Selection

## Decision status

`SELECTED`

The deferred Jogger page-6 injection evidence can be imported without adding a
new attribute, relation, enum value or range model. The canonical
`injection_type` attribute is active, configuration observations already support
fuel context, and all source terms have exact active targets in
`enums/injection_types.csv`.

## Source evidence and controlled mapping

| Source group | Source text | Fuel context | Canonical value | Configurations | Observations |
| --- | --- | --- | --- | ---: | ---: |
| Eco-G 120 manual | `benzyna bezpośredni` | `petrol` | `direct_injection` | 6 | 6 |
| Eco-G 120 manual | `LPG pośredni` | `lpg` | `port_injection` | 6 | 6 |
| Eco-G 120 automatic | `benzyna bezpośredni` | `petrol` | `direct_injection` | 4 | 4 |
| Eco-G 120 automatic | `LPG pośredni` | `lpg` | `port_injection` | 4 | 4 |
| TCe 110 manual | `bezpośredni` | none | `direct_injection` | 6 | 6 |
| Hybrid 155 automatic | `wielopunktowy` | none | `multi_point_injection` | 6 | 6 |
| **Total** | — | — | — | **22** | **32** |

The existing enum descriptions preserve the source distinction:

- `direct_injection`: fuel injected directly into the combustion chamber;
- `port_injection`: fuel injected into the intake port;
- `multi_point_injection`: fuel injected into multiple intake ports.

No new interpretation is required. The Eco-G source explicitly separates petrol
and LPG with a slash, so the import will retain two observations per
configuration rather than selecting one generic injection type.

## Selected implementation boundary

**Selected Jogger Injection-Type Import** will:

- add one versioned declarative `injection_type` specification;
- materialize 32 observations dated `2026-04-01` with IDs 1037–1068;
- verify the repository-local Jogger PDF and page-6 `SILNIKI` source text;
- lock all four group mappings and both Eco-G fuel contexts with regression
  tests;
- preserve the completed 312-value technical denominator unchanged.

The implementation will not modify engine entities, model-engine associations,
configuration identities or the injection enum dictionary.

## Candidates not selected in this package

The remaining deferred evidence still needs separate decisions because it
cannot be represented exactly by the current scalar observation contract or
existing master associations:

- WLTP fuel-consumption, CO2 and payload ranges;
- minimum-qualified kerb weights;
- the unassigned Hybrid 155 acceleration range;
- two cargo measurements with different height boundaries;
- the LPG total/filling-capacity pair;
- Hybrid system power and battery semantics;
- gearbox type/count associations;
- Eco-G and TCe engine-speed ranges.

These items remain deferred evidence, not missing or zero values.

## Selection rationale

Injection type is the highest-confidence bounded candidate because it covers all
22 configurations, adds 32 exact observations, uses only existing canonical
semantics and exercises the already-approved observation-level fuel context. It
therefore advances Jogger coverage without crossing an architecture boundary.

## Next package

After the injection import, **Jogger Remaining Deferred Technical Evidence
Review** will reassess the still-deferred ranges, qualifiers, cargo definitions,
LPG capacities, hybrid battery/system values and gearbox evidence.
