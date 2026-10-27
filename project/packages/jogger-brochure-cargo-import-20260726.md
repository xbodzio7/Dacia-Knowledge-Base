# Jogger Brochure Cargo Value Import

Date: 2026-07-26

## Scope

Import the unambiguous cargo table observations on page 22 of the official Polish
Jogger brochure dated 17 December 2025 into all 22 active Jogger configurations.

The package keeps five- and seven-seat layouts separate. It creates 110 canonical
`boot_capacity` observations, 110 one-to-one cargo-context rows and 22
source-to-configuration relationships.

## Five-seat observations per configuration

- 708 dm3 according to ISO 3832, second row upright, main luggage compartment;
- 829 ordinary litres, second row upright, main luggage compartment;
- 1819 dm3 according to ISO 3832, second row folded, source-stated total;
- 2094 ordinary litres, second row folded, source-stated total.

The brochure separately confirms that 1819 dm3 is the five-seat variant with the
rear bench folded.

## Seven-seat observations per configuration

- 160 dm3 according to ISO 3832 and 212 ordinary litres with both rear rows upright;
- 565 dm3 according to ISO 3832 and 699 ordinary litres with the second row upright
  and the third row folded;
- 696 dm3 according to ISO 3832 and 820 ordinary litres with the second row upright
  and the third row removed.

## Deferred maximum

The seven-seat maximum pair `1807 dm3 / 2085 L` is not imported. The table does not
state whether the third row is folded or removed, and those states are materially
different in the canonical context model. Importing either interpretation would be
an unsupported inference.

## Evidence boundary

The source distinguishes passenger layout and rear-row state but does not qualify
the values by spare wheel, tyre-repair kit or double floor. Those optional context
fields remain empty and mean **not stated**, never `absent`.

Every mapped configuration is active, belongs to Jogger and has an exact
configuration-level `number_of_seats` observation matching its five- or seven-seat
layout.

## Follow-up

The next package will evaluate the official Bigster brochure cargo table, including
repair-kit, spare-wheel and double-floor qualifiers already supported by the cargo
context model.
