# Jogger Source Binary Archival

## Decision status

`COMPLETE`

The authoritative Polish Dacia Jogger MY26 price-list binary has been archived
in the repository and verified byte for byte against the source file supplied
by the owner.

## Archived source

- source code: `src_pl_jogger_price_my26_20260401`
- repository path: `PDF/Cenniki/DACIA JOGGER cennik MY26 20260401.pdf`
- market: `PL`
- document date: `2026-04-01`
- pages: `9`
- size: `2,031,453` bytes
- SHA-256: `a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b`

The archived bytes have the same size and SHA-256 as the original owner upload.
The smaller processed derivative available during intake was not used.

## Retrieval provenance

The exact binary was recovered from a raw Internet Archive Wayback snapshot of
an official Dacia/Renault CDN asset:

- snapshot timestamp: `20260519160349`
- original asset: `https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/0913ceb856.pdf`
- retrieval mode: raw `id_` snapshot

The current public CDN routes are mutable and later served a different
seven-page document. They are therefore not treated as the archived binary's
byte source. The raw historical snapshot is retained only as retrieval
provenance; the repository PDF and its registered SHA-256 remain the controlled
source of truth.

## Verification result

The archival workflow accepted a candidate only when both conditions matched:

1. exact size `2,031,453` bytes;
2. exact SHA-256
   `a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b`.

After verification it committed the PDF and removed all temporary transport
fragments and the one-shot workflow. No master-data rows, counters or catalogue
semantics changed in this package.

## Consequence

The registered Jogger source is now fully repository-local. Shared source-file
verification, declarative import checks and evidence-preserving page review can
operate without depending on the conversation upload or a mutable public URL.

The next bounded package is **Jogger Technical Denominator Review**. It will
classify the page-6 table into exact powertrain-wide values, explicit five- and
seven-seat observations and source ranges before any technical scalar import.
