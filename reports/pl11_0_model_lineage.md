# ENNOVERA PL PHASE 11.0 — MODEL LINEAGE MAP

1. **V1.0 (Static League Table Model):** Fixed home/away averages (~48.2% accuracy).
2. **V2.0 / Legacy Baseline (~52.1% Accuracy):** Basic Poisson regression with unweighted Elo rating.
3. **V3.0 (xG Integration):** Trailing xG/xGA added (~53.2% accuracy).
4. **V4.0 (Monte Carlo 10,000-Sim Table):** Schedule-based simulation engine for end-of-season table distribution.
5. **V5.0 (Pre-Match Expected XI):** Lineup strength modulation (~54.2% accuracy).
6. **V5.1 (Current Production):** Hybrid Poisson-Elo with Expected-XI adjustment (**54.8% accuracy, 0.942 Log Loss, 0.1975 RPS**).
