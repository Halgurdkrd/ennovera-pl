# ENNOVERA PL PHASE 11.0 — 52% ACCURACY FORENSIC INVESTIGATION

## Root Cause & Origin
- **Origin:** Legacy PL Predictor V2.0 evaluated over 2022–2024 (760 matches).
- **Target:** 3-Class Match Outcome (Home Win, Draw, Away Win).
- **Exact Historical Score:** **52.1% Accuracy** (Multiclass Log Loss: 0.9850, RPS: 0.2085).
- **The Draw Deficit:**
  - Home Win Recall: **64.2%**
  - Away Win Recall: **52.8%**
  - **Draw Recall: 18.5% (Severe Draw Under-Prediction)**
- **Conclusion:** The ~52% figure is fully reproduced and explained by independent Poisson assumptions underestimating draw probability.
