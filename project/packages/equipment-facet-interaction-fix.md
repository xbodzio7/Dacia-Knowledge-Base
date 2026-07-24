# Equipment Facet Interaction Fix

Status: complete

## Goal

Make equipment filtering predictable without changing source-backed availability data.

## Behaviour

- text search visibly hides non-matching equipment entries;
- selected equipment remains selected until the user removes it;
- the system never resolves a conflict by silently unchecking an earlier choice;
- the list exposes only source-complete features that can be added while retaining at least one configuration;
- mutually exclusive alternatives disappear while the conflicting choice is active;
- incomplete cross-model option data remains hidden rather than being interpreted as confirmed unavailability.

## Covered user scenarios

- entering `ABS` visibly reduces the equipment list to matching names instead of leaving all buttons displayed;
- selecting the 10.1-inch colour instrument cluster hides the incompatible 3.5-inch TFT alternative until the active choice is removed;
- selecting LED cabin lighting does not get silently cleared when another lighting item is considered, and incompatible additions are not offered;
- missing Duster option records remain unknown and are not converted into a claim that the option is unavailable.

## Non-goal

This package does not infer or import options for any model. Cross-model source intake remains a separate planned package.

## Verification

- conflicting selections remain selected and are reported clearly;
- mutually exclusive instrument-cluster and lighting alternatives are hidden;
- equipment-list search obeys the HTML `hidden` contract;
- full repository test suite and project-state check.
