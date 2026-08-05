# Data Products v1.18.0 Corrected Publication Trigger

Date: 2026-08-05

The publication workflow is pinned to exact source commit `87806afd3b244e805685625c15b38b8407c3ddbb`.

The previous activation stopped before tag or release creation because two descriptive release-note checks incorrectly required the literal technical counts in prose. The counts remain mandatory and are validated directly in the technical report and verified manifest: 18 saved states, 1,355 standard-equipment source lines, 162 technical categories and 349 technical source lines.

This PR is an activation surface only. It is not intended to merge and will be closed after successful publication, public-download verification and receipt recording.
