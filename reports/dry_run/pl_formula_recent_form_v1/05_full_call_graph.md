# FULL IMPLEMENTATION CALL GRAPH

```
[GW1 Completed Fixture Event]
  │
  ├──> [Table Ledger Builder] -> (Points, GD, GF updated)
  ├──> [Bayesian Team State Loader] -> (Attack/Defence EWMA micro-update)
  ├──> [Opponent & Venue Normalizer] -> (Schedule Difficulty Remaining)
  ├──> [Dixon-Coles Score Engine] -> (Scoreline PMF with rho = -0.115)
  ├──> [Dirichlet Calibrator] -> (3-Class Probability Surface)
  └──> [Vectorized Season Simulator] -> (10,000 Iterations with Points > GD > GF Tiebreaks)
```
