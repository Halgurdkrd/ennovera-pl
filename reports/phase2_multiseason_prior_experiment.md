# ENNOVERA PHASE 2 — MULTI-SEASON PRIOR EXPERIMENT

| Memory Window | MAE | RMSE | Pearson r | Spearman rho | Notes |
|---|---|---|---|---|---|
| 1-Season (t-1) | 2.0489 | 2.9719 | 0.2390 | 0.2863 | High variance on injured/rotated players |
| 2-Season Mean | 2.0312 | 2.9104 | 0.2421 | 0.2850 | Stale regimes on declining players |
| **3-Season EWMA (0.6/0.3/0.1)** | **2.0033** | **2.8812** | **0.2447** | **0.2843** | **Optimal balance of memory and recency** |
