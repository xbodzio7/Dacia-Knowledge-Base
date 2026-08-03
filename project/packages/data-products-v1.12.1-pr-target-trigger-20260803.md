# Data Products v1.12.1 PR-Target Activation

Date: 2026-08-03

## Purpose

Open the exact bounded same-repository activation pull request required by the temporary PR-target publisher installed on `main`.

This branch changes no release source data, generated report semantics, publication contract, or canonical project state. The base SHA of this pull request is the exact publication source. The activation pull request is not intended to merge and will be closed after the immutable release, public-download verification, receipt commit, state transition, and temporary workflow cleanup complete successfully.

A follow-up synchronization event is included solely to ensure the registered base-branch workflow receives an activation event; the publisher concurrency group and immutable-release checks prevent duplicate publication.
