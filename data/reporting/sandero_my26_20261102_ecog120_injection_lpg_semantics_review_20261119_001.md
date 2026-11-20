# Sandero / Sandero Stepway MY26 Eco-G 120 Injection and LPG Capacity Semantics Review

Report ID: sandero_my26_20261102_ecog120_injection_lpg_semantics_review_20261119_001
Generated: 2026-11-20T21:35:05Z
Analysed commit: 8bcc724454adf90f9d022864010f2b76e6286edc
Status: current
Scope: Sandero and Sandero Stepway MY26 official Polish cennik effective 2026-11-02, printed page 5; Eco-G 120 injection wording and LPG/petrol tank-capacity semantics across the nine exact source-linked Eco-G 120 configurations, compared with the official Jogger MY26 cennik effective 2026-10-01, printed page 6.

## Objective and source scope

Review the official Polish Sandero / Sandero Stepway MY26 cennik effective 2026-11-02, printed page 5, for the nine exact Eco-G 120 configurations. Compare its wording with the official Polish Jogger MY26 cennik effective 2026-10-01, printed page 6, only to assess whether the second source establishes a safely transferable shared-powertrain fact.

Both PDFs are archived in the repository and their SHA-256 values are verified.

## Sandero source evidence

The Sandero technical table states:

- Fuel: benzyna + LPG
- Displacement: 1,199 cm³
- Cylinders / valves: 3 / 12
- Injection type: bezpośredni (one unqualified value for the Eco-G 120 column)
- LPG / petrol tank capacities: 40 l / 50 l
- LPG output: 90 kW (122 KM) at 4,500 rpm
- Petrol output: 84 kW (114 KM) at 4,500 rpm

The table does not distinguish the petrol and LPG injection systems. Its 40 l LPG value is not labelled as total vessel capacity or fillable capacity.

## Jogger comparison evidence

The Jogger technical table states the same Eco-G 120 fuel pairing, 1,199 cm³ displacement, 3 / 12 cylinders / valves and fuel-specific power outputs. Unlike Sandero, it explicitly states:

- Petrol injection: direct
- LPG injection: indirect
- LPG total / fillable vessel capacity: 50 l / 40 l
- Petrol tank capacity: 50 l

This is a useful comparison, not proof that the detailed Jogger wording can be transferred to Sandero. The repository currently has no normalized Eco-G 120 record in `data/master/engines.csv` and no Eco-G 120 model-engine relationship in `data/master/model_engines.csv` for Sandero, Stepway or Jogger. Legacy Eco-G 100 records are not identity evidence.

## Existing Sandero capacity observations

The nine exact configurations have 18 source-dated observations from 2026-11-02:

- Nine petrol observations: 50 l each
- Nine LPG observations: 40 l each
- IDs: 8509–8526

They remain represented by the generic `fuel_tank_capacity` attribute with the fuel context retained. No total/fillable classification is added.

## Findings and disposition

### Eco-G 120 injection type — Do sprawdzenia

The Sandero source provides one unqualified injection value, while the Jogger source distinguishes direct petrol injection and indirect LPG injection. The matching engine label and headline technical figures are not enough to establish a normalized shared-engine identity in the repository. Do not add fuel-specific injection values or reinterpret the Sandero value.

### LPG capacity — Do sprawdzenia

The Sandero source's 40 l value is numerically consistent with the Jogger's 40 l fillable capacity, but the Sandero cennik does not state that meaning. Do not convert the existing 40 l observation into total or fillable vessel capacity.

## Outcome

- Master rows added / updated: 0
- Existing fuel-capacity observations preserved: 18
- Fuel-specific injection observations added: 0
- LPG total / fillable classifications added: 0
- Import specifications changed: 0
- Source binaries changed: no

The evidence review is complete. Both underlying semantic questions remain explicitly deferred as **Do sprawdzenia**.

## Verification

The focused test checks the archived source hashes, exact nine-configuration scope, all 18 source-dated capacity rows, absence of fuel-specific injection or LPG total/fillable classifications, engine-registry boundary and report metadata.
