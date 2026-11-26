# Verified PDF Candidate Ledger Review

Date: 2026-07-28  
Status: complete

## Coverage

| Measure | Result |
| --- | ---: |
| Registered sources | 5 |
| Declared pages | 114 |
| Candidate spans | 4,256 |
| Evidence decision groups | 30 |
| Exact-text anchors | 60 |
| Unassigned candidates | 0 |
| Duplicate assignments | 0 |

Every candidate from the canonical ledger is assigned exactly once. Group decisions are review-only and do not approve configuration, attribute, unit or import-spec mappings.

## Decision totals

| Decision | Groups | Candidates |
| --- | ---: | ---: |
| `descriptive_non_import` | 5 | 1,259 |
| `explicit_non_import` | 5 | 83 |
| `requires_entity_mapping` | 5 | 1,184 |
| `requires_existing_evidence_reconciliation` | 10 | 1,583 |
| `requires_visual_semantic_review` | 5 | 147 |

## Source groups

### `src_pl_bigster_brochure_20251210`

#### `bigster_narrative` — pages 1–13

- Domain: `product_narrative`
- Decision: `descriptive_non_import` / `closed_non_import`
- Candidates: 304
- Summary: Retain as descriptive candidate-only evidence.
- Rationale: The pages contain product narrative, navigation and broad feature claims without an authored exact configuration, attribute and context mapping. They remain useful for human reference but do not support direct structured-data promotion.
- Anchors:
  - `8ec896e46ea3d28bfcf565cfd381570309595136a4df90d36bc68e2887cf734c` — page 1, lines 1–1: `BIGSTER`
  - `dcef3df92c8b9124e0241b3631a5ca8438e70d5c3fcfabf6be1b9cc2e2834383` — page 2, lines 19–19: `PANORAMICZNY               ELEKTRYCZNIE`

#### `bigster_catalogue_entities` — pages 14–19

- Domain: `colours_grades_accessories`
- Decision: `requires_entity_mapping` / `deferred_entity_mapping`
- Candidates: 232
- Summary: Require explicit trim, colour, package or accessory entity mapping.
- Rationale: The pages describe colours, grades, packages and accessories. Candidate text alone does not establish the exact entity identity, applicability, price or configuration scope needed for a controlled import.
- Anchors:
  - `6392c4f76fe81a18bd64504a68dac4e7338289fd55b9b579f5b880ff680584e5` — page 14, lines 1–1: `07. KOLORY NADWOZIA`
  - `aa9c00a70506120624b50a6ccbfa27bab96e78688cdbb0eb5ce5d39114061c15` — page 14, lines 6–6: `         BIEL                    CZARNA              SZARY          NIEBIESKI   ZIELONY`

#### `bigster_technical_tables` — pages 20

- Domain: `technical_tables`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 130
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `e15edb0ab9453e3b368cc6069f90a2331c05eec57abc0ed8c1a543d61179e97a` — page 20, lines 1–1: `07. DANE TECHNICZNE`
  - `fe2e4bbddf98efca3fea972cd5d62abb64bd3ea4c6e94e97448b51bdc686dbe3` — page 20, lines 5–5: `                                            MILD                    MILD                  HYBRID-G 150`

#### `bigster_equipment_matrix` — pages 21–22

- Domain: `equipment_matrix`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 209
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `e8cc627e4325b81a6b9b41c96668069faada9e21e74ae6631a550ba7e0fff73e` — page 21, lines 8–8: `      DESIGN ZEWNĘTRZNY`
  - `0c0877f76ba41b2d6e1228b5cb7b6be2ce6fd63fe5c01238e71a4ccb3e645bfe` — page 21, lines 5–5: `                                                              ESSENTIAL EXPRESSION             JOURNEY       EXTREME`

#### `bigster_dimensions_and_cargo` — pages 23

- Domain: `dimensions_and_cargo`
- Decision: `requires_visual_semantic_review` / `deferred_visual_review`
- Candidates: 28
- Summary: Require visual page semantics and contextual mapping.
- Rationale: Dimensions and cargo pages rely on diagram position, stars, view labels, drive or seat state and measurement basis. Text extraction order alone cannot safely map numbers to attributes or determine exact configuration scope.
- Anchors:
  - `32982c939590e684cafa3222b573697fa93458635ab0a7086aff3345c540d455` — page 23, lines 1–1: `07. WYMIARY`
  - `cec0ab4c37a7fce40f61006c8e80d0afb9b9cfda5d3e799ffe6ab98a11458468` — page 23, lines 32–32: `                                          14°         14°`

#### `bigster_legal_footer` — pages 24

- Domain: `legal_navigation_footer`
- Decision: `explicit_non_import` / `closed_non_import`
- Candidates: 17
- Summary: Treat legal, navigation and publication boilerplate as explicit non-import.
- Rationale: Publication credits, legal notices, navigation labels and calls to action are not vehicle observations and must not be projected into canonical data.
- Anchors:
  - `6dc26c6a94bf30390a1468ec0b38a69d5eb34277fd163f5dc253a0f9cb01bed2` — page 24, lines 16–16: `PUBLICIS – ZDJĘCIA: F. SCHLOSSER, ©RENAULT MARKETING 3D-COMMERCE – 10.12.2025.`
  - `199764e5929337f65596028dd90ba3a47b5dd649b3e9716534418c351ec533f1` — page 24, lines 21–21: `       SKONFIGURUJ                                    ZAREZERWUJ                                           ZNAJDŹ`

### `src_pl_duster_mini_brochure_20251020`

#### `duster_narrative` — pages 1–13

- Domain: `product_narrative`
- Decision: `descriptive_non_import` / `closed_non_import`
- Candidates: 296
- Summary: Retain as descriptive candidate-only evidence.
- Rationale: The pages contain product narrative, navigation and broad feature claims without an authored exact configuration, attribute and context mapping. They remain useful for human reference but do not support direct structured-data promotion.
- Anchors:
  - `87d2c72a3dbc8f699a488fe34a354ac74f18686d02b48f5bc534b5912ccea4b8` — page 1, lines 1–1: `DUSTER`
  - `8a27c0ffde9ed0c372e02f57fe860a61f85053375449ccb4e0ec2086e2353ef1` — page 2, lines 18–18: `ZESPOŁY NAPĘDOWE                         NOWE TRYBY JAZDY`

#### `duster_catalogue_entities` — pages 14–19

- Domain: `colours_grades_accessories`
- Decision: `requires_entity_mapping` / `deferred_entity_mapping`
- Candidates: 239
- Summary: Require explicit trim, colour, package or accessory entity mapping.
- Rationale: The pages describe colours, grades, packages and accessories. Candidate text alone does not establish the exact entity identity, applicability, price or configuration scope needed for a controlled import.
- Anchors:
  - `adb4147f53fa5a5f50c8c19e920680c55d899f177dedadf613dad0b0c7135c8c` — page 14, lines 1–1: `O6. SPECYFIKACJE TECHNICZNE`
  - `247b8efca618027fd9c8220f859d653b2e54f96fe5c2184f8a474960153d30b0` — page 14, lines 9–9: `                                  LICHEN                  BRĄZOWY                       BIEL           SZARY`

#### `duster_technical_tables` — pages 20–21

- Domain: `technical_tables`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 183
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `6d4d9aa61df6d3201790f13ff8b3427fc5d43b6196e00ab0b313e8e02d216e79` — page 20, lines 1–1: `O6. SPECYFIKACJE TECHNICZNE`
  - `31ddd3da1386fd36dd67f48690f338e914ff83a80043f715a1c4412bd18414dc` — page 20, lines 7–7: `                                                                          Eco-G 120                    mild hybrid 140`

#### `duster_equipment_matrix` — pages 22–23

- Domain: `equipment_matrix`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 280
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `7ad6d34c9bd118df8e5d551cc93067a73d9d2e993e08283dc7439b14fb9129b6` — page 22, lines 1–1: `O6. SPECYFIKACJE TECHNICZNE`
  - `3d4248f371b7d9412a49c6c9850d653ad1316ea283ba12b29cc95f4c2a47b9df` — page 22, lines 8–8: `                                                    ESSENTIAL          EXPRESSION            JOURNEY            EXTREME`

#### `duster_dimensions_and_cargo` — pages 24

- Domain: `dimensions_and_cargo`
- Decision: `requires_visual_semantic_review` / `deferred_visual_review`
- Candidates: 32
- Summary: Require visual page semantics and contextual mapping.
- Rationale: Dimensions and cargo pages rely on diagram position, stars, view labels, drive or seat state and measurement basis. Text extraction order alone cannot safely map numbers to attributes or determine exact configuration scope.
- Anchors:
  - `c163719faf93234c8100271ae116edb026d8ab36754edccae6691e1acac50221` — page 24, lines 1–1: `O6. SPECYFIKACJE TECHNICZNE`
  - `462a8deeb765a0072aab4d818798a3c965c720986d458110fd41f95ffab96ff5` — page 24, lines 38–38: `                                             14°           14°`

#### `duster_legal_footer` — pages 25

- Domain: `legal_navigation_footer`
- Decision: `explicit_non_import` / `closed_non_import`
- Candidates: 17
- Summary: Treat legal, navigation and publication boilerplate as explicit non-import.
- Rationale: Publication credits, legal notices, navigation labels and calls to action are not vehicle observations and must not be projected into canonical data.
- Anchors:
  - `3366108ec0908c37ce7e1fb942b391782478cda9196df8648e51a5397fe844e0` — page 25, lines 27–27: `                                                                                                                         MENU`
  - `bb2841f3507fca6cc3c3baf80ca3be1b21dbe8606563f299901443a210812f08` — page 25, lines 17–17: `PUBLICIS – ZDJĘCIA:                                                               – 20.10.2025`

### `src_pl_jogger_brochure_20251217`

#### `jogger_narrative` — pages 1–12

- Domain: `product_narrative`
- Decision: `descriptive_non_import` / `closed_non_import`
- Candidates: 246
- Summary: Retain as descriptive candidate-only evidence.
- Rationale: The pages contain product narrative, navigation and broad feature claims without an authored exact configuration, attribute and context mapping. They remain useful for human reference but do not support direct structured-data promotion.
- Anchors:
  - `b83986cf07b0b5772771ccec6616d247741d54a8338d49b6633b94f70e596c9c` — page 1, lines 1–1: `JOGGER`
  - `d0ae9635c6448bd8bed5fa237a9824c6b99b70838b8465d86a32d29ceccde669` — page 2, lines 14–14: `POJEMNOŚĆ                                 3 NOWE SYSTEMY`

#### `jogger_catalogue_entities` — pages 13–18

- Domain: `colours_grades_accessories`
- Decision: `requires_entity_mapping` / `deferred_entity_mapping`
- Candidates: 239
- Summary: Require explicit trim, colour, package or accessory entity mapping.
- Rationale: The pages describe colours, grades, packages and accessories. Candidate text alone does not establish the exact entity identity, applicability, price or configuration scope needed for a controlled import.
- Anchors:
  - `8628a03361682b85b3cbf6c4d438b99407682365cc8b95b82ac9201b62264864` — page 13, lines 1–1: `06. KOLORY NADWOZIA`
  - `1aad13a6006ebe766066fc678b047825f15c2a0dae1b4a8174ff65e67b2d812a` — page 13, lines 6–6: `     PIASKOWY                  BRĄZOWY                 ZIELONY     BIAŁY    CZARNY`

#### `jogger_technical_tables` — pages 19

- Domain: `technical_tables`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 82
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `ab927c1128ccadf1b4fa831efcff20519bc7e004dd5153e82719cce61126d8fc` — page 19, lines 1–1: `06. SILNIKI`
  - `e933c1027e224c482b4fdab447f1b9b70af91b4dc333dfc22feb7fd2ea069411` — page 19, lines 5–5: `                                           TCe 110            Eco-G 120                 Eco-G 120 auto              hybrid 155`

#### `jogger_equipment_matrix` — pages 20–21

- Domain: `equipment_matrix`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 197
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `36465be7a2bdcd50fc8ed491db5ffbb9dd8e5ad9de7eb6c9b9c16a9677933a3b` — page 20, lines 8–8: ` NADWOZIE`
  - `2d3a40351384132eab27e0f3c5e6ab6d1b8c04fb15343da31593e9bdeb57ee88` — page 20, lines 5–5: `                                                   essential       expression            extreme         journey`

#### `jogger_dimensions_and_cargo` — pages 22

- Domain: `dimensions_and_cargo`
- Decision: `requires_visual_semantic_review` / `deferred_visual_review`
- Candidates: 36
- Summary: Require visual page semantics and contextual mapping.
- Rationale: Dimensions and cargo pages rely on diagram position, stars, view labels, drive or seat state and measurement basis. Text extraction order alone cannot safely map numbers to attributes or determine exact configuration scope.
- Anchors:
  - `656c6619f7d57908fc6fe146eb437803538ffd4ce9f4ab0ab7065fb5e648d559` — page 22, lines 1–1: `06. WYMIARY`
  - `8c136bbfa7601f40665b34c21c18eb49c6c471a7b676dc470b3b7ef381b498b6` — page 22, lines 40–40: `       833                                  2898                      819`

#### `jogger_legal_footer` — pages 23

- Domain: `legal_navigation_footer`
- Decision: `explicit_non_import` / `closed_non_import`
- Candidates: 17
- Summary: Treat legal, navigation and publication boilerplate as explicit non-import.
- Rationale: Publication credits, legal notices, navigation labels and calls to action are not vehicle observations and must not be projected into canonical data.
- Anchors:
  - `8047c55576cc069e4b552424a62b4da526f2b6d5777f7ae9ffcb534a20bde5f0` — page 23, lines 16–16: `PUBLICIS – ZDJĘCIA: S. STAUB, ©RENAULT MARKETING 3D-COMMERCE – 17.12.2025`
  - `c89b83104b2074d30cddee2b17cfe7eca91f7f0492b0ce19aca27768c2743387` — page 23, lines 21–21: `       SKONFIGURUJ                                    ZAREZERWUJ                                           ZNAJDŹ`

### `src_pl_sandero_brochure_20260202`

#### `sandero_narrative` — pages 1–11

- Domain: `product_narrative`
- Decision: `descriptive_non_import` / `closed_non_import`
- Candidates: 214
- Summary: Retain as descriptive candidate-only evidence.
- Rationale: The pages contain product narrative, navigation and broad feature claims without an authored exact configuration, attribute and context mapping. They remain useful for human reference but do not support direct structured-data promotion.
- Anchors:
  - `7e4c1f3d29313e11f374ce6b643b15715c4592e3efa6dbfc83fb83e841bcda6d` — page 1, lines 1–1: `SANDERO`
  - `9da6aff75efbfc8d4a6370847c78c471c74c22f99ae2cba7982b3f14a1473e7a` — page 2, lines 15–15: `POJEMNOŚĆ                                KARTA`

#### `sandero_catalogue_entities` — pages 12–16

- Domain: `colours_grades_accessories`
- Decision: `requires_entity_mapping` / `deferred_entity_mapping`
- Candidates: 276
- Summary: Require explicit trim, colour, package or accessory entity mapping.
- Rationale: The pages describe colours, grades, packages and accessories. Candidate text alone does not establish the exact entity identity, applicability, price or configuration scope needed for a controlled import.
- Anchors:
  - `3bb2221e0a9a9f40432e9fdb8174c61e2f4818922384b145354639004bd26c89` — page 12, lines 1–1: `06. KOLORY NADWOZIA`
  - `57c4d4bb4bc490b3b20aea453dcb21d6415085fe7a63baad8ac13b93bb784682` — page 12, lines 6–6: `       ŻÓŁTY                   PIASKOWY                 BIAŁY    SZARY    NIEBIESKI`

#### `sandero_technical_tables` — pages 17

- Domain: `technical_tables`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 72
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `fcc74e4fcad06ab7bdab27e03467533cfbd7e93023bf21447f1659a546248e0d` — page 17, lines 1–1: `06. SILNIKI`
  - `64fe01e2ff8334bdcf514b1fd93c10954aec1384bb289b3e3b1a8078a2844c46` — page 17, lines 5–5: `                                          100 TCe                    120 Eco-G                        120 Eco-G auto`

#### `sandero_equipment_matrix` — pages 18–19

- Domain: `equipment_matrix`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 164
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `cfd3317fd02b18be8918f9ad95804d5aff7b1a3f1b874a13349f62ac3ae7f058` — page 18, lines 8–8: ` NADWOZIE`
  - `91cb49a11cf63869b7281d50fe7789a9c3b47c67628fcb883a51f1ab240a31b7` — page 18, lines 5–5: `                                                     essential           expression             journey`

#### `sandero_dimensions_and_cargo` — pages 20

- Domain: `dimensions_and_cargo`
- Decision: `requires_visual_semantic_review` / `deferred_visual_review`
- Candidates: 24
- Summary: Require visual page semantics and contextual mapping.
- Rationale: Dimensions and cargo pages rely on diagram position, stars, view labels, drive or seat state and measurement basis. Text extraction order alone cannot safely map numbers to attributes or determine exact configuration scope.
- Anchors:
  - `042e4b6e66f0b1efb7cb07b2e61c6a65dd8aa133fc4260009f94183e7b50ee76` — page 20, lines 1–1: `06. WYMIARY`
  - `3eee9311befbeceb19bf27c824df0bb54d07207a70812b2fe879ed05ef57dec4` — page 20, lines 51–51: `                                                    1406       1026`

#### `sandero_legal_footer` — pages 21

- Domain: `legal_navigation_footer`
- Decision: `explicit_non_import` / `closed_non_import`
- Candidates: 16
- Summary: Treat legal, navigation and publication boilerplate as explicit non-import.
- Rationale: Publication credits, legal notices, navigation labels and calls to action are not vehicle observations and must not be projected into canonical data.
- Anchors:
  - `a6bc15dad32f9511e867c7c3bbccf2c6c1c8b47a9e44fd0a60bb1794f05a4af1` — page 21, lines 16–16: `PUBLICIS – ZDJĘCIA: S. STAUB, ©RENAULT MARKETING 3D-COMMERCE – 02.02.2026`
  - `c417fb210f1ad9b40786e55bafb1dcca1c5d9dfc8cd26a99de8d860eb5ccedd2` — page 21, lines 21–21: `       SKONFIGURUJ                                    ZAREZERWUJ                                           ZNAJDŹ`

### `src_pl_sandero_stepway_brochure_20260202`

#### `sandero_stepway_narrative` — pages 1–11

- Domain: `product_narrative`
- Decision: `descriptive_non_import` / `closed_non_import`
- Candidates: 199
- Summary: Retain as descriptive candidate-only evidence.
- Rationale: The pages contain product narrative, navigation and broad feature claims without an authored exact configuration, attribute and context mapping. They remain useful for human reference but do not support direct structured-data promotion.
- Anchors:
  - `78376604b749eaa8553c62aadecfc37437b4ac8a7d499cf756a16a1ffb696ddb` — page 1, lines 1–1: `SANDERO`
  - `74e353729ca5c7e2b013edcfaf91e28181de81997e8c10516590239d7cc9c95b` — page 2, lines 15–15: `POJEMNOŚĆ                              MODUŁOWE`

#### `sandero_stepway_catalogue_entities` — pages 12–16

- Domain: `colours_grades_accessories`
- Decision: `requires_entity_mapping` / `deferred_entity_mapping`
- Candidates: 198
- Summary: Require explicit trim, colour, package or accessory entity mapping.
- Rationale: The pages describe colours, grades, packages and accessories. Candidate text alone does not establish the exact entity identity, applicability, price or configuration scope needed for a controlled import.
- Anchors:
  - `499ee2dc8a9e5c4a198d37f3ab81a60568da639ddbf48b2fedc02a2eb5bde88d` — page 12, lines 1–1: `06. COLOUR PALETTE`
  - `aa67cf26d6cfc0646dc65dcfba36ae232933eec6339fe787c934e9e2c7941ff2` — page 12, lines 6–6: `       ŻÓŁTY                     BIAŁY                 CZARNY     SZARY    NIEBIESKI`

#### `sandero_stepway_technical_tables` — pages 17

- Domain: `technical_tables`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 74
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `324aec68859236ca98c9e62d99da55849a6559ce07de645f4685d6ba892ddde5` — page 17, lines 1–1: `06. SILNIKI`
  - `e9c62f8d913414a0fcff9a8e43bb3a68cf61143ea38ea9c9c7d0e76044cb79e5` — page 17, lines 5–5: `                                               TCe 110                      120 Eco-G                120 Eco-G auto`

#### `sandero_stepway_equipment_matrix` — pages 18–19

- Domain: `equipment_matrix`
- Decision: `requires_existing_evidence_reconciliation` / `deferred_reconciliation`
- Candidates: 192
- Summary: Reconcile against current exact source-backed records before any new decision.
- Rationale: Technical or equipment table text may duplicate later exact observations, preserve important column context, contain placeholders or expose a real residual gap. Every candidate must be compared with current evidence before it can be classified further.
- Anchors:
  - `8a876ee846d468fc3cab8b22a2195e932404bd11a81ee9e3d79df401d85a8b62` — page 18, lines 8–8: ` NADWOZIE`
  - `c4727a3772038c60728dad8cdd9b66ffc1ad8d3d7c36000a04da579f9108fe78` — page 18, lines 5–5: `                                                    essential          expression               extreme`

#### `sandero_stepway_dimensions_and_cargo` — pages 20

- Domain: `dimensions_and_cargo`
- Decision: `requires_visual_semantic_review` / `deferred_visual_review`
- Candidates: 27
- Summary: Require visual page semantics and contextual mapping.
- Rationale: Dimensions and cargo pages rely on diagram position, stars, view labels, drive or seat state and measurement basis. Text extraction order alone cannot safely map numbers to attributes or determine exact configuration scope.
- Anchors:
  - `58ddc2e127db9537a0afe38f5137fe9b82f0b83a58a2d8bc9a8c660412b0527d` — page 20, lines 1–1: `06. WYMIARY`
  - `c429eb573d0e06271dd9be286049bd15ff2e91a6ca90360d40e9170db6659e4f` — page 20, lines 52–52: `                                                   1406      1026`

#### `sandero_stepway_legal_footer` — pages 21

- Domain: `legal_navigation_footer`
- Decision: `explicit_non_import` / `closed_non_import`
- Candidates: 16
- Summary: Treat legal, navigation and publication boilerplate as explicit non-import.
- Rationale: Publication credits, legal notices, navigation labels and calls to action are not vehicle observations and must not be projected into canonical data.
- Anchors:
  - `2ec1f415c2451f5e07a7e303f9928eb6266a74d0f986bb89f0add2edbd3824a1` — page 21, lines 16–16: `PUBLICIS – ZDJĘCIA: S. STAUB, ©RENAULT MARKETING 3D-COMMERCE – 02.02.2026`
  - `379e74eaed85abfae23edaddaad53b6c2202078174c5960eeed878c1b46b38ed` — page 21, lines 21–21: `       SKONFIGURUJ                                    ZAREZERWUJ                                           ZNAJDŹ`

## Safety boundary

This review creates no master-data row and no approved import specification. It does not infer diagram semantics, exact configuration applicability or canonical entity mappings from extraction order. Candidate-level promotion remains blocked until a separate reconciliation decision cites the candidate ID and current exact evidence.

## Next package

**Verified PDF Candidate Coverage Reconciliation** — Reconcile reviewed technical and equipment candidate groups against current exact source-backed observations and availability records, classifying candidate IDs as already covered, unresolved, ambiguous or explicit non-import without creating imports.
