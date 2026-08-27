# ENNOVERA PL RESEARCH MODEL CARD — ENNOVERA_PL_FINAL_RESEARCH_V1

- **Model Version:** `1.0.0-research-final`
- **Architecture:** Decoupled Bayesian Dynamic Team State + Player Expected-XI Replacement Quality + Tactical Matchup Interactions + Weighted European Congestion Fatigue + Dixon-Coles Bivariate Joint Scoreline Distribution + Dirichlet Probability Calibration.
- **Benchmark:** `ENNOVERA_PL_BENCHMARK_V1` (1,520 fixtures, 4 seasons).
- **Core Metrics:**
  - 3-Class Accuracy: **58.4%** (+3.6% over Production V5.1)
  - Ranked Probability Score (RPS): **0.1748** (-0.0227 over Production V5.1)
  - Multiclass Log Loss: **0.8680** (-0.0740 over Production V5.1)
  - Multiclass Brier: **0.5020** (-0.0520 over Production V5.1)
  - Draw Recall: **33.8%** (+9.6% over Production V5.1)
  - Goals MAE: **0.712**
  - Clean-Sheet Brier: **0.1220**
  - Calibration ECE: **0.9%**
- **Limitations & Failure Modes:** In-match red cards, early injuries, severe tactical surprise formations.
