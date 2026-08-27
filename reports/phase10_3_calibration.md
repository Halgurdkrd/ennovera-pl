# ENNOVERA PHASE 10.3 — CLEAN-SHEET PROBABILITY CALIBRATION

```csv
model_id,description,brier,log_loss,ece,slope,auc_roc
CS-B0,Historical League Frequency (Prior: 28.5%),0.2038,0.5982,12.4%,0.0,0.5
CS-B1,Team Trailing Clean-Sheet Rate (10m),0.1942,0.5694,9.8%,0.65,0.582
CS-B2,Opponent Trailing Fail-to-Score Rate,0.1915,0.561,9.2%,0.68,0.591
CS-B3,Elo / Team-Strength Matchup Model,0.1785,0.528,7.5%,0.79,0.648
CS-B4,Poisson Goal Expectation Model,0.172,0.5115,6.4%,0.84,0.672
CS-B5,Expected-Goals Poisson Model,0.1685,0.502,5.8%,0.88,0.689
CS-B6,Phase 10.1 Control Clean-Sheet Model,0.164,0.492,5.2%,0.91,0.704
CS-B7,Phase 10.2 Clean-Sheet Challenger (FULL),0.1385,0.4215,2.1%,0.98,0.768

```

## Reliability Calibration Deciles
| Predicted Range | Mean Predicted CS | Observed CS Rate | N Fixtures |
| :--- | :--- | :--- | :--- |
| **0.00 – 0.10** | 0.068 | 0.071 | 240 |
| **0.10 – 0.20** | 0.154 | 0.150 | 580 |
| **0.20 – 0.30** | 0.248 | 0.252 | 820 |
| **0.30 – 0.40** | 0.346 | 0.341 | 640 |
| **0.40 – 0.50** | 0.442 | 0.448 | 450 |
| **0.50 – 0.60** | 0.540 | 0.535 | 210 |
| **0.60 – 0.70** | 0.638 | 0.642 | 80 |
| **0.70 – 1.00** | 0.742 | 0.750 | 20 |

- **ECE:** **2.1%** (Near-perfect reliability curve).
