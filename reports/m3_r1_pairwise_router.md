# ENNOVERA PL — M3-R1 Pairwise Sequential Override Router Report

**Research Focus:** Formulation, Training, and Evaluation of Pairwise Sequential Override Logic (Candidate R2).

---

## 1. Sequential Decision Architecture

$$\text{Decision Path: } P_{\text{Base (F2)}} \xrightarrow{\mathbb{P}(\text{PQ}>\text{Base})} P_{\text{PQ}} \xrightarrow{\mathbb{P}(\text{Tact}>\text{Current})} P_{\text{Tact}} \xrightarrow{\mathbb{P}(\text{Ctx}>\text{Current})} P_{\text{Final}}$$

| Sequential Step | Override Trigger Condition | Trigger Frequency (Holdout) | Override Success Rate (%) | Primary Target Scenario |
|---|---|---|---|---|
| **Step 1: PQ Override** | $\mathbb{P}(\text{PQ} > \text{Base}) \ge 0.55$ | 82 matches (21.6%) | **64.6%** | **Promoted & Rebuilt Squads ($\text{Cont} < 0.65$)** |
| **Step 2: Tactical Override**| $\mathbb{P}(\text{Tact} > \text{Current}) \ge 0.52$ | 114 matches (30.0%) | **68.4%** | **High Tactical Mismatch / Pressing Traps** |
| **Step 3: Context Override** | $\mathbb{P}(\text{Ctx} > \text{Current}) \ge 0.55$ | 68 matches (17.9%) | **72.1%** | **European Congestion / Fatigue Differentials** |

---

## 2. Performance Summary:
- **Validation:** 51.84% Accuracy, 0.99479 Log-Loss.
- **Holdout (2025–26):** **188 / 380 correct (49.47% accuracy)**, **1.02794 Log-Loss**.
- **Conclusion:** Pairwise override routing provides a highly interpretable, stable alternative to direct 5-class multinomial routing.

