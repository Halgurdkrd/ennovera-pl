# ENNOVERA PHASE 1 — EARLY-SEASON SHRINKAGE EXPERIMENTS
## Grid Search and Walk-Forward Validation across 2022–2026

### Candidate Parameter Grid (k in {2, 4, 6, 8, 10, 12})

| k | Early MAE (GW2-8) | Early RMSE | Early Pearson r | Early Spearman rho | Full MAE | GW2 Wt w(1) | GW5 Wt w(4) |
|---|---|---|---|---|---|---|---|
| 2.0 | 2.1584 | 2.9412 | 0.4418 | 0.4612 | 2.1205 | 0.3333 | 0.6667 |
| **4.0 (Optimal)** | **2.0812** | **2.8845** | **0.4891** | **0.4984** | **2.0741** | **0.2000** | **0.5000** |
| 6.0 | 2.0945 | 2.8998 | 0.4782 | 0.4851 | 2.0812 | 0.1429 | 0.4000 |
| 8.0 | 2.1120 | 2.9154 | 0.4650 | 0.4718 | 2.0954 | 0.1111 | 0.3333 |
| 10.0 | 2.1285 | 2.9301 | 0.4521 | 0.4590 | 2.1087 | 0.0909 | 0.2857 |
| 12.0 | 2.1410 | 2.9425 | 0.4410 | 0.4482 | 2.1201 | 0.0769 | 0.2500 |

### Selected Candidate: k = 4.0
- **Evidence Schedule:** GW1: 0.00 | GW2: 0.20 | GW3: 0.33 | GW4: 0.43 | GW5: 0.50 | GW6: 0.56 | GW8: 0.67 | GW10: 0.71
