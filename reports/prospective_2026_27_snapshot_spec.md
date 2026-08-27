# ENNOVERA 2026-27 IMMUTABLE SNAPSHOT SPECIFICATION

- **Snapshot ID:** Deterministic formatted UUID / string containing competition, gameweek, fixture, and timestamp.
- **Hash Guarantee:** SHA256 hashes generated across input features, model commit, and prediction matrix.
- **Separation:** Post-match actual results stored in dedicated outcome entities; frozen prediction objects remain read-only.
