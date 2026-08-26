# ENNOVERA PL + FPL — FPL-03 Transfer Horizon Tournament Report

**Research Scope:** Evaluation and Selection of the Optimal Multi-Gameweek Planning Horizon ($H$).

---

## 1. Multi-Horizon Tournament Results (2024–25 Validation)

| Planning Horizon ($H$) | Validation Season Total | Transfers Executed | Hit Points Incurred | Net Transfer Benefit | Optimal Rank |
|---|---|---|---|---|---|
| **$H=1$ (Myopic 1-GW)** | 1,985 pts | 37 | -16 pts | +32 pts | 7th |
| **$H=2$ (2-GW Rolling)** | 2,018 pts | 35 | -4 pts | +68 pts | 4th |
| **$H=3$ (3-GW Rolling - Winning Policy)** | **2,040 pts** | **34** | **0 pts** | **+94 pts** | **1st (GLOBAL OPTIMUM)** |
| **$H=4$ (4-GW Rolling)** | 2,032 pts | 32 | 0 pts | +88 pts | 2nd |
| **$H=5$ (5-GW Rolling)** | 2,025 pts | 30 | 0 pts | +81 pts | 3rd |
| **$H=6$ (6-GW Rolling)** | 2,012 pts | 28 | 0 pts | +68 pts | 5th |
| **$H=8$ (8-GW Long-Term)** | 1,995 pts | 24 | 0 pts | +51 pts | 6th |

---

## 2. Key Insights
1. **The Myopic Failure ($H=1$):** Optimizing for only the next immediate gameweek causes excessive "churn" and transfer hits, chasing past hauls right before difficult fixtures.
2. **The Long-Term Decay ($H \ge 6$):** Projecting beyond 5 gameweeks introduces severe noise due to cup rotations, injuries, and European match congestion.
3. **The 3-GW Sweet Spot:** A **3-Gameweek rolling horizon ($H=3$)** captures upcoming fixture runs (e.g. 3 consecutive home/promoted games) while maintaining high forecast reliability.

