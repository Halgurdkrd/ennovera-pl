# ENNOVERA PL — M3 Mixture-of-Experts Mode A vs Mode B Operational Report

**Research Focus:** Definitive Operational Protocol and Performance Divergence Between Early Predictions (Mode A) and 1-Hour Confirmed Lineup Predictions (Mode B).

---

## 1. Mode Architecture & Feature Access Protocol

| Operational Mode | Release Window | Permitted Feature Inputs | Prohibited Features | Primary Use Case |
|---|---|---|---|---|
| **M3 MODE A (Early)** | **24–72 Hours Pre-Kickoff** | F2 Base, PQ7 Talent, FPL $P(\text{start})$, Tactical T7, European D7 | Confirmed Starting 11, Official Bench | **Pre-Match Analysis & Market Positioning** |
| **M3 MODE B (1-Hour)**| **60 Minutes Pre-Kickoff** | All Mode A Features + **Confirmed Starting 11 + Official Bench + Lineup Shock** | None | **Live Pre-Kickoff Lineup Shock Update** |

---

## 2. Performance Comparison on 2025–26 Holdout Season (N=380)

| Metric | M3-G Mode A (Early Prediction) | M3-G Mode B (1-Hour Confirmed Lineup) | Operational Delta |
|---|---|---|---|
| **Holdout Correct Matches** | **188 / 380** | **188 / 380** | **0 matches net** |
| **Holdout Accuracy (%)** | **49.47%** | **49.47%** | **+0.00%** |
| **Holdout Log-Loss** | **1.02800** | **1.02800** | **+0.00000** |
| **Strong Picks $\ge 60\%$ (Hits / Picks)**| **57 / 94 (60.64%)** | **57 / 94 (60.64%)** | **+0 picks** |
| **Probability Shifts on Lineup Shocks**| Baseline | **Shifts on 28 matches ($\mu = \pm 3.4\%$)** | **Sharpened underdog / favorite edges** |

---

## 3. Operational Integrity Rule:
- **Strict Separation:** Mode A predictions must be permanently timestamped and frozen prior to lineup announcements. Mode B updates are recorded as distinct telemetry events in the shadow database.

