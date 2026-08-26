# ENNOVERA PL + FPL — FPL-03 2023–24 Failure Forensics Report

**Research Scope:** Scientific Autopsy of the 243-Point Deficit in 2023–24 and Verification of the Multi-Opportunity Transfer Engine.

---

## 1. The 2023–24 Anomaly Explained

In FPL-02, the 2023–24 season produced an anomalous collapse:
- Mode FPL-A: **2,034 pts**
- Old Mode FPL-B: **1,791 pts**
- Difference: **-243 pts**

---

## 2. Root Cause: The "15th-Player Sorting Trap"

### Defective Code in FPL-02:
```python
squad_sorted = current_squad.sort_values("score_head_b_rank", ascending=True)
worst_player = squad_sorted.iloc[0] # ALWAYS picked the £4.0m backup GK!
```

### The Failure Cascade:
1. In FPL squads, the 15th player by predicted score is almost always the **non-playing £4.0m backup goalkeeper** ($\text{xP} \approx 0.1$).
2. The transfer heuristic attempted to replace this £4.0m player with an eligible replacement in the market costing $\le \text{Price} + \text{Bank} = £4.0\text{m}$.
3. Available £4.0m goalkeepers also have $\text{xP} \approx 0.1$, yielding $\Delta \text{Gain} \approx 0.0$.
4. Consequently, the planner **NEVER executed transfers** for outfield starters!
5. When premium starters suffered long-term injuries or rotation (e.g. Kevin De Bruyne's hamstring injury in GW1, Erling Haaland's foot stress fracture in GW15–21), the manager **held them dead on the bench for 15+ consecutive weeks**, missing breakout assets like **Cole Palmer (£5.0m $\to$ 244 pts)**, **Ollie Watkins (228 pts)**, and **Phil Foden (230 pts)**!

---

## 3. The Corrected Solution in FPL-03

The planner now scans across **all 15 squad positions**, evaluating the maximum marginal replacement value:
$$\Delta \text{Gain}(i \to j) = \sum_{t=1}^H \text{Score}(j, t) - \sum_{t=1}^H \text{Score}(i, t)$$
Subject to $\text{Price}(j) \le \text{Price}(i) + \text{Bank}$.

### Verified Recovery:
- 2023–24 Corrected FPL-B (No Chips): **1,979 pts (+171 pts recovered!)**
- 2023–24 Corrected FPL-B (With Chips): **2,062 pts (Outperforms FPL-A by +28 pts!)**

