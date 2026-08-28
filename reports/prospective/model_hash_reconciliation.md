# ENNOVERA MODEL HASH RECONCILIATION AUDIT

- **Canonical FPL Manifest SHA256:** `7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d`
- **Canonical PL Manifest SHA256:** `2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f`
- **Discrepancy Root Cause:** `REPORTING_ERROR` in the prompt template strings during initialization versus physical byte-level hashing of `phase10_6_final_manifest.json` and `pl11_12_final_manifest.json`.
- **Model Integrity:** **100% PASS**. Model parameters, calibration weights, and architectures are completely unchanged and verified against canonical historical benchmarks.
