# ENNOVERA PL — ROOT-CAUSE-03 Master Router Tournament Report

**Research Focus:** Out-of-Sample Evaluation and Comparative Forensic Tournament of Candidate Routing Architectures (R0 to R8, R-SELECTIVE, SOFT-RELIABILITY).

---

## 1. Master Router Tournament Leaderboard

| Router Architecture | Validation Acc (%) | Val Log-Loss | Holdout Correct / 380 | Holdout Acc (%) | Holdout Log-Loss | Holdout Brier | Net Gain vs M3 | Routing Efficiency (%) | Disagreement Accuracy (%) |
|---|---|---|---|---|---|---|---|---|---|
| **R0: Consensus Majority Router** | **52.63%** | 0.99520 | **191 / 380** | **50.26%** | **1.03098** | **0.6201** | **+2 matches** | **+14.3%** | **43.40% (23/53)** |
| **Ennovera M3 Peak (Baseline)** | 52.11% | 0.99505 | 189 / 380 | 49.74% | 1.02785 | 0.6174 | 0 matches | 0.0% | 39.62% (21/53) |
| **R_SELECTIVE Override Engine** | **54.21%** | **0.98370** | 187 / 380 | 49.21% | 1.03332 | 0.6224 | -2 matches | -14.3% | 35.85% (19/53) |
| **SOFT_RELIABILITY_ROUTER** | 52.11% | 0.99514 | 187 / 380 | 49.21% | 1.03274 | 0.6219 | -2 matches | -14.3% | 35.85% (19/53) |
| **R1: Multinomial Logistic** | 51.32% | 1.01874 | 187 / 380 | 49.21% | 1.04244 | 0.6278 | -2 matches | -14.3% | 35.85% (19/53) |
| **R6: Reliability Argmax** | 53.42% | 0.98215 | 186 / 380 | 48.95% | 1.03529 | 0.6231 | -3 matches | -21.4% | 33.96% (18/53) |
| **R3: Random Forest Router** | 53.42% | 0.99281 | 186 / 380 | 48.95% | 1.04607 | 0.6288 | -3 matches | -21.4% | 33.96% (18/53) |
| **R2: Shallow Decision Tree** | 52.37% | 1.00211 | 185 / 380 | 48.68% | 1.05295 | 0.6318 | -4 matches | -28.6% | 32.08% (17/53) |
| **R4: HistGradientBoosting** | 52.89% | 0.99796 | 184 / 380 | 48.42% | 1.05223 | 0.6315 | -5 matches | -35.7% | 30.19% (16/53) |

---

## 2. Core Scientific Discoveries:
1. **The Consensus Majority Router Breaks 50%:**  
   **R0 Consensus** reaches **191 / 380 (50.26% accuracy)** on Holdout, beating M3 Peak by $+2$ matches and achieving a positive routing efficiency of **+14.3%**.
2. **The Disagreement Match Decider:**  
   On the 53 disagreement matches, **R0 Consensus scores 43.40% (23 / 53 correct)**, higher than M3 alone (39.62%), S2 alone (35.85%), or C-PLAYER alone (33.96%).
3. **The ML Router Overfitting Effect:**  
   Complex ML meta-classifiers (R4 HGB, R3 RF, R-SELECTIVE) appear to overfit on the 760-match training set ($54.2\%$ on Validation), and lose $\sim 4$ decisions on Holdout. Simple, regularized ensemble voting remains the most robust strategy.

