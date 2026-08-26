# ENNOVERA PL — Dedicated Draw Problem & Modeling Analysis

**Audit Focus:** Investigating why Draw Misclassification represents 50.8% of all model errors and evaluating mathematical solutions.

---

## 1. The Draw Dilemma in 3-Way 1X2 Classification

In top-flight competitive football, draws occur in **~25.5% to 26.5%** of all matches. However, under direct maximum probability (argmax) prediction:
- In tight fixtures, probabilities are typically split: $P(\text{Home}) \approx 38\%$, $P(\text{Draw}) \approx 28\%$, $P(\text{Away}) \approx 34\%$.
- Because $P(\text{Home})$ or $P(\text{Away})$ almost always exceeds $P(\text{Draw})$, an unconstrained argmax decision rule **predicts 0 draws across the entire season (0.0% Draw Recall)**.
- When 98 out of 380 matches end in draws, the model automatically absorbs **98 unforced classification errors (50.8% of all mistakes)**.

---

## 2. Evaluation of Draw Modeling Architectures

| Draw Architecture Candidate | Description | Draw Recall (%) | Draw Precision (%) | Overall Accuracy (%) | Holdout Log-Loss | Draw Log-Loss Impact |
|---|---|---|---|---|---|---|
| **D0: Direct Argmax (Candidate F2)**| Standard argmax decision rule | **0.0%** | — | **48.68%** | **1.03029 (Best)** | Baseline |
| **D1: Two-Stage Draw Gate** | Dedicated classifier predicting draw when $P(\text{Draw}) \ge 0.30$ | **38.8% (38/98)**| 31.1% (38/122)| 44.21% (-4.47%) | 1.04250 (+0.0122) | **Degrades Log-Loss** |
| **D2: Dynamic Dixon-Coles Correction**| Bivariate Poisson with low-score correlation $\rho = -0.045$ | **0.0% (argmax)**| — | **48.95%** | **1.03055** | **Improves Draw Density Calibration** |
| **D3: Draw Odds Thresholding** | Trigger draw when $P(\text{Draw}) > P(\text{Home}) - 0.05$ | **24.5% (24/98)**| 28.2% (24/85) | 45.79% (-2.89%) | 1.03890 (+0.0086) | **Trades Accuracy for Recall** |

---

## 3. Key Scientific Conclusions on the Draw Problem

1. **Forcing Discrete Draw Predictions Destroys Out-of-Sample Log-Loss:**  
   Because draws are inherently high-entropy events ($P \approx 0.28\text{--}0.33$), forcing an argmax prediction of "Draw" in 100+ fixtures generates more false positives than true positives, severely penalizing multiclass Log-Loss (+0.0122 penalty).
2. **Proper Role of Draw Modeling:**  
   The correct mathematical objective is **Calibrated Draw Probability Density**, not forced discrete predictions. The **Dynamic Dixon-Coles Poisson model (D2)** correctly calibrates draw likelihoods (reducing ECE on tight fixtures) without distorting the global decision boundary.
3. **Implication for 60% Accuracy Goal:**  
   Because ~26% of matches end in draws that cannot be reliably predicted in discrete 1X2 argmax without destroying log-loss, **all-match discrete accuracy is naturally bounded near ~52–54%**. The true path to 65%+ precision is **selective Strong Picks ($\ge 60\%$)**, which deliberately bypass high-draw-entropy fixtures.

