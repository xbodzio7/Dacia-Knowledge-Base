# Data Products v1.12.1 Publication Trigger

Date: 2026-08-03

Package ID: `data_products_v1_12_1_publication_001`

Activation: `003` — this dedicated branch is the sole accepted activation source for the installed merged-PR publisher.

The exact merge SHA must be used as `repository_commit` and release target. Publication is allowed only after byte-identical independent double builds, canonical asset verification, complete offline workspace verification including the direct `model_family_summary_html` entry point and dedicated **Model family summary** card, and public-download byte identity.

The existing immutable `data-products-v1.12.0` release must not be rewritten.
