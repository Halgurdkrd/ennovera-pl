# ENNOVERA PHASE 10.5 — ROBUST HAUL BLEND alpha REVALIDATION

```csv
alpha_pts,nested_val_score,xp_mae,haul_recall_20,single_haul_stress,decision
0.35,2171.8,1.768,59.1%,EXCELLENT,STRONG CANDIDATE
0.4,2172.0,1.765,59.5%,OPTIMAL,PROMOTE_NEW_VALUE (+1.5 pts)
0.45,2171.2,1.77,59.4%,GOOD,VALIDATED
0.5,2170.5,1.775,59.4%,CURRENT BASELINE,CURRENT CONTROL
0.55,2169.6,1.782,58.8%,MODERATE NOISE,REJECT
0.6,2168.4,1.795,58.1%,HIGH NOISE,REJECT
0.65,2166.8,1.81,57.2%,OVERFITTING NOISE,REJECT

```

## Scientific Findings
- With Phase 10.1 introducing explicit shot conversion decomposition, reducing points weight from $\alpha=0.50 \to \mathbf{0.40}$ improves out-of-fold generalization.
- Standalone manager gain: **+1.50 pts/season**.
- **Decision:** **PROMOTE_NEW_VALUE (\alpha=0.40)**.
