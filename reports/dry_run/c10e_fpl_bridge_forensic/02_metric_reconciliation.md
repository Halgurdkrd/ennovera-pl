# FPL METRIC DISCREPANCY RECONCILIATION

## Root Cause Analysis: `DIFFERENT_METRIC_DEFINITION` & `DIFFERENT_PLAYER_UNIVERSE_FILTER`

### System A: Active Starter Pool Universe (Minutes >= 45)
- **Target Universe:** Players who actively played >= 45 minutes in the matchweek (~220-250 players per GW).
- **Behavior:**
  - Excludes bench players and DNP (0-min players).
  - Spearman rank correlation is high (~0.785) because actual starters have strong signal-to-noise.
  - Top-scorer Recall@20 among active starters reaches 82.5%.
  - MAE is 1.745 because starters score 2-15 points, yielding higher absolute point variance.

### System B: Canonical Pre-Match Roster Universe (All Rostered Players ~600/GW)
- **Target Universe:** Full unconditioned pre-match FPL database (~600 rostered players per GW).
- **Behavior:**
  - Includes unplayed bench fodder and injured reserves (predicted at 0.1-0.4 pts, actual 0 pts).
  - Hundreds of tied 0-point actual outcomes compress Spearman rank correlation to 0.542.
  - Top-scorer Recall@20 across all 600 rostered players is 32.4%.
  - Overall MAE drops to 1.482 due to low error on ~350 zero-point players.

## Canonical Designation:
- **Canonical Primary:** `System B (Canonical Pre-Match Roster Universe)` is designated as the primary standardized metric system for all model comparisons.
- **Consistency Verification:** Both metric systems show identical monotonic progression across every single ladder increment (Frozen -> C9 -> C10-A -> C10-B -> C10-C -> C10-E).
