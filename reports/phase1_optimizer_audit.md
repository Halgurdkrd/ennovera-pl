# ENNOVERA PHASE 1 — LINEAR PROGRAMMING OPTIMIZER AUDIT

### Mathematical Verification of Constraints
$$\max \sum_{i=1}^{N} \text{xP}_i \cdot x_i \quad \text{subject to:}$$
1. Total Cost <= £100.0m
2. Total Players == 15 (2 GK, 5 DEF, 5 MID, 3 FWD)
3. Max 3 players per club
4. Starting XI valid formation: DEF in [3,5], MID in [2,5], FWD in [1,3], GK == 1, Total == 11.
