# ENNOVERA PROSPECTIVE RUN 001 — FORENSIC CORRECTION REPORT

- **Original Run:** `PROSPECTIVE_RUN_2026_08_28_001`
- **Original Commit:** `09b83d0bcdb79417c8a54f062cb87e6a6b2dc630` (Preserved intact; never amended).
- **Core Governance Corrections:**
  1. **Timing Semantics & Early Forecast Reclassification:** Reclassified 10 Matchweek 3 PL predictions as `EARLY_FORECAST` and FPL GW3 plan as `EARLY_GW_PLAN`. They are preserved as valuable early research evidence but do not count toward canonical prospective denominators until official execution inside the designated pre-kickoff/pre-deadline operational windows.
  2. **Prohibition of Future Freeze Timestamps:** Formalized the invariant `official_freeze_at <= current_actual_time_at_snapshot_creation`.
  3. **Hash Reconciliation:** Reconciled model artifact hashes in `research_lock_v2_hash_reconciliation.json` (FPL: `7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d`, PL: `2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f`). Root cause: prompt string template reporting vs physical manifest byte hashing.
  4. **Fallback Provenance Validation:** Audited decoupled Bayesian priors (PL) and DefCon role resistance (FPL) as 100% frozen-model-valid historical mechanisms.
  5. **Snapshot Registry & Counter Integrity:** Deployed append-only `snapshot_registry.csv` enforcing exactly one canonical evaluation snapshot per fixture/gameweek.
