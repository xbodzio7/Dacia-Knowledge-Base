# Spring MY25 Stock Price List — Retrospective Source Audit

**Source code:** `src_pl_spring_price_my25_stock_20260708`  
**Document:** `DACIA SPRING cennik MY25 stock`  
**Document date:** 2026-07-08  
**Registered SHA-256:** `809d24ec3710aac02b3f3a2f33e1872689430a1d6887f387936a5ac3ff343ae0`  
**Coverage state:** `partial_review`  
**Audit opened:** 2026-08-02

## Confirmed charging-table evidence

The rendered table section `ŁADOWANIE AKUMULATORA` explicitly states:

| Item | Expression 70 | Extreme 100 |
|---|---:|---:|
| Przewód ładowania z gniazdka domowego FlexiCharger | 1500 PLN | 1500 PLN |
| Przewód ładowania typu 2 do terminali typu Wallbox i terminali publicznych | standard | standard |
| Gniazdo DC (40 kW) do szybkiego ładowania | 2750 PLN | package/standard marker `P` |
| adapter do ładowania dwukierunkowego V2L | no Expression marker | package/standard marker `P` |

## Confirmed prior omission

The previous Spring charging-cable evidence matrix left `Expression Electric 70` home-cable availability unresolved. That conclusion resulted from using saved-configuration PDFs without reconciling the complete price-list option matrix.

The price-list table is explicit evidence that FlexiCharger is an optional 1500 PLN item for Expression 70. The saved Expression configuration remains valid evidence only for the selected standard Type 2 cable and does not contradict the unselected FlexiCharger option.

## Required corrective migration

A bounded migration must add the existing `domestic_socket_charging_cable` commercial mapping for `spring_expression_electric70_automatic` as:

- availability: `optional`;
- price: `1500`;
- currency: `PLN`;
- source: `src_pl_spring_price_my25_stock_20260708`;
- applicability must remain bounded to the exact Spring Expression 70 state supported by the table and project model-year policy.

## Remaining audit boundary

This artifact does not close complete assimilation of the price list. A full page-by-page audit is still required because the exact PDF bytes could not be rendered in the current connector session. All other tables, footnotes, symbols and applicability columns remain unaudited in this artifact.

The source must remain `partial_review` until a complete page inventory and fact classification are committed.
