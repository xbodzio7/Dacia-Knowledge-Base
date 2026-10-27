# Hybrid 155 technical and equipment materialization — 2026-09-19

## Scope

Materialize the source-explicit Hybrid 155 technical table and equipment matrix from the official Polish Dacia Sandero/Sandero Stepway price list effective 11.08.2026 for the four configurations already added by the preceding master-reconciliation package.

## Configurations

- Sandero Expression Hybrid 155 automatic — 84,600 PLN
- Sandero Journey Hybrid 155 automatic — 90,200 PLN
- Sandero Stepway Expression Hybrid 155 automatic — 90,700 PLN
- Sandero Stepway Extreme Hybrid 155 automatic — 96,800 PLN

## Technical observations

The source explicitly states: 1,789 cm³, 4 cylinders / 16 valves, Euro 6e BIS, automatic Multimode transmission, 80 kW petrol engine, 172 Nm at 3,000 rpm, E-Motor 36 kW, HSG 15 kW, 180 km/h, 50 l fuel tank and 328 dm³ VDA boot capacity. WLTP combined consumption is 4.2 l/100 km for Sandero and 4.4 l/100 km for Sandero Stepway; CO₂ is 96 g/km and 100 g/km respectively.

## Equipment

The 11.08.2026 equipment matrix is grade-based and is materialized only for the four exact Hybrid 155 combinations that are explicitly present in the same price matrix. The import preserves standard, optional/package-item and unavailable states represented by the canonical availability model.

Canonical attribute mapping uses the existing verified Sandero/Stepway catalogue vocabulary; this is a code-mapping operation, not a new inference about applicability.

## Boundaries

- Historical 03.07.2026 observations remain untouched.
- No colour compatibility is inferred.
- No package membership is changed.
- No other Dacia model receives these observations.
- No Hybrid 155 values are copied from Duster, Jogger or another body style.

## Source

Official Dacia Poland price list effective 11.08.2026; supplied PDF SHA-256:
`c220ab0ff1df848b72121c6ebe0f05fb245bb9b70052a10dbd48068709b2034a`.
