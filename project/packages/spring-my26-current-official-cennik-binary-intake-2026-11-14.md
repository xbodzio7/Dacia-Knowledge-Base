# Spring MY26 Current Official Cennik Binary Intake

**Package:** `spring_my26_current_official_cennik_binary_intake_20261114_001`  
**PR:** #816  
**Source URL:** https://cdn.group.renault.com/dac/pl/pdf/cenniki/spring-price.pdf.asset.pdf/2e0588c888.pdf  
**Expected document identity:** `S2E_PY26_06.02.2026`, MY26, effective 2026-02-06

## Why a separate capture is required

The owner-supplied Library file `2e0588c888.pdf` is MY25/effective 2026-03-03 (recorded source SHA-256 `295deb2f8136c2f0ff090c88183579a135e7220a38d628973667a8824c0db5d0`). The same CDN URL currently returns a different PDF identifying MY26/effective 2026-02-06. URL equality is not binary identity; preserve both content versions separately.

## Workflow change

Update the existing `.github/workflows/source-assimilation-spring-audit.yml` workflow to:
1. Download the live official CDN response without modifying it.
2. Verify exactly six pages and first-page markers: `Ceny katalogowe`, `ROCZNIK 2026`, `Cennik obowiązuje od 06.02.2026`, and the three price cells 73,500 / 81,500 / 85,900 PLN.
3. Compute SHA-256, file size, PDF metadata, full extracted text and rendered page images.
4. Upload the audit bundle for seven days.
5. Push the original PDF, SHA-256 file and capture manifest to `data/spring-my26-cennik-assimilation-20261114-001`, never to `main`.

The workflow has `contents: write` only so it can create that dedicated source branch; the capture step is fixed to the official Dacia Polish cennik CDN path and validates the expected document markers before any push.

## Exact MY26 price candidates

| Grade | Powertrain | Price |
|---|---|---:|
| Essential | Electric 70 | 73,500 PLN |
| Expression | Electric 70 | 81,500 PLN |
| Extreme | Electric 100 | 85,900 PLN |

The source page heading/footer call these catalogue prices while the table row labels say `Cena promocyjna`. Both printed contexts are retained for the next data-assimilation package.

## Acceptance criteria

- The workflow runs successfully on the merge push to `main`.
- The downloaded PDF is six pages and passes every expected marker.
- The manifest and SHA-256 are recorded from the exact downloaded bytes.
- The original PDF is committed to the dedicated source branch with no mutation of the MY25 source record or file.
- The next package imports the three MY26 prices and cennik commercial matrix only after verifying the captured PDF bytes.


## Capture result and follow-up

PR #816 merged the guarded capture workflow. The first direct download run (43534970475) retrieved a 1.35 MB PDF but the extracted first page did not contain ROCZNIK 2026. The workflow stopped before hashing or committing a source binary. No MY26 file or price row was added.

PR #817 changes the workflow to retain a diagnostic artifact even when the identity check fails. It records the first-page text, PDF page count, size, SHA-256 and whether the bytes match the registered MY25 hash. The binary-commit step remains gated on positive MY26 verification.
