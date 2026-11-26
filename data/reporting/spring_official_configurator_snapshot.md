# Spring Official Configurator Snapshot

Date: 2026-07-31

Status: **complete**

## Registered snapshot

The dated normalized snapshot is stored at `project/sources/dacia-pl-spring-configurator-20260731.json` with SHA-256 `9b90aa2a2f81f1bc81509f04d3705887e8bd74af595f69a3e830c85c35b0601b`.

It records three exact official grade/powertrain states:

- Essential — electric 70 — exact configurator price 73,500 PLN;
- Expression — electric 70 — grade and powertrain accepted, catalogue price unresolved;
- Extreme — electric 100 — exact comparison price 85,900 PLN.

## Conflict preserved

The combined version page repeats the Essential starting price of 73,500 PLN in the Expression and Extreme sections. That repeated value is not treated as a grade-specific price. The independently visible Essential configurator and Extreme comparison prices remain the only accepted catalogue prices in this snapshot.

## Boundaries

This package registers dated evidence only. It imports no configuration, price, equipment, option, package or technical observation, creates no Cargo state and does not supersede the immutable Spring brochure or MY25 stock price list.

Decision: `REGISTER_SPRING_OFFICIAL_CONFIGURATOR_SNAPSHOT`.

## Next package

**Spring Source-Backed Data Import Review** — determine which exact configurations, prices, equipment and technical values are import-ready across the two PDFs and this dynamic snapshot while preserving the unresolved Expression price.
