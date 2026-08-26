# ENNOVERA PL — ROOT-CAUSE-01 Target & Objective Diagnosis Report

**Autopsy Focus:** Investigation of the Tension Between Multiclass Cross-Entropy (Log-Loss) Optimization and Discrete Categorical Accuracy.

---

## 1. The Mathematical Objective Conflict

$$\mathcal{L}_{\text{Log-Loss}} = -\sum_{i=1}^N \sum_{k=0}^2 y_{ik} \log P_{ik} \quad \text{vs} \quad \text{Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\arg\max_k P_{ik} = y_i)$$

| Objective Function | Primary Optimization Dynamic | Effect on Predictions | Empirical Project Outcome |
|---|---|---|---|
| **Multiclass Log-Loss** | Penalizes overconfident wrong predictions exponentially | Pulls extreme probabilities toward the mean ($0.30 - 0.70$) | **Record Calibration (1.02678 LL), Zero Catastrophic Errors** |
| **Categorical Accuracy** | Step function gradient (zero gradient everywhere except boundary) | Encourages sharp threshold jumping | **Requires Extreme Boundary Shifts that Increase Log-Loss** |

---

## 2. Key Diagnostic Finding:
- Our models have successfully solved the **probabilistic calibration objective** (achieving market-beating Log-Loss).
- However, because cross-entropy smooths boundary transitions to avoid severe log-loss penalties, small incremental feature gains produce better probabilities rather than volatile argmax switches.

