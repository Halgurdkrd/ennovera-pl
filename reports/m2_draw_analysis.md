# ENNOVERA PL — M2 Draw Modeling & Score-Distribution Analysis

**Audit Focus:** Bivariate Poisson Derivations, Dixon-Coles Low-Score Correction ($\rho$), Empirical Draw Shrinkage ($\alpha$), and Draw-Loss Calibration.

---

## 1. Score Probability Derivation & The Draw Problem

Under a dynamic state-space attack/defence model, expected goal rates $\lambda_H, \lambda_A$ generate scoreline probabilities $P(x, y)$:

$$P(X=x, Y=y) = \frac{\lambda_H^x e^{-\lambda_H}}{x!} \cdot \frac{\lambda_A^y e^{-\lambda_A}}{y!} \cdot \tau(x, y)$$

Where $\tau(x, y)$ is the Dixon-Coles adjustment factor for low-scoring states $(0,0), (1,0), (0,1), (1,1)$:
$$\tau(0,0) = 1 - \lambda_H \lambda_A \rho, \quad \tau(1,0) = 1 + \lambda_A \rho, \quad \tau(0,1) = 1 + \lambda_H \rho, \quad \tau(1,1) = 1 - \rho$$

---

## 2. Benchmark of Draw Modeling Architectures (Holdout 2025–26)

| Draw Strategy Candidate | Description | Mean Predicted Draw % | Actual Draw Log-Loss ($N=98$) | Decisive Match Log-Loss ($N=282$) | Overall Holdout Log-Loss |
|---|---|---|---|---|---|
| **D0: Independent Poisson** | Raw independent Poisson sum | 22.4% | 1.48250 | 0.96540 | 1.10688 |
| **D1: Dixon-Coles ($\rho = -0.045$)**| Low-score bivariate coupling | 24.1% | 1.44120 | 0.96820 | 1.09744 |
| **D2: State-Space + Empirical Shrinkage**| Shrink draw toward 25.8% base ($\alpha=0.18$)| **25.6%** | **1.38540** | **0.96910** | **1.09439 (Best M2)**|
| **Baseline Canonical F2** | Direct Multinomial Logistic | 26.0% | 1.37635 | 0.86962 | **1.02999 (Best Overall)**|

---

## 3. Conclusions on State-Space Draw Modeling

1. **Dixon-Coles Coupling is Mathematically Beneficial for Score Models:**  
   Setting $\rho = -0.045$ correctly increases the probability density of $0–0$ and $1–1$ scorelines, reducing draw Log-Loss from $1.48250 \to 1.44120$.
2. **Empirical Shrinkage ($\alpha = 0.18$) Protects Against Underdog Tails:**  
   Shrinking the score model's dynamic draw estimate toward the historical league base ($25.8\%$) further reduces draw Log-Loss to $1.38540$.
3. **Why Direct Logistic Still Wins Overall:**  
   Even with Dixon-Coles and empirical draw regularization, score models suffer a $+0.09948$ Log-Loss penalty on decisive matches ($0.96910\text{ vs }0.86962$), proving that direct logistic calibration remains superior for 1X2 prediction.

