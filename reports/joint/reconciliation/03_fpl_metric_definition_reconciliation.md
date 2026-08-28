# R2: FPL METRIC UNIVERSE RECONCILIATION

## Root Cause of Metric Discrepancy
- **Phase 10.6 Canonical Universe (`CANONICAL_MANAGER_POOL_TOP20`):** Evaluates the top 20 projected players in each gameweek ($N=3,040$ player-GWs). Because high-variance premium captaincy candidates dominate this pool, absolute MAE is higher (1.745), and haul recall inside the selection pool is high (Recall@20 = 61.8%).
- **J1 Previous Reporting Universe (`SECONDARY_ALL_STARTING_PLAYERS`):** Evaluated all 220 starting players in the league per gameweek ($N=33,440$ player-GWs). Low baseline scores across defensive and non-attacking starters pull average MAE down to 1.412, and overall event recall across all starters to 38.4%.

## Recomputed Apples-to-Apples Canonical Metrics
1. **MAE:** Control 1.745 $\to$ Challenger **1.732** ($\Delta = -0.013$)
2. **Spearman Rank Correlation:** Control 0.7845 $\to$ Challenger **0.7892** ($\Delta = +0.0047$)
3. **NDCG@20:** Control 0.7915 $\to$ Challenger **0.7960** ($\Delta = +0.0045$)
4. **10+ Haul Recall@20:** Control 61.8% $\to$ Challenger **62.9%** ($\Delta = +1.1\%$)
5. **15+ Mega-Haul Recall@20:** Control 54.2% $\to$ Challenger **55.4%** ($\Delta = +1.2\%$)
6. **Top Scorer Recall@20:** Control 82.5% $\to$ Challenger **83.2%** ($\Delta = +0.7\%$)

## Standardized FPL Scoring Universe Verification
Manager points are verified strictly under standardized historical scoring rules:
- **Control Historical Mean:** **2,179.50 pts/season** (2022-23: 2091, 2023-24: 2120, 2024-25: 2199, 2025-26: 2308)
- **J1 Challenger Historical Mean:** **2,183.00 pts/season** (2022-23: 2095, 2023-24: 2123, 2024-25: 2203, 2025-26: 2311)

## Status: `METRICS_VALID_DIFFERENT_UNIVERSE` (Reconciled to Canonical Top-20 Standard)
