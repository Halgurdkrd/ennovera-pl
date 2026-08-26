# ENNOVERA PL — Championship Tournament Mathematics Audit

**Audit Focus:** Analytical Derivation of Title Probability vs Multi-Team Simulator Dynamics.

---

## 1. Formal Mathematical Derivation (Analytical Two-Team Tournament)

Let final points for two title contenders be modeled as normal random variables:
$$A \sim \mathcal{N}(\mu_A, \sigma_A^2), \quad B \sim \mathcal{N}(\mu_B, \sigma_B^2)$$

The difference between their season points follows:
$$D = A - B \sim \mathcal{N}\left(\mu_A - \mu_B, \; \sigma_A^2 + \sigma_B^2 - 2\operatorname{Cov}(A,B)\right)$$

The probability that Team A finishes ahead of Team B is given analytically by the standard normal CDF:
$$P(A > B) = \Phi\left(\frac{\mu_A - \mu_B}{\sqrt{\sigma_A^2 + \sigma_B^2 - 2\operatorname{Cov}(A,B)}}\right)$$

---

## 2. Analytical Head-to-Head Probability Matrix

Table of $P(A > B)$ across points variance ($\sigma$) and expected points gap ($\Delta \mu = \mu_A - \mu_B$), assuming direct match correlation $\operatorname{Cov}(A,B) = -0.10 \sigma^2$:

| Points Std Dev ($\sigma$) | $\Delta \mu = 0$ | $\Delta \mu = 1$ | $\Delta \mu = 2$ | $\Delta \mu = 3$ | $\Delta \mu = 5$ | $\Delta \mu = 10$ |
|---|---|---|---|---|---|---|
| **$\sigma = 4.0$** | 50.00% | 56.69% | 63.20% | 69.34% | 80.03% | 95.41% |
| **$\sigma = 5.0$** | 50.00% | 55.36% | 60.63% | 65.71% | 74.99% | 91.12% |
| **$\sigma = 6.0$ (Empirical PL)**| **50.00%** | **54.47%** | **58.89%** | **63.20%** | **71.29%** | **86.94%** |
| **$\sigma = 7.0$** | 50.00% | 53.84% | 57.64% | 61.37% | 68.49% | 83.23% |
| **$\sigma = 8.0$** | 50.00% | 53.36% | 56.69% | 59.98% | 66.33% | 80.03% |
| **$\sigma = 10.0$** | 50.00% | 52.69% | 55.36% | 58.01% | 63.20% | 74.99% |

---

## 3. Comparison: Analytical Rate vs Multi-Team Simulator Rate

For a $+1.0\text{ xPts}$ expected points advantage at empirical Premier League variance ($\sigma = 6.1$):
- **Analytical Head-to-Head Margin:** $\Phi(1.0 / \sqrt{2 \times 6.1^2 \times 1.1}) = 54.40\% \text{ vs } 45.60\% \implies \mathbf{+8.80\text{pp}}$ margin.
- **Multi-Team Simulator Margin:** City $52.26\% \text{ vs Arsenal } 43.38\% \implies \mathbf{+8.87\text{pp}}$ margin.

> [!TIP]
> **Audit Finding:**  
> The observed rate of **$\sim 8.8\text{ to }10.5\text{ percentage points per xPt}$** is the exact analytical behavior of the normal CDF in a two-horse title race. It is **mathematically sound**, not a simulation bug.

---

## 4. Simulator Variance vs Historical Premier League Variance

- **Historical PL Top-2 Points Standard Deviation:** $\sigma \approx 6.0\text{--}6.5\text{ points}$.
- **Current Simulator Top-2 Points Standard Deviation:** $\sigma = 6.12\text{ points}$.
- **Assessment:** The simulator's points standard deviation closely matches historical variance. To prevent over-sensitivity during in-season updating, future simulation iterations (V5.2/V5.3) will incorporate latent team-level form shocks.

