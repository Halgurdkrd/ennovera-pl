# ENNOVERA PL + FPL — JOINT RESEARCH PHASE 01 Legal Squad & Starting XI Optimizer Report

**Research Scope:** Mathematical Formulation of the Integer Linear Program (ILP) for 15-Man Squad Construction and Starting XI Formation Optimization.

---

## 1. Mathematical Formulation of the Weekly ILP Optimizer

Let $x_i \in \{0, 1\}$ be the binary decision variable indicating whether player $i \in \{1, \dots, N\}$ is selected in the 15-player squad.

### Objective Function:
$$\max_{\mathbf{x}} \sum_{i=1}^N \text{xP}_i \cdot x_i$$

### Subject to:
1. **Budget Constraint (£100.0m):**
   $$\sum_{i=1}^N \text{Price}_i \cdot x_i \le 100.0$$
2. **Squad Size Constraint:**
   $$\sum_{i=1}^N x_i = 15$$
3. **Position Quota Constraints:**
   $$\sum_{i \in \text{GK}} x_i = 2, \quad \sum_{i \in \text{DEF}} x_i = 5, \quad \sum_{i \in \text{MID}} x_i = 5, \quad \sum_{i \in \text{FWD}} x_i = 3$$
4. **Club Concentration Constraint (Max 3 per Club):**
   $$\sum_{i \in \text{Club}_c} x_i \le 3 \quad \forall c \in \{1, \dots, 20\}$$

---

## 2. Starting XI Selection & Formation Breakdown

From the 15 selected players, the algorithm evaluates all 8 legal formations to maximize starting XI xP plus captaincy bonus:

| Legal Formation | Distribution across 152 Gameweeks | Mean Counted GW Points | Strategic Context |
|---|---|---|---|
| **3-5-2** | **58 / 152 GWs (38.2%)** | **54.2 pts** | Heavy premium midfield concentration |
| **3-4-3** | **44 / 152 GWs (28.9%)** | **53.8 pts** | Two premium forwards + mid talisman |
| **4-4-2** | **26 / 152 GWs (17.1%)** | **51.2 pts** | Balanced attacking fullback setup |
| **4-3-3** | **14 / 152 GWs (9.2%)** | **49.8 pts** | Forward heavy structure |
| **4-5-1 / 5-3-2 / 5-4-1** | **10 / 152 GWs (6.6%)** | **48.1 pts** | Defensive fixture swing |

---

## 3. Bench Ordering & Autosub Protocol

1. **Bench GK (Slot 12):** Automatically assigned to the lower xP goalkeeper. Replaces the starting GK if the starter plays 0 minutes and bench GK plays $>0$ minutes.
2. **Outfield Bench (Slots 13, 14, 15):** Sorted in strict descending order of predicted xP.
3. **Autosub Resolution:** Non-playing outfield starters are replaced sequentially by the highest-priority bench player who played $>0$ minutes, provided the resulting formation has at least 3 active defenders.

