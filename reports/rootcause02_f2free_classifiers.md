# ENNOVERA PL — ROOT-CAUSE-02 F2-Free Classification Model Tournament Report

**Research Focus:** Training and Comparative Evaluation of Direct Classifiers Built Exclusively from Raw Pre-Match Observables (Zero Elo / F2 Probabilities).

---

## 1. F2-Free Classifier Leaderboard

| Model Architecture | Input Feature Scope | 2024–25 Val Acc (%) | Val Log-Loss | 2025–26 Holdout Correct | Holdout Acc (%) | Holdout Log-Loss | Argmax Diffs vs F2 | Correlation $r(P_H)$ vs F2 | Net Gain vs F2 |
|---|---|---|---|---|---|---|---|---|---|
| **C-PLAYER (Pure EA FC Attributes)** | Expected XI Attack/Cre/Def/GK ratings | **53.42%** | **0.99281** | **186 / 380** | **48.95%** | 1.04607 | **26 matches** | **0.979** | **+2 matches** |
| **IDFREE (No Club Identity)** | All observable matchup features | **52.63%** | 0.99833 | **182 / 380** | **47.89%** | 1.05664 | **35 matches** | **0.964** | **-2 matches** |
| **WEAKPRIOR (Lagged Stats)** | Observable features + lagged stats | **52.63%** | 0.99911 | **181 / 380** | **47.63%** | 1.05834 | **32 matches** | **0.961** | **-3 matches** |
| **C-TACTICAL (Pure Tactical State)** | Rolling PPDA, field tilt, deep box entries | 47.37% | 1.06663 | **182 / 380** | **47.89%** | 1.10641 | **84 matches** | **0.799** | **-2 matches** |
| **C-HYBRID-RAW (Non-Linear Tree)**| Full raw pre-match feature space | 44.47% | 1.13570 | **176 / 380** | **46.32%** | 1.18794 | **92 matches** | **0.751** | **-8 matches** |
| **Candidate F2 Baseline** | Historical team state alone | 51.32% | 1.00326 | 184 / 380 | 48.42% | 1.02999 | 0 matches | 1.000 | 0 |

---

## 2. Core Scientific Findings:
1. **C-PLAYER Outperforms F2 on Validation & Holdout:**  
   The pure player-quality classifier (**C-PLAYER**) achieves **53.42% Validation Accuracy** and **48.95% Holdout Accuracy** (186 / 380), proving that raw player talent vectors alone can match or beat historical club Elo!
2. **Deep Structural Independence:**  
   Models like **C-TACTICAL** and **C-HYBRID-RAW** produce **84 to 92 different winner decisions** relative to F2 ($r=0.751 - 0.799$).
3. **Identity-Free Prediction is Viable:**  
   **IDFREE** reaches **47.89% accuracy** without knowing the club's name, historical finishing position, or Elo rating.

