# ENNOVERA PL — ROOT-CAUSE-04 Oracle Provenance & Match-by-Match Decomposition Report

**Research Focus:** Forensic Accounting and Match-by-Match Provenance of the +20 Tactical and +17 HybridRaw Incremental Oracle Wins.

---

## 1. Incremental Oracle Decomposition Table (2025–26 Holdout Season, N=380)

| System Stage | Constituent Experts | Standalone Oracle Correct | Theoretical Oracle Acc (%) | Incremental Wins Contributed |
|---|---|---|---|---|
| **Baseline Reference** | **M3 Peak Alone** | 189 / 380 | 49.74% | 0 |
| **CORE-3 ORACLE** | **M3 + S2 + C-PLAYER** | **203 / 380** | **53.42%** | **+14 matches** |
| **CORE-4 ORACLE** | **CORE-3 + C-TACTICAL** | **223 / 380** | **58.68%** | **+20 matches** |
| **CORE-5 ORACLE** | **CORE-4 + C-HYBRID-RAW** | **240 / 380** | **63.16%** | **+17 matches** |

---

## 2. Match-by-Match Provenance Summary:
- **The +20 Tactical Oracle Wins:**  
  Represent fixtures where all 3 Core models (M3, S2, C-PLAYER) failed simultaneously, but C-TACTICAL happened to predict the winning outcome (e.g. low-possession counter-attacking upsets and defensive stalemates). Full fixture ledger saved to `data/experiments/rootcause04_tactical_unique_wins.csv`.
- **The +17 HybridRaw Oracle Wins:**  
  Represent extreme outlier fixtures where the entire 4-model ensemble failed, but C-HYBRID-RAW's high-variance tree structure picked the winner. Full fixture ledger saved to `data/experiments/rootcause04_hybridraw_unique_wins.csv`.
- **The Critical Forensic Distinction:**  
  While these 37 matches exist in the post-hoc oracle union, their pre-match predictability must be empirically evaluated against the cost of harmful false overrides.

