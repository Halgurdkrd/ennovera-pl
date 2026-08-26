# ENNOVERA PL — M1 Blending Optimization & Weight Stability Report

**Audit Focus:** Static Weight Optimization Grid, 1,000 Development Bootstraps, Gating Parameter Stability, and Overfitting Dynamics.

---

## 1. Static Blend Weight Optimization Grid (Development 2022–24)

| Elo Weight ($w_{\text{elo}}$) | Player Weight ($w_{\text{player}}$) | Development Log-Loss (22–24) | Validation Log-Loss (24–25) | Holdout Log-Loss (25–26) | Generalization Verdict |
|---|---|---|---|---|---|
| **0.0 (0% Elo)** | **1.0 (100% Player)** | **0.94878 (In-Sample Best)**| **0.99448 (Val Best)** | **1.03783 (Degraded)** | **Overfits Holdout (+0.00784)** |
| **0.1 (10% Elo)** | 0.9 (90% Player) | 0.94928 | 0.99450 | 1.03690 | Overfits Holdout |
| **0.3 (30% Elo)** | 0.7 (70% Player) | 0.95110 | 0.99480 | 1.03510 | Overfits Holdout |
| **0.5 (50% Elo)** | 0.5 (50% Player) | 0.95391 | 0.99590 | 1.03340 | Balanced |
| **0.8 (80% Elo)** | 0.2 (20% Player) | 0.95980 | 1.00010 | **1.03050 (Holdout Robust)** | **Holdout Safe** |
| **1.0 (100% Elo)**| 0.0 (0% Player) | 0.96478 | 1.00277 | **1.02979** | Baseline |

---

## 2. 1,000 Bootstrap Resamples of Optimal Static Blend Weight

Evaluating the stability of the numerical optimizer across 1,000 random resamples of the Development partition:

| Selected Elo Weight Bracket | Bootstrap Frequency (%) | Mean Selected Weight | Interpretation |
|---|---|---|---|
| **0% – 20% Elo (Heavy Player Model)** | **92.8%** | **0.06 Elo / 0.94 Player** | **Optimizer aggressively exploits player in-sample sharpness** |
| **20% – 40% Elo** | 6.6% | 0.28 Elo / 0.72 Player | Moderate blend |
| **40% – 60% Elo** | 0.6% | 0.48 Elo / 0.52 Player | Balanced blend |
| **60% – 100% Elo** | 0.0% | — | Never selected in-sample |

### Why Static Global Blending Fails Out-of-Sample:
- In-sample, the 11-feature Player Model fits training data with a **0.94878 Log-Loss** (0.01600 sharper than Elo), leading unregularized static optimizers to set $w_{\text{player}} = 1.0$.
- Out-of-sample, individual player metrics encounter early-season variance and squad rotation, giving a Holdout Log-Loss of **1.03783** (+0.00784 penalty vs F2).
- **Conclusion:** Static global blending is statistically unstable. **Adaptive Gating (M1-D)** is mathematically required to confine high player reliance strictly to transition squads while preserving 85–90% Elo on stable title contenders.

---

## 3. Gating Coefficient Stability Audit

The M1-D gating network employs 4 coefficients:
$$\text{Gate Logit} = 1.80 \cdot \text{Continuity} - 1.20 \cdot \text{Promoted} - 0.90 \cdot \text{Uncertainty} + 0.40 \cdot \ln(\max(1, \text{GW}))$$

| Coefficient | Parameter Role | Learned Range | Bootstrap 95% CI | Stability Verdict |
|---|---|---|---|---|
| **$\beta_{\text{cont}} = +1.80$** | Retain Elo for stable squads | `[+1.40, +2.20]` | `[+1.45, +2.15]` | **HIGHLY STABLE** |
| **$\beta_{\text{prom}} = -1.20$** | Reduce Elo for promoted clubs | `[-1.50, -0.90]` | `[-1.48, -0.88]` | **HIGHLY STABLE** |
| **$\beta_{\text{unc}} = -0.90$** | Dampen weight on high uncertainty | `[-1.20, -0.60]` | `[-1.15, -0.65]` | **STABLE** |
| **$\beta_{\text{gw}} = +0.40$** | Gradually increase Elo as GW grows | `[+0.20, +0.60]` | `[+0.22, +0.58]` | **STABLE** |
