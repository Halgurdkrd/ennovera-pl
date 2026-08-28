# ARCHITECTURE EQUIVALENCE & COMPARISON MATRIX

| Component | Final Control (`ENNOVERA_PL_FINAL_RESEARCH_V1`) | Pure Ablation (Minus Expected XI) | Historical Sprint A Checkpoint (`PL11_3`) |
| :--- | :--- | :--- | :--- |
| **Expected XI / Replacement Quality** | Active (P(start) x Quality) | **Disabled (Uniform Prior)** | Disabled (Uniform Prior) |
| **Dynamic Bayesian Team State** | Active (Poisson State) | Active (Poisson State) | Disabled (Static Base) |
| **Dixon-Coles Score Correlation** | Active (Copula $\rho$) | Active (Copula $\rho$) | Disabled (Independent Poisson) |
| **Dirichlet Probability Calibration** | Active (3-Class Calibrated) | Active (3-Class Calibrated) | Uncalibrated Softmax |
| **Canonical 3-Class Accuracy** | **58.4%** | **57.1%** | **56.2%** |
| **Ranked Probability Score (RPS)** | **0.1748** | **0.1824** (+0.0076) | **0.1895** (+0.0147) |
| **Multiclass Log Loss** | **0.8680** | **0.8870** | **0.9180** |
