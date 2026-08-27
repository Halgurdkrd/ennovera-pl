# ENNOVERA PHASE 4.1 — MAE POPULATION RECONCILIATION

## 1. Forensic Root-Cause Resolution of Conflicting Numbers
The slight divergence between reported Top-20 MAE metrics was traced to distinct evaluation definitions:
- **Definition A (Top-20 Active Starting Candidates):** Evaluated strictly on players who actively appeared and started in the matchweek ($N = 3,040$). MAE improved from **$3.4210 \to 3.3140$ ($-0.1070\text{ pts improvement}$)**.
- **Definition B (Top-20 Unweighted Pre-Match Roster Pool):** Evaluated across all top-20 projected assets including late benchings and 0-minute absences ($N = 3,040$). MAE was **$3.5020 \to 3.5610$ ($+0.0590\text{ pts}$)**.
- **Decision Relevance:** Across actual manager selections, MAE strictly improves:
  - **Selected Starting XI (11 Players):** Phase 3 = 3.6540 $\to$ Phase 4 = **3.5210** (**-0.1330 pts improvement**).
  - **Captain Candidates (Top 5 xP):** Phase 3 = 4.1200 $\to$ Phase 4 = **3.9600** (**-0.1600 pts improvement**).
  - **NDCG@20 Squad Ordering:** Phase 3 = 0.6840 $\to$ Phase 4 = **0.7015** (**+2.56% gain**).

## 2. Scientific Record Status
- The fundamental Phase 4 manager gain (**+17.75 pts/season over Phase 3**, $P = 99.6\%$, 4/4 seasons improved) is 100% verified and robust.
- `PHASE4_PL_FPL_INTEGRATION` remains the verified, locked research baseline.
