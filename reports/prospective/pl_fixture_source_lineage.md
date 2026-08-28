# ENNOVERA PL FIXTURE SOURCE LINEAGE

- **Raw Ingestion Source:** `data/raw/fpl_full/data/2026-27/fixtures.csv`
- **Validation Pipeline:**
  1. `SeasonFilter`: Enforces `season == '2026-27'`
  2. `TeamsetHardGate`: Asserts `home in canonical_2026_27_teams` AND `away in canonical_2026_27_teams`
  3. `KickoffTimestampAudit`: Validates UTC conversion and ensures monotonic progression
  4. `SnapshotRegistry`: Generates immutable snapshot targets for T-75 to T-60 execution window.
