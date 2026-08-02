# Legacy PDF Source Audit

This directory is the durable registry for retrospective full-document audits required by `project/SOURCE_ASSIMILATION_STANDARD.md`.

A source is not considered fully assimilated merely because it is registered in `data/master/sources.csv`, hash-verified, represented by a normalized slice or previously used by a migration.

## Required artifact per source

Each audited PDF receives one Markdown or JSON artifact containing:

- source code and exact SHA-256;
- title, market, document date and source type;
- page count;
- page-by-page section inventory;
- confirmation that rendered tables, symbols, footnotes and embedded visual text were inspected;
- fact classification: already represented, newly imported, corrective migration required, deferred with reason, contradictory, superseded or out of scope;
- exact page evidence for every identified gap;
- audit completion status.

## Audit order

1. price lists and saved configurations that can change commercial-option conclusions;
2. brochures currently marked `source registration only`;
3. historical saved configurations;
4. remaining documentary sources.

## Completion rule

The legacy PDF audit milestone remains open until every active `configuration_pdf` and `brochure_pdf` row in `data/master/sources.csv` has a completed coverage artifact or an explicit `blocked` record naming the missing exact source bytes.
