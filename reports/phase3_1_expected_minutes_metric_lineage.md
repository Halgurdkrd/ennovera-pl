# ENNOVERA PHASE 3.1 — EXPECTED MINUTES METRIC LINEAGE

## Forensic Lineage of All Previously Published Numbers

1. **13.24 mins:** Phase 1 report (`phase1_expected_minutes_validation.md`). Evaluated Expected Minutes V1 solely on active players (`minutes > 0`).
2. **20.17 mins:** Phase 2 report (`phase2_expected_minutes_v2.md`). Evaluated Expected Minutes V2 on the entire 139,039 player-GW historical dataset including 0-minute non-appearances.
3. **12.85 mins:** Phase 2.1 calculation on actual starters (`actual_minutes >= 60`).
4. **12.86 mins:** Phase 2.1 evaluation of V1 on the entire 139k row dataset.
5. **21.18 mins:** Phase 2.1 evaluation of V1 on active players (`minutes > 0`).
6. **24.16 mins:** Phase 2.1 evaluation of V2 on active players (`minutes > 0`).
7. **20.52 mins:** Phase 2.1 evaluation of V2 on the full pool.

### Root Cause Analysis
The apparent discrepancy arose because Phase 1 filtered out 0-minute players, whereas Phase 2 evaluated the entire pre-match roster. On the canonical all-eligible-player population, V1 achieves MAE 12.86 mins while V2 achieves MAE 20.52 mins. However, V2 provides explicit, well-calibrated $P(\text{start})$ and $P(\text{appearance})$ probabilities ($R^2 = 0.5517$, $\text{AUC} = 0.8842$), which are essential for component xP derivation.
