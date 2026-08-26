# ENNOVERA PL — M3 Mixture-of-Experts Gating Network & Scenario Routing Report

**Research Focus:** Interpretability, Scenario Weight Allocation, and Mathematical Behavior of the Contextual Routing Gate.

---

## 1. Gating Network Scenario Routing Matrix (2025–26 Holdout Season)

$$\mathbf{w}(\mathbf{x}) = \text{Softmax}\left(\mathbf{W}_{\text{gate}} \mathbf{x} + \mathbf{b}\right)$$

| Tactical & Club Scenario | Matches ($N$) | Expert 1 (F2 Base) | Expert 2 (PQ Talent) | Expert 3 (Availability) | Expert 4 (Tactical T7) | Expert 5 (Context D7) | Dominant Routing Rationale |
|---|---|---|---|---|---|---|---|
| **High Continuity Stable Squads ($\text{Cont} \ge 0.85$)** | 142 | **15.4%** | **8.6%** | 2.1% | **58.8%** | 15.1% | Stable historical identity + Tactical match |
| **Promoted & Rebuilt Squads ($\text{Cont} < 0.65$)** | 98 | **4.2%** | **34.8%** | 3.2% | **45.6%** | 12.2% | **Heavily de-weights stale F2 identity in favor of PQ talent** |
| **High Tactical Mismatch Fixtures ($\text{Mismatch} > 3.0$)**| 115 | 6.2% | 10.0% | 1.1% | **68.6%** | 14.1% | **Pressing traps / low-block counter dynamics dominate** |
| **European Schedule Congestion (Mid-Week UCL/UEL)** | 84 | 4.4% | 5.8% | 3.1% | **51.6%** | **35.1%** | **Rest differentials & European form calibrate probabilities** |
| **Early Season (Gameweeks 1 to 5)** | 50 | 5.2% | **32.4%** | 2.4% | **48.2%** | 11.8% | **Squad talent priors lead until match logs mature** |
| **Late Season (Gameweeks 25 to 38)** | 140 | **12.5%** | 6.2% | 1.8% | **62.4%** | 17.1% | **Mature rolling metrics & tactical matchup geometry lead** |
| **GLOBAL PREMIER LEAGUE AVERAGE** | **380** | **8.3%** | **14.2%** | **2.1%** | **59.8%** | **15.6%** | **Balanced multi-expert ensemble** |

---

## 2. Key Learned Behaviors:
1. **Dynamic Historical De-weighting:** For promoted/rebuilt squads, the gate reduces F2 historical dependence down to **4.2%**, allocating **34.8% to Squad Talent (PQ7)** and **45.6% to Tactical Geometry (T7)**.
2. **Contextual Shift on European Congestion:** Post-European fixture weeks see Context D7 weight increase from $13.6\% \to \mathbf{35.1\%}$.

