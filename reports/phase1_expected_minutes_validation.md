# ENNOVERA PHASE 1 — EXPECTED MINUTES VALIDATION
## Historical Calibration across 113,592 Player-Match Instances

- **Expected Minutes MAE:** 13.24 minutes
- **R^2 Variance Explained:** 0.5756
- **P(Start / 60+ Mins) Classification Accuracy:** 86.16%
- **Formulation:** Multi-head rolling EWMA (0.60 * roll_mins_3 + 0.40 * roll_mins_5) blended with fitness status and price prior.
