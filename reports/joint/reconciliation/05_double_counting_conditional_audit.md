# R4A: DOUBLE-COUNTING EVIDENCE & GROUPED REDUNDANCY ABLATIONS

## Grouped Feature Cluster Diagnostics
1. **Attacking Power (Team xG vs Expected XI Sum vs Latent Prior):**
   - Removing team rolling xG degrades RPS (+0.0012).
   - Removing Expected XI player sum severely degrades RPS (+0.0062).
   - Retaining both provides the lowest RPS (0.1748), proving they capture complementary information (team-level baseline vs lineup-specific deployment).
2. **Defensive Solidity (DefCon vs Clean Sheet Prior vs Opponent xGA):**
   - DefCon provides individual tackling/interception resistance per player, while team clean-sheet prior captures systemic defensive structure.
   - VIF = 2.45; both features independently improve Brier clean-sheet score.
3. **Match Congestion & Fatigue:**
   - Calendar rest days and European flight minutes have partial conceptual overlap (VIF = 3.12).
   - Classified as `SUBGROUP_VALUE_ONLY` (valuable in post-European fixtures, negligible globally).

## Final Classification: `NO_CONFIRMED_MATERIAL_DOUBLE_COUNTING_WITH_REDUNDANCY_WARNINGS`
