# ENNOVERA PL — M3-DATA-02 Latent Tactical Factors Report

**Audit Focus:** Dimensionality Reduction, Latent Tactical State Factors, and Principal Component Analysis on Development Match Logs.

---

## 1. Latent Tactical Factor Loadings (Fitted on Development 2022–24)

| Latent Tactical Dimension | Underlying Raw Variables | Factor Loading ($\beta$) | Explained Variance (%) | Football Interpretation |
|---|---|---|---|---|
| **Factor 1: Pressing & Turnover Intensity** | $\text{PPDA}$ (Negative)<br>$\text{Tackles in Att 3rd}$<br>$\text{Interceptions}$ | $-0.78$<br>$+0.72$<br>$+0.64$ | **34.5%** | **High-press pressing line (e.g. Man City, Liverpool, Spurs)** |
| **Factor 2: Possession & Territorial Dominance**| $\text{Deep Completions}$<br>$\text{Field Tilt \%}$<br>$\text{Progressive Passes}$ | $+0.84$<br>$+0.81$<br>$+0.76$ | **28.2%** | **Sustained final-third territory (e.g. Arsenal, City)** |
| **Factor 3: Low-Block Resistance** | $\text{Deep Allowed}$ (Negative)<br>$\text{Blocks in Box}$<br>$\text{PPDA Allowed}$ | $-0.74$<br>$+0.68$<br>$+0.62$ | **18.4%** | **Compact defensive shape in box (e.g. Everton, Forest)** |
| **Factor 4: Direct Transition Attack** | $\text{Direct Speed (m/s)}$<br>$\text{Counterattack xG}$ | $+0.79$<br>$+0.71$ | **11.2%** | **Fast vertical counter-attacks (e.g. Brentford, Wolves)** |

---

## 2. Dimensionality Reduction Finding:
- Feeding dozens of raw tactical variables introduces multicollinearity ($r > 0.80$ between possession and pass counts).
- Compressing into **4 orthogonal latent factors** preserves **92.3% of total tactical variance** while stabilizing out-of-time model regularization.

