# ENNOVERA PL — M3 Baseline Integrity Check Report

**Audit Objective:** Verification and canonicalization of existing predictive baselines (Canonical F2, M1-D Adaptive Transition Specialist, and M2 S1 Simulation) prior to M3 research design.

---

## 1. Frozen Baseline Verification from Local Source Artifacts

Verified from `data/experiments/m1_canonical_f2_comparison.json`, `data/experiments/m2_model_comparison.csv`, and reproducible walk-forward evaluation:

| Baseline Model Candidate | Primary Role & Status | Development LL (22–24) | Validation LL (24–25) | Holdout LL (25–26) | Holdout Accuracy (25–26) | Strong Picks $\ge 60\%$ Precision | Strong Pick Coverage |
|---|---|---|---|---|---|---|---|
| **Canonical F2** | **Frozen Master Anchor** | **0.96798** | **1.00326** | **1.02999** | **48.42% (184/380)** | **67.27% (37/55)** | **14.5% (55 picks)** |
| **Candidate M1-D** | **Adaptive Transition Specialist**| **0.96340** | **0.99918** | **1.02940** | **48.16% (183/380)** | **64.62% (42/65)** | **17.1% (65 picks)** |
| **Candidate M2 (Standalone)**| **REJECTED AS MATCH PREDICTOR** | 0.96478 | 1.09225 | 1.09439 | 43.16% (164/380) | 54.55% (96/176) | 46.3% (176 picks) |
| **Candidate M2 (S1 Sim)** | **RETAINED FOR CHAMPIONSHIP SIM**| N/A | N/A | N/A | $\sigma = 7.2\text{ pts}$ | Man City: 46.8% | Arsenal: 33.5% |

---

## 2. Definitive Guidelines for M3 Pre-Implementation

1. **M2 Standalone Score Predictor is Formally Excluded:**  
   M2's Poisson score model underperforms F2 by $+0.06440$ Log-Loss points ($P(\text{M2 Better}) = 0.0\%$) and will not be used for 1X2 match betting.
2. **S1 Latent Season-State Uncertainty is Formally Retained:**  
   The season-level latent uncertainty perturbation ($\tau_{\text{season}} \sim \mathcal{N}(0, 0.080^2)$) remains the canonical championship simulation engine.
3. **M3 Must Earn Every Gain Over F2 (1.02999) and M1-D (1.02940):**  
   All M3 experiments must benchmark directly against Canonical F2 and M1-D without tuning on 2025–26.

