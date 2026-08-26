# ENNOVERA PL + FPL — FPL-01-VERIFY Squad Optimizer & Objective Counterfactual Report

**Verification Focus:** Squad Legality, Budget Utilization, and Counterfactual Mathematical Optimization Objectives.

---

## 1. Squad Legality & Constraint Audit (152 Gameweeks)

| Constraint Check | Requirement | Compliance Rate across 152 GWs | Status |
|---|---|---|---|
| **Total Squad Size** | Exactly 15 players | 152 / 152 GWs (100.0%) | **PASS** |
| **Position Quotas** | 2 GK, 5 DEF, 5 MID, 3 FWD | 152 / 152 GWs (100.0%) | **PASS** |
| **Club Concentration** | Maximum 3 players per club | 152 / 152 GWs (100.0%) | **PASS** |
| **Budget Ceiling** | Total squad cost $\le$ £100.0m | 152 / 152 GWs (100.0%) | **PASS** |
| **Starting XI Formations** | 1 GK, $\ge 3$ DEF, $\ge 2$ MID, $\ge 1$ FWD | 152 / 152 GWs (100.0%) | **PASS** |

---

## 2. Budget Utilization Analysis

- **Ennovera Component xP:** Mean budget used = **£98.6m** (Mean unused bank = **£1.4m**).
- **Price Baseline:** Mean budget used = **£99.8m** (Mean unused bank = **£0.2m**).
- **Insight:** Because Ennovera maximizes 15-player total xP, it sometimes selects high-value mid-priced players that leave £1.0m–£1.5m unused, whereas Price baseline fully exhausts the £100.0m cap on premium assets.

---

## 3. Optimizer Objective Counterfactuals (Diagnostic Only)

| Objective Formulation | Mathematical Definition | 2024–25 Val Score | 2025–26 Holdout Score | Delta vs Baseline |
|---|---|---|---|---|
| **O1: Maximize 15-Man Total xP** | $\max \sum_{i=1}^{15} \text{xP}_i$ | 2,023 pts | 1,961 pts | 0 pts (Default) |
| **O2: Maximize Starting XI xP** | $\max \sum_{i \in \text{XI}} \text{xP}_i$ | 2,048 pts | 1,982 pts | **+21 pts** |
| **O3: Maximize Starting XI + Captain** | $\max (\sum_{i \in \text{XI}} \text{xP}_i + \max_{i \in \text{XI}} \text{xP}_i)$ | 2,075 pts | 2,005 pts | **+44 pts** |

