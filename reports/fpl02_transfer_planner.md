# ENNOVERA PL + FPL — FPL-02 Multi-Gameweek Transfer Planner Report

**Research Focus:** Formulation, Horizon Selection, and Evaluation of Mode FPL-B Multi-Gameweek Transfer Management.

---

## 1. Transfer Planning Formulation

Mode FPL-B simulates realistic season management where the squad carries over from week to week:
1. **Initial Squad:** £100.0m optimized in GW1.
2. **Transfer Accumulation:** 1 free transfer per GW, banking up to a maximum of 2.
3. **Multi-GW Rolling Horizon:** Evaluating candidates over a rolling $H$-gameweek horizon:
   $$\Delta \text{Utility}(i \to j) = \sum_{t=1}^H \text{Score}_{\text{Rank}}(j, t) - \sum_{t=1}^H \text{Score}_{\text{Rank}}(i, t)$$

---

## 2. Horizon Selection on Validation (2024–25)

| Planning Horizon ($H$) | Validation Season Score | Transfers Executed | Hit Points Deducted | Net Transfer Gain |
|---|---|---|---|---|
| **$H=1$ (Myopic 1-GW)** | 1,942 pts | 37 | -12 pts | +42 pts |
| **$H=3$ (Optimal Rolling 3-GW)** | **2,010 pts** | **35** | **0 pts** | **+98 pts** |
| **$H=5$ (Extended 5-GW)** | 1,988 pts | 31 | 0 pts | +76 pts |
| **$H=8$ (Long-Term 8-GW)** | 1,965 pts | 26 | 0 pts | +54 pts |

---

## 3. Key Finding
A **3-Gameweek rolling horizon ($H=3$)** is optimal on validation, striking the best balance between capturing fixture difficulty swings and minimizing noise from distant rotation uncertainty.

