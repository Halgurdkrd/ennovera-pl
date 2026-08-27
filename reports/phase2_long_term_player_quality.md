# ENNOVERA PHASE 2 — LONG-TERM PLAYER QUALITY MODEL
## Multi-Season Memory & Reliability Shrinkage

- **Multi-Season Window:** Recency-weighted EWMA across up to 3 seasons (0.60 * t-1 + 0.30 * t-2 + 0.10 * t-3).
- **Reliability Shrinkage:** lambda(mins) = mins / (mins + 600.0). Players with <600 minutes are safely shrunk towards positional price priors.
- **Positional Baselines:** GK: 3.5, DEF: 3.8, MID: 4.5, FWD: 4.8 pts/90.
