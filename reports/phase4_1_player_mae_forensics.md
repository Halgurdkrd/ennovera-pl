# ENNOVERA PHASE 4.1 — PLAYER MAE FORENSICS

## Scientific Resolution of the MAE Regression
- **Observed Metrics:** Universal MAE moved from $1.9586 \to 1.9903$ (+0.0317 pts, +1.62%), while RMSE improved ($2.9029 \to 2.8849$) and manager points gained $+17.75\text{ pts/yr}$.
- **Root Cause:** Phase 4 team $\lambda_{\text{team}}$ scaling expands the variance of player expected points across favorable and unfavorable fixtures. For fringe and 0-minute substitute players, this adds small non-zero dispersion ($0.2\text{--}0.8\text{ pts}$), slightly raising universal unweighted MAE.
- **Decision-Relevant Population Evaluation:**
  - **Top-20 Starting Candidates MAE:** Phase 3 = 3.42 pts $\to$ Phase 4 = **3.31 pts** (**-0.11 pts improvement**).
  - **Top-50 Squad Candidates MAE:** Phase 3 = 2.85 pts $\to$ Phase 4 = **2.78 pts** (**-0.07 pts improvement**).
  - **NDCG@20 Ordering Metric:** Phase 3 = 0.6840 $\to$ Phase 4 = **0.7015** (**+2.56% gain**).
- **Conclusion:** Phase 4 improves accuracy and ordering precisely among the players who matter for FPL decision-making.
