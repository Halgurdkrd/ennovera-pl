# ENNOVERA PHASE 5.3 — REGRET DECOMPOSITION REPORT

```csv
category,fpl03_pts,phase4_pts,phase5_pts
Prediction Regret (Unrealized Points vs Oracle xP),245,198,184
Selection Regret (Starting XI vs Bench Hauls),124,104,92
Captain Regret (Captain vs Optimal Owned Asset),94,82,78
Transfer Regret (Sold Player Hauls vs Bought Blanks),62,48,42
Chip Regret (Suboptimal Chip Gameweek Timing),48,38,34
Bench Regret (Points Trapped on Bench),36,28,26

```

## Primary Vulnerability Analysis for Phase 6
- **Prediction Regret (184 pts) & Selection Regret (92 pts):** Driven by variance in extreme ceiling hauls where point xP under-weights upside relative to median outcomes.
- **Phase 6 Recommendation:** Focus on **Outcome Distribution Modeling (Poisson / Negative Binomial Mixture)** and **Haul Probability Engine** rather than mean xP tuning.
