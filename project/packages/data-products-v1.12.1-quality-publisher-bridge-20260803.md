# Data Products v1.12.1 Registered Workflow Publisher Bridge

Date: 2026-08-03

This one-time package attaches the verified v1.12.1 publisher to the already registered `Versioned Data Product Release` workflow. The publisher runs only on the merge push of this package, uses that exact `main` SHA, performs independent byte-identical builds, verifies the complete offline workspace and public downloads, records the publication receipt, and removes all temporary publication automation.
