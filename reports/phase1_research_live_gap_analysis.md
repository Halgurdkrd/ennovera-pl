# ENNOVERA PHASE 1 — RESEARCH ↔ LIVE ARCHITECTURE GAP ANALYSIS

| Component | Historical FPL-03 | Current Live Serving | Phase 1 Candidate | Gap Severity | Resolution |
|---|---|---|---|---|---|
| **Long-Term Prior** | Multi-season career EWMA | None (0% prior) | Hierarchical Bayesian Prior | CRITICAL | Built in `fpl_player_prior.py` |
| **Recent Points** | Shifted 5-GW rolling EWMA | Raw 1-match FPL form | Decomposed EWMA | HIGH | Replaced heuristic |
| **Underlying xG/xA** | Shifted 5-GW rolling rates | None (Points only) | Multi-Head Rate Blend | HIGH | Decomposed in xP |
| **Expected Minutes** | 3-GW / 5-GW + Price Prior | Status heuristic (0.95/0.85) | Logistic P(start) + Minutes | MODERATE | Calibrated R^2 = 0.52 |
| **Early-Season Handling**| Shifted historical priors | 70% 1-match momentum | Bayesian Shrinkage w(n) = n / (n + 4) | CRITICAL | Resolved via grid search |
| **Captain Utility** | U = xP + 3.0 P(Haul) - pen | U = xP + 3.0 P(Haul) - pen | Same (Identical) | CLEAN | Preserved |
| **Optimizer** | Scipy `linprog` (15 players, £100m) | Scipy `linprog` (15 players, £100m) | Same (Identical) | CLEAN | Preserved |
| **Chip Decision Logic**| Reservation value tournament | Disjunctive `or` bug | Conjunction `and` fix | HIGH | Corrected in Phase 1 |
