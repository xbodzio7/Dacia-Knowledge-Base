# Spring MY26 price-list source assimilation review — 2026-11-14

**Review status:** complete  
**Registration:** proposed in branch `data/spring-my26-source-registration-20261114-001`  
**Scope:** source identity, all seven rendered pages, page-level evidence and explicit non-import boundaries. This is not a master-data import.

## Verified source identity

- Source code: `src_pl_spring_price_my26_20260206`
- Market/model year: Poland / MY26
- Effective date: 2026-02-06
- Host: PGD dealer website; Dacia-branded distribution copy, not verified as a live manufacturer CDN binary
- URL: https://www.dacia.pgd.pl/SiteData/Dacia/images/NowaStrona/Cenniki/2026/kwiecien/Spring.pdf
- Repository binary: `PDF/Cenniki/DACIA SPRING cennik MY26 20260206.pdf`
- Size: 1,418,626 bytes; 7 pages; PDF 1.7
- SHA-256: `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`
- Registered MY25 SHA-256: `295deb2f8136c2f0ff090c88183579a135e7220a38d628973667a8824c0db5d0` — different binary.

Two tested live Dacia CDN assets returned the registered MY25 binary. The MY26 file is therefore recorded with its actual PGD-hosted distribution provenance; it is not represented as the live manufacturer CDN response.

## Page-by-page review

| Page | Coverage and material findings | Import decision |
|---|---|---|
| 1 | Price matrix: Essential Electric 70 — 73,500 PLN; Expression Electric 70 — 81,500 PLN; Extreme Electric 100 — 85,900 PLN. Header/footer call them catalogue prices, but matrix rows say “Cena promocyjna”. Effective 06.02.2026; ROCZNIK 2026. | No price import in registration package; preserve both labels. |
| 2 | Narrative overview. It states 48 kW / 65 KM and 26.8 kWh. | Conflicts with page 5; do not import these values. |
| 3 | Exterior/interior/comfort/driving equipment matrix for Essential, Expression and Extreme. Khaki Lichen paint: 2,300 PLN across grades. Front sensors are optional on Extreme; reversing camera optional on Expression and standard on Extreme. | No equipment or commercial mappings imported. |
| 4 | Safety, multimedia, charging and packages. FlexiCharger: 1,500 PLN across grades. DC 40 kW socket: 2,750 PLN Expression, optional Extreme. TECHNO: 3,500 PLN Expression; CITY: 1,800 PLN Extreme; POWER: 3,000 PLN Extreme. Legend distinguishes unavailable, standard and optional. | No equipment, option or package mappings imported. |
| 5 | Technical table: Electric 70 — 52 kW / 70 hp, 24.3 kWh; Electric 100 — 75 kW / 100 hp, 24.3 kWh. Both: 4 seats, 354 V, 204 kg battery, 137 Nm. WLTP range and wheel/mass footnotes are grade-bounded. | No technical import pending conflict-aware reconciliation. |
| 6 | Rendered dimension diagram reviewed; includes exterior, wheelbase, overhang and interior measurements. | No dimensions imported; semantic/measurement-basis mapping deferred. |
| 7 | Legal, VAT, promotion and financing terms; no additional configuration matrix. | No promotional/financing claim imported. |

## Preserved source conflict

Page 2 narrative says **48 kW / 65 KM and 26.8 kWh**. Page 5 technical table says **52 kW / 70 hp and 24.3 kWh** for Electric 70, and **75 kW / 100 hp and 24.3 kWh** for Electric 100. These are contradictory source contexts. Neither value is silently selected or migrated by this registration package.

## Registration

- `data/master/sources.csv`: row 129
- `data/master/source_models.csv`: row 38, `spring` / `price_list_for`
- Full structured evidence: `data/reporting/spring_my26_price_list_source_assimilation_review_20261114.json`

## Explicit boundaries

- MY26 remains separate from the registered MY25 stock cennik.
- PGD hosting provenance remains explicit; no claim that the live Dacia CDN serves this MY26 binary.
- Catalogue-price versus “Cena promocyjna” ambiguity remains preserved.
- Page 2/page 5 technical conflict remains unresolved.
- No master-data price, equipment, option, package, technical or dimension observations are imported.
- Configurator data must not override this dated source.
