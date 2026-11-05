# Bigster MY26 commercial option/package price reconciliation — 2026-10-01 to 2026-11-02

- New commercial items: **2**
- New dated configuration mappings: **172** (86 per source date)
- Existing rows overwritten: **0**
- Duplicate natural keys: **0**

| Item | 2026-10-01 | 2026-11-02 |
|---|---:|---:|
| Metallic paint | 3000 PLN | 3100 PLN |
| Two-tone body | 1400 PLN | 1500 PLN |
| 19-inch wheels | 1200 PLN | 1200 PLN |
| Panoramic roof | 4300 PLN | 4300 PLN |
| Powered tailgate | 1300 PLN | 1300 PLN |
| Media Nav Live | 2400 PLN | 2400 PLN |
| EASY (P1) | 2700 PLN | 2700 PLN |
| PARKING (P2) | 2200 PLN | 2200 PLN |
| WINTER (P3) | 1200 PLN | 1200 PLN |
| WINTER PLUS (P4) | 2300 PLN | 2300 PLN |
| Space-saver spare wheel (Hybrid 155) | 800 PLN | 900 PLN |

Spare-wheel rows outside Hybrid 155 are `unknown` rather than `not_available`. The source qualifier does not justify projecting the price to mild hybrid-G 140 or tribrid 150. The commercial-offer loader now suppresses an older optional price when a later `unknown` or `not_available` mapping exists.

October source SHA-256 is verified against the archived PDF. November source raw bytes remain in the user's Library; no hash is asserted.
