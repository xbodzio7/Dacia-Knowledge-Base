# Spring Official Source Intake Review

Date: 2026-07-31

Status: **complete**

## Decision

Select **Spring Official PDF Source Registration** as the next package.

Spring currently has no registered source in the project. The review identified two stable official Polish documents that can be captured and verified independently before any observation is imported:

- the 22-page Spring brochure dated 2026-02-19;
- the six-page Spring price list effective from 2026-07-08, explicitly limited to the model-year-2025 stock offer.

## Selected immutable sources

### Official brochure

The brochure covers essential, expression, extreme and cargo variants together with electric 70 and electric 100. It contains equipment and technical tables, but its grade, cargo and powertrain footnotes must remain binding.

The registration package will archive the exact PDF, calculate SHA-256, add a `brochure_pdf` source row and relate it to model `spring` as `brochure_for`. Registration alone will not create configuration, equipment or technical observations.

### Official price list

The price list is effective from 2026-07-08 and describes a model-year-2025 stock offer. Its commercial matrix explicitly shows expression electric 70 and extreme electric 100, including catalogue and promotional stock prices.

The source must remain distinct from current MY26 configurator observations. Stock promotions and footnote-dependent technical values cannot be generalized beyond the exact document scope.

## Deferred dynamic sources

The current Spring configurator proves one exact default state: essential electric 70 MY26.b. Other visible grade selectors do not prove every grade and powertrain combination, so the configurator requires a separate dated normalized snapshot.

The official stock catalogue exposes exact Spring MY26 cards, including extreme electric 100. Each card has dealer-specific and potentially expiring identity. It therefore requires a separate exact-card snapshot and cannot be used as a generic price or equipment source.

## Planned registration package

The next package will contain exactly:

- two archived official PDFs;
- two source rows;
- two model-level source relationships;
- a registration receipt and state update.

It will import no prices, configurations, equipment, technical values or reporting scopes.

Decision: `SELECT_SPRING_OFFICIAL_PDF_SOURCE_REGISTRATION`.
