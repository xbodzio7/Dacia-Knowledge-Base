# Duster Mini Equipment Page 23 Ambiguity Review

Authored review of `residual_gap_007`. Symbols and multi-line row boundaries are preserved; the review does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 26 |
| Covered | 6 |
| Partially covered | 20 |
| Selected evidence signatures | 43 |
| Selected evidence records | 518 |
| Rejected attached signatures | 18 |

## Candidate decisions

| Line | Candidate | Decision | Signatures | Records | Row context |
| ---: | --- | --- | ---: | ---: | --- |
| 5 | `e7d77061bf613db664b2fac2c5948d11965c94de2f6d042724801933fd1b4c2a` | `covered` | 2 | 24 | complete fog-lights row |
| 15 | `67bfa6143925d078ab4d6b98e4a909c748fe7efdb6042ceeacafcf92dc7fd942` | `covered` | 2 | 25 | complete manual-air-conditioning row |
| 17 | `914b8682491d97e10cb74de3869f161013139e0194852eefccfd22170de44d4b` | `covered` | 2 | 26 | complete automatic-climate-control row |
| 25 | `8455b0e3b71fd819c06db3d30c2411f082e500e10d56ab4e173079b08e03bbb4` | `partially_covered` | 2 | 25 | first line of the Keyless Entry row |
| 26 | `3d09f4062abab6c0cfc00f6e4ff77b42d3b70a4aec702cd357128705538246e5` | `partially_covered` | 2 | 25 | availability-bearing middle line of the Keyless Entry row |
| 27 | `e0a3dae3be152c1898a485b2d685aae35a35863cb0b2e1add5bb5fb036504a08` | `partially_covered` | 2 | 25 | final line of the Keyless Entry row |
| 28 | `1e3cb273c9aea5a8b30be82184f7f0f06219ed2a4b6d599e350cffb4e84d39da` | `covered` | 1 | 27 | complete front power-window row |
| 30 | `1dbb3d92a96f57ace3ffcf707250f8907622d553496ce01706d6bd607aeb42fb` | `covered` | 2 | 27 | complete rear power-window row |
| 32 | `738ff58cdf0084291a7f7361a7909a42d073083f6c0a71a20fa27a143f6abaad` | `partially_covered` | 2 | 54 | first line of the height/reach steering-wheel adjustment row |
| 35 | `f537be0e005d196dd821e69637a80e99ba8d78eb2e3d9b5029750bbefd33acf0` | `covered` | 1 | 27 | complete driver-seat height row |
| 42 | `367e8c3a0d6f267fe39768d09a019cd8115b46bda563fb17fa21a7a7d665db27` | `partially_covered` | 2 | 8 | passenger-seat height row split across option and standard markers |
| 46 | `77639618810b66ccd2c25ff8e667a62c04164c452fc6022bb77c021dacc1ca60` | `partially_covered` | 2 | 27 | first line of the centre-console armrest row |
| 62 | `3263a784dc65a5239a862c149f7924e52044eae648e2f8c84ba0b8a7f3d47367` | `partially_covered` | 3 | 26 | wireless-charging row with the Extreme package marker on the following line |
| 66 | `05639266337f85a97239e31563d67a576b753d9d1d0fce6fb9529e2563aa18e3` | `partially_covered` | 2 | 24 | first line of the Media Control row |
| 73 | `80fed6910e8c25629cfe124425a23d30797138b0c37e44e4cf5d601540ca7525` | `partially_covered` | 2 | 24 | first line of the Media Display row |
| 92 | `b6fd6517ac2abb8ee8522cf8792137206c79698c0628c2e62542d4598f5a8500` | `partially_covered` | 2 | 27 | final line of the Media Nav Live description |
| 94 | `bdc78d82c8d5108072cba2be1839185b56804cb85b1bcf3d7d69c3fb705a41bb` | `partially_covered` | 2 | 24 | first line of the separate remote-services row |
| 95 | `c695d1a46a9ec4ab42c9b6f9a9ce88ee896a96f0fd085f8f12aba502a2072648` | `partially_covered` | 2 | 24 | second line of the separate remote-services row |
| 107 | `62ec88f4925dacadd5c0a7a925b0094be661a8f392df50ef403e4f4b05b560f9` | `partially_covered` | 1 | 6 | first line of the Parking package row |
| 112 | `919be17ffe35a31d89cb1baaee4d785b2907ff6888a7ae1aa13eb345f5e43a2b` | `partially_covered` | 1 | 9 | first line of the Extreme Winter package row |
| 115 | `c67dfca1a468cd90ffa06827413282fab38239d3383113e552ada097c0efb734` | `partially_covered` | 1 | 6 | first line of the Extreme Winter Plus package row |
| 118 | `9f45140013402ce3253e430ea41b9b164e66a905ff7135db1590a11edb2f869d` | `partially_covered` | 1 | 9 | first line of the Expression/Journey Winter package row |
| 122 | `3bab9be222e4b913a6f0eafaa24622d42a4d885641310ccc3024addfb8473f4f` | `partially_covered` | 1 | 6 | passenger-seat tail of the Expression/Journey Winter package row |
| 123 | `0ce47af75f3921094b15d89c07fb35e222ffc406fb52eae78431baba77a19b2b` | `partially_covered` | 1 | 6 | first line of the Journey Winter Plus package row |
| 127 | `37fdef3bf18768861841e0b7473313fa3a0ffb394c810f7ce9816ce503cdb4a3` | `partially_covered` | 1 | 6 | passenger-seat tail of the Journey Winter Plus package row |
| 142 | `6f657acc5e7861d31dd69553fbd01682f82350547a9efde67677eaba1b1d4535` | `partially_covered` | 1 | 1 | final line of the Hybrid-G 150 4x4 Techno package row |

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- `•`, `¤` and `-` remain standard, optional and unavailable respectively;
- multi-line labels are reviewed as one visual row without inventing new attributes;
- package components do not inherit standard status from records outside the printed package row;
- evidence for adjacent attributes is rejected rather than substituted;

## Next package

**Duster Mini Equipment Page 22 Ambiguity Review** — Review the 11 ambiguous equipment candidates from Duster mini-brochure page 22 against their 27 preserved evidence signatures without creating master-data rows or approved import specifications.
