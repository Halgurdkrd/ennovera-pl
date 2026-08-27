# ENNOVERA PHASE 10.5 — COUNT DISPERSION REVALIDATION

```csv
r_goal,nll,crps,brier_2plus,tail_coverage,decision
1.65,0.428,0.312,0.0628,93.8%,OVERDISPERSED
1.85,0.422,0.308,0.0615,95.1%,CURRENT CONTROL
1.95,0.418,0.304,0.0608,95.8%,PROMOTE_NEW_VALUE (Analytic ML Estimate)
2.15,0.424,0.309,0.0618,94.6%,UNDERDISPERSED

```
```csv
r_assist,nll,crps,brier_2plus,tail_coverage,decision
1.5,0.384,0.282,0.0485,94.2%,OVERDISPERSED
1.65,0.376,0.276,0.0472,95.6%,PROMOTE_NEW_VALUE (Analytic ML Estimate)
1.85,0.382,0.28,0.048,95.0%,CURRENT CONTROL (Goal Shared Proxy)

```

## Scientific Findings
- Separate statistical ML estimation for goals ($r=1.95$) and assists ($r=1.65$) improves NLL and CRPS tail calibration.
- **Decision:** **PROMOTE_NEW_VALUE (r_goal=1.95, r_assist=1.65)**.
