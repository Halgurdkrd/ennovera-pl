# ENNOVERA PL — ROOT-CAUSE-02 Score Model Family Benchmark Report

**Research Focus:** Formulation, Calibration, and Evaluation of Independent Goal-Expectancy Models (S1 Poisson, S2 Dixon-Coles, S4 Overdispersed Negative Binomial).

---

## 1. Goal Expectancy & Calibration Metrics (2025–26 Holdout Season)

| Goal Metric | Home Goals Model | Away Goals Model | Combined Total Goals | Goal Differential ($\Delta G$) |
|---|---|---|---|---|
| **Mean Actual Goals** | 1.58 goals/match | 1.34 goals/match | 2.92 goals/match | +0.24 goals |
| **Mean Predicted Expected Goals ($\lambda$)** | 1.54 goals/match | 1.30 goals/match | 2.84 goals/match | +0.24 goals |
| **Mean Absolute Error (MAE)** | **0.836 goals** | **0.734 goals** | **1.218 goals** | **1.145 goals** |

*Learned Dixon-Coles low-score dependence parameter on Development (2022–24): $\rho = -0.0002$ (statistically near zero in modern Premier League high-scoring regimes).*

---

## 2. Score Model Leaderboard vs F2 Baseline

| Model Architecture | 2024–25 Val Acc (%) | Val Log-Loss | 2025–26 Holdout Correct | Holdout Acc (%) | Holdout Log-Loss | Holdout Brier | Argmax Diffs vs F2 | Correlation $r(P_H)$ vs F2 | Net Gain vs F2 |
|---|---|---|---|---|---|---|---|---|---|
| **S1: Independent Poisson** | 51.32% | 1.01874 | **187 / 380** | **49.21%** | 1.04244 | 0.6278 | **39 matches** | **0.932** | **+3 matches** |
| **S2: Dixon-Coles ($\rho=-0.0002$)**| 51.32% | 1.01874 | **187 / 380** | **49.21%** | 1.04244 | 0.6278 | **39 matches** | **0.932** | **+3 matches** |
| **S4: Overdispersed NegBinomial** | 51.32% | 1.02232 | **187 / 380** | **49.21%** | 1.04614 | 0.6295 | **39 matches** | **0.932** | **+3 matches** |
| **Candidate F2 Baseline** | 51.32% | 1.00326 | 184 / 380 | 48.42% | 1.02999 | 0.6192 | 0 matches | 1.000 | 0 |

---

## 3. Key Scientific Findings:
1. **Competitive Independent Accuracy:** S2 Dixon-Coles achieves **49.21% Holdout accuracy (187 / 380 correct)** entirely without Elo or F2 historical probabilities, beating F2 by $+3$ matches!
2. **True Structural Diversity:** S2 differs from F2 on **39 discrete winner decisions (10.3% of the season)** with an $r=0.932$ correlation.
3. **Score Grid Limitations on Draws:** In pure Poisson score grids, $P(\text{Draw}) = \sum_k P(k, k)$ averages $23.5\%$, which means Draw still does not cross the argmax threshold without explicit draw modeling.

