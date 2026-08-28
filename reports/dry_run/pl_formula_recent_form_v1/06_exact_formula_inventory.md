# EXACT FORMULA INVENTORY

1. **Latent State Update:** $\theta_{t} = (1 - \alpha)\theta_{t-1} + \alpha (\text{Observed} - \mu)$ with $\alpha = 0.08$.
2. **Match Goal Expectation:** $\lambda_H = \exp(\mu + \gamma + \alpha_H + \beta_A)$, $\lambda_A = \exp(\mu + \alpha_A + \beta_H)$ with $\gamma = 0.24, \mu = 0.12$.
3. **Score Copula:** $\tau(x, y; \rho)$ with $\rho = -0.115$ on low scores (0-0, 1-0, 0-1, 1-1).
4. **Dirichlet Calibration:** $P_{\text{cal}}(y) = \text{Dirichlet}(\mathbf{w}^T \mathbf{z})$.
