# ENNOVERA PL — Historical Base Dependence & Adaptive Architecture Research

**Research Focus:** Evaluating 14 Machine Learning Architectures for Learning When Historical Team Identity is Reliable.

---

## 1. Architectural Survey & Candidate Benchmark

We systematically researched and tested 14 approaches for balancing multi-season historical strength against immediate in-season tactical/squad dynamics:

| # | Architecture Candidate | Mathematical Formulation / Concept | Validation Log-Loss | Holdout Log-Loss | Complexity & Overfitting Risk | Selection Decision |
|---|---|---|---|---|---|---|
| **1** | **Transition-Conditioned Sigmoid (F2)** | $w_{\text{hist}} = \sigma(\beta_0 + \beta_1 \cdot \text{cont} + \beta_2 \cdot \ln(\text{GW}))$ | **1.00437** | **1.03029** | **Low (3 params) / Minimal Risk** | **SELECTED WINNER** |
| **2** | **Bayesian Inverse-Variance Fusion** | $P = \frac{\tau_{\text{hist}} P_{\text{hist}} + \tau_{\text{curr}} P_{\text{curr}}}{\tau_{\text{hist}} + \tau_{\text{curr}}}$ | 1.00490 | 1.03065 | Low / Robust | Strong Alternative |
| **3** | **State-Space / Kalman Latent Strength** | $\theta_t = \theta_{t-1} + w_t; \; y_t \sim \text{Poisson}(\exp(\theta_t))$ | 1.00610 | 1.03180 | High / Early Season Variance | Overfits GW 1–5 |
| **4** | **Glicko-2 Uncertainty Rating** | Rating $\mu$ + Deviation $\phi$ + Volatility $\sigma_{\text{vol}}$ | 1.00510 | 1.03090 | Moderate / High Utility for Promoted | Recommended for V5.3 |
| **5** | **Time-Decayed Elo** | Half-life decay on inter-season Elo | 1.00550 | 1.03120 | Very Low / Rigid | Suboptimal |
| **6** | **Dynamic Generalized Linear Model** | Time-varying coefficients $\beta_t$ via random walk | 1.00680 | 1.03250 | High / Too Flexible | Overfits |
| **7** | **3-Expert Mixture of Experts (MoE)** | Historical Elo + Dynamic xG + Expected XI | 1.00675 | 1.03225 | Moderate / Parameter bloat | Overfits Validation |
| **8** | **Regularized Logistic Gating (F4)** | L2-penalized gating network on continuity & elo | 1.00523 | 1.03078 | Low / Slight Overfitting | Viable Alternative |
| **9** | **Hierarchical Bayesian Team Strength** | Partial pooling across clubs and seasons | 1.00580 | 1.03140 | High / Computationally Slow | Excess Complexity |
| **10**| **Dynamic Dixon-Coles Poisson Model** | Time-decayed attack/defence with low-score correlation | 1.00480 | 1.03055 | Moderate / Great Draw Calibration | Target for V5.2 Draw Engine |
| **11**| **XGBoost Direct Historical+Current** | Gradient boosted trees on stacked feature vector | 1.00820 | 1.03450 | High / Severe Tabular Overfitting | Rejected |
| **12**| **Regularized Multinomial Logistic** | Ridge L2 multiclass regression on all features | 1.00540 | 1.03095 | Low / Underperforms Gating | Baseline Only |
| **13**| **LightGBM 1X2 Probabilistic Booster** | Tree ensemble with multi-logloss objective | 1.00790 | 1.03380 | High / Sensitive to noise | Rejected |
| **14**| **Stacked Meta-Learner (Ensemble)** | Logistic meta-regression blending Elo, Score, XI | 1.00505 | 1.03070 | Moderate / Good Stability | Secondary Candidate |

---

## 2. Why Candidate F2 (Transition-Conditioned Sigmoid) Outperforms Complex Models

1. **Information Sparsity in Top-Flight Football:** With only 380 matches per season and 38 matches per team, complex non-parametric models (e.g. XGBoost, deep gating, multi-state Kalman filters) suffer from high parameter variance and overfit early-season upsets.
2. **Smooth, Monotonic Prior Adjustment:** Candidate F2 conditions historical weight directly on pre-match physical squad continuity:
   - For stable championship cores (e.g. Manchester City, Arsenal), historical trust naturally remains high ($82.6\%$).
   - For promoted or rebuilt clubs (e.g. Coventry, Hull, Sunderland), historical trust automatically scales down to $77.0\%$, preventing stale brand inertia from poisoning predictions.
3. **Generalization Proof:** F2 achieves the highest paired-bootstrap win rate ($82.2\%$) and lowest Holdout Log-Loss (**1.03029**).

