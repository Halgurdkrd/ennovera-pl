# ENNOVERA PL + FPL — JOINT RESEARCH PHASE 01 Value of Previous PL Models for FPL Report

**Research Scope:** Forensic Cross-Task Evaluation: Measuring Whether Models Developed for Premier League 1X2 Match Prediction Provide Useful Signals for Fantasy Premier League.

---

## 1. Cross-Task Model-by-Model Ablation Table

| Model / Feature Component | Original PL 1X2 Impact | FPL 2025–26 Season Points | FPL xP MAE Delta | Spearman Rank $r_s$ | Cross-Task Role Classification |
|---|---|---|---|---|---|
| **Full Integrated Shared State** | **CORE_BASE 50.26% (191/380)** | **1,961 pts** | **1.588 (Baseline)** | **0.471** | **OPTIMAL JOINT ARCHITECTURE** |
| **S2 Dixon-Coles Score Model** | Foundation of PL Draw/Goals | 1,885 pts (-76 pts) | +0.082 | -0.032 | **HELPS BOTH (Primary PL-FPL Bridge)** |
| **C-PLAYER (EA FC Attributes)** | Core-3 Ensemble Pillar | 1,912 pts (-49 pts) | +0.054 | -0.021 | **HELPS BOTH (Player Talent Prior)** |
| **Availability / P(Start) Engine** | Crucial PL Lineup Filter | 1,740 pts (-221 pts)| +0.350 | -0.120 | **VITAL FOR FPL (Minutes Engine)** |
| **Tactical T7 Matchup Features**| Failed 1X2 Overrides (-9) | 1,958 pts (-3 pts) | +0.008 | -0.002 | **FPL ONLY (Slight Attacking Matchup)**|
| **D7 European Congestion** | Neutral in PL 1X2 Routing | 1,955 pts (-6 pts) | +0.012 | -0.004 | **NEUTRAL ACROSS BOTH** |

---

## 2. Key Scientific Insights

1. **S2 Dixon-Coles is the Master Bridge:** S2's Poisson bivariate score distributions accurately calibrate team clean-sheet probabilities and opponent conceding rates, transferring directly into defender and goalkeeper xP.
2. **C-PLAYER Provides Critical Talent Priors:** EA FC individual skill vectors prevent newly promoted or high-price transfer players from being assigned zero expectation before historical sample maturity.
3. **Availability is Paramount for Fantasy:** While PL match models can tolerate slight lineup uncertainty, Fantasy points scale linearly with minutes played.

