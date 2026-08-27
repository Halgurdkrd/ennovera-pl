# ENNOVERA PHASE 1 — LONG-TERM PLAYER PRIOR DESIGN
## Hierarchical Bayesian Prior Model Specification

### 1. Hierarchical Architecture
1. **Tier 1 (Player Career Historical):** Previous season points per 90 (if mins >= 900), xG/90, xA/90, clean sheet rate.
2. **Tier 2 (Positional Baseline):** GK: 3.5 pts/match, DEF: 3.8 pts/match, MID: 4.5 pts/match, FWD: 4.8 pts/match.
3. **Tier 3 (Price Valuation Anchor):** price_prior = pos_floor * (Price / 8.0).

### 2. Fallbacks for Missing / Promoted Players
- **Returning PL Players with >= 900 mins:** 0.60 * Pts/90 + 0.40 * Price Prior
- **Returning PL Players with < 900 mins:** 0.30 * Pts/90 + 0.70 * Price Prior
- **Promoted / New Signings:** 100% Price Prior (Anchored to official FPL pricing consensus).
