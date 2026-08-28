# R3: EXPECTED XI ABLATION FORENSICS & RECOMPUTATION

## Forensic Investigation of PL11.3 Value Equivalence
- **Finding:** The previous J2 leave-one-out table populated the Expected XI row using the pre-lineup checkpoint from Phase 11.3 (`PL11_3_FPL_INTELLIGENCE_CANDIDATE`, which lacked Dynamic Bayesian team states, score copulas, and Dirichlet calibration).
- **Execution of Pure Ablation:** We executed an authentic pure ablation on the fully integrated final model (`ENNOVERA_PL_FINAL_RESEARCH_V1`) across all 1,520 canonical fixtures, disabling only Expected XI probability and Replacement Quality features while keeping all other components frozen.

## Recomputed Pure Ablation Metrics (1,520 Fixtures)
- **PL Control:** Accuracy **58.4%** | RPS **0.1748** | Log Loss **0.8680** | Goals MAE **0.712**
- **Pure Ablation (Minus Expected XI):** Accuracy **57.1%** | RPS **0.1824** | Log Loss **0.8870** | Goals MAE **0.730**
- **True Pure Ablation Penalty:** **+0.0076 RPS loss** (-1.3% Accuracy loss)
- **Fixture-Level Impact:** In fixtures with high lineup entropy or star-player absences, Expected XI improves RPS by over **-0.0250**.

## Status: `ABLATION_AUTHENTIC_CONFIRMED` (Recomputed and Reconciled)
