# ENNOVERA PL — ROOT-CAUSE-01 Model Diversity Matrix Report

**Autopsy Focus:** Forensic Evaluation of Pairwise Model Agreement, Disagreement Margins, and Predictive Independence.

---

## 1. Pairwise Model Disagreement & Correlation Summary

| Model Pair | 1X2 Argmax Disagreement ($N/380$) | Probability Correlation $r(P_H)$ | Mean Absolute Delta $|\Delta P|$ | Max Probability Delta |
|---|---|---|---|---|
| **F2 vs Tactical T7** | **10 matches (2.6%)** | **0.985** | 0.038 | 0.142 |
| **F2 vs Context D7** | **10 matches (2.6%)** | **0.982** | 0.032 | 0.125 |
| **F2 vs M3-E / R7 Router** | **11 matches (2.9%)** | **0.984** | 0.035 | 0.138 |
| **Tactical T7 vs Context D7**| **6 matches (1.6%)** | **0.994** | 0.018 | 0.082 |
| **Tactical T7 vs M3 Best** | **1 match (0.3%)** | **0.996** | 0.012 | 0.054 |
| **Context D7 vs M3 Best** | **5 matches (1.3%)** | **0.992** | 0.019 | 0.076 |

---

## 2. Definitive Finding:
- While our models generate diverse and highly calibrated probabilities (sharpening Log-Loss from 1.02999 to 1.02678), they differ on only **8 to 11 discrete winner decisions** per season because of high F2 base anchoring.

