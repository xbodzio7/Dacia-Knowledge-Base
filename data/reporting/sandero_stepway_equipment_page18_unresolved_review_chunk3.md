# Sandero Stepway Equipment Page 18 Unresolved Review — Chunk 3

Authored review of `residual_gap_036`. The final 17 of 97 candidates complete the Sandero Stepway page-18 equipment-matrix review. Source findings are review-only and do not approve imports.

## Summary

- candidates: 17 of 97 (chunk 3 of 3);
- visual groups: 7;
- `unresolved_signature_mismatch`: 8;
- `context_only_non_import`: 9;
- attached evidence signatures: 0;
- attached evidence records: 0.

## Source boundary

- source: `src_pl_sandero_stepway_brochure_20260202`;
- archived file: `PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf`;
- SHA-256: `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`;
- page: 18;
- columns: `essential`, `expression`, `extreme`.

The review completes the electric-parking-brake/armrest row and covers fatigue warning, automatic high-/low-beam switching, tyre-pressure monitoring, spare-wheel and repair-kit states, plus Isofix. Literal `o`, `•` and `¤` extraction markers remain unchanged.

## Candidate decisions

| # | Line | Candidate | Group | Decision | Exact text |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 133 | `8431244efd2436c8a703a3cdd629bb49e5ed83159753243a500a5ed2ac4e7139` | `electric_parking_brake_armrest` | `unresolved_signature_mismatch` | `podłokietnik ze schowkiem, 1 gniazdem 12 V               -` |
| 2 | 134 | `46f48f29804271f242894abe7cd8dbec50442d514f93134252db32aa6b72650d` | `electric_parking_brake_armrest` | `context_only_non_import` | `                                                                      skrzynia biegów` |
| 3 | 135 | `e54fccca9c474d60b69db6ceed77c157a7f98736510222266375c6cd1722ffc4` | `electric_parking_brake_armrest` | `unresolved_signature_mismatch` | `                                                                                                     •` |
| 4 | 136 | `052712a62eaa0c8dfa8ddbd8f21add56297f0b87749399e77eab0fc255901f0e` | `electric_parking_brake_armrest` | `context_only_non_import` | `i 1 gniazdem USB-C z tyłu` |
| 5 | 137 | `5e24a6906cfcfdec48736a363ac07afc45853aedb262683be2fd7d50fb62e9db` | `fatigue_and_drowsiness_warning` | `context_only_non_import` | `System ostrzegania o zmęczeniu kierowcy` |
| 6 | 138 | `25b96d7512059422bdbb6c2864babd2a15864e79d93ff521abcb41a85d23a3b4` | `fatigue_and_drowsiness_warning` | `unresolved_signature_mismatch` | `                                                         •                    •                      •` |
| 7 | 139 | `1ab0edaa284ef1490a220b6292f8bcee4c45c1d56aea78b19f9416c5777884f6` | `fatigue_and_drowsiness_warning` | `context_only_non_import` | `i wykrywania jego senności` |
| 8 | 140 | `cc2194fb9c388a61819b03a2fba0b93e0c4284b0e39d414c065663fc87f459e0` | `automatic_high_low_beam` | `context_only_non_import` | `Funkcja automatycznego przełączania świateł` |
| 9 | 141 | `f23f2af0a5e2a787e2fdaa0094f0f27221032887c7051e0ac9b132d9e096df3a` | `automatic_high_low_beam` | `unresolved_signature_mismatch` | `                                                         -                    -                      ¤` |
| 10 | 142 | `f36163fead720b1ae467992f7205b5cb9220f29bdcd0357aab29430d1ce5df7f` | `automatic_high_low_beam` | `context_only_non_import` | `drogowych na światła mijania` |
| 11 | 143 | `eef6a8b79740418105a4d56081269a100dc17efbb548c07baee6eaa5c7288900` | `tyre_pressure_monitoring` | `unresolved_signature_mismatch` | `System kontroli ciśnienia w oponach                      •                    •                      •` |
| 12 | 145 | `b870804718ec47a379f06a5fd4c0dc3e39007f5eaf4d4cd0a908cc4438faf6e9` | `spare_wheel_and_jack` | `context_only_non_import` | `Koło zapasowe + podnośnik (z wyjątkiem wersji` |
| 13 | 146 | `7f999d692693be8c10a5686b3edbbf86a7677597860a6dd5d69cdc3aa98a7816` | `spare_wheel_and_jack` | `unresolved_signature_mismatch` | `                                                         o                   o                       o` |
| 14 | 148 | `df7c9b8c11e372cf8a6266f3cdd07bb41fcd75369054d01dce0d15154c3861a2` | `tyre_repair_kit` | `unresolved_signature_mismatch` | `Zestaw do naprawy opon                                   •                    •                      •` |
| 15 | 150 | `864171fa949e517fcf2241a1a04e2e4b64fa43600241b31c658c0df10cbe8484` | `isofix_rear_outer` | `context_only_non_import` | `System mocowania fotelików dziecięcych Isofix` |
| 16 | 151 | `8bac93123f745c6d791c9b60c87ea2cb74e8a627801d2e99dec57f0ca9be7f9b` | `isofix_rear_outer` | `unresolved_signature_mismatch` | `                                                         •                    •                      •` |
| 17 | 152 | `19387ce0ab1cad66d6d18c9a07959fc0e07f62bbd5c53275fe85c72a4152ef28` | `isofix_rear_outer` | `context_only_non_import` | `na tylnych skrajnych siedzeniach` |

## Decision boundary

- The parking-brake/armrest row is completed only from candidates assigned to chunks 2 and 3.
- Complete and aligned state fragments remain unresolved because no matching evidence signature is attached.
- Wrapped labels and continuations remain non-importable context.
- Literal `o` is retained rather than normalized to another symbol.
- The incomplete spare-wheel exception is not reconstructed from outside the candidate package.
- No file under `data/master` or `data/imports` changes.
