# ENNOVERA PL — ROOT-CAUSE-01 Draw Problem Scientific Autopsy Report

**Autopsy Focus:** Forensic Deconstruction of Draw Probabilities, Argmax Multiclass Boundaries, and Counterfactual Decision Rules.

---

## 1. The Draw Failure Reality: 54.5% of All Errors

$$\text{Total 2025–26 Errors} = 191 \text{ matches} \quad \longrightarrow \quad \mathbf{104 \text{ Errors (54.45\%) are DRAWS}}$$

| Metric | Candidate F2 | Tactical T7 | Context D7 | M3 Best (R7) | Market Consensus |
|---|---|---|---|---|---|
| **Actual Draws in Season ($N$)** | 104 | 104 | 104 | 104 | 104 |
| **Argmax Draw Predictions ($N$)** | **0** | **0** | **0** | **0** | **0** |
| **Draw Recall (%)** | **0.0%** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |
| **Mean $P(\text{Draw})$ on Actual Draws** | 0.274 | 0.282 | 0.285 | **0.284** | 0.278 |
| **Mean $P(\text{Draw})$ on Non-Draws** | 0.252 | 0.248 | 0.246 | **0.247** | 0.251 |
| **Maximum Observed $P(\text{Draw})$** | 0.328 | 0.342 | 0.348 | **0.345** | 0.338 |

---

## 2. Why Does Argmax Never Pick Draw? (The 3-Class Mathematics)
- In the Premier League, empirical draw frequency is $\approx 27.4\%$.
- Even in a dead-even match, model probabilities split:
  $$P(\text{Home}) = 0.38, \quad P(\text{Draw}) = 0.29, \quad P(\text{Away}) = 0.33$$
- Because $P(\text{Draw}) < \max(P_H, P_A)$, the categorical argmax decision rule strictly selects the side with slight home advantage or higher talent, even when a draw is highly probable.

---

## 3. Counterfactual Diagnostic Draw Threshold Test

*Evaluating whether lowering the threshold to predict Draw improves net winner accuracy.*

| Draw Margin Threshold ($\Delta P$) | Draws Predicted ($N$) | Actual Draws Captured | Correct Home/Away Lost | Total Correct / 380 | Net Accuracy (%) | Net Accuracy Gain vs Argmax |
|---|---|---|---|---|---|---|
| **0.0 pp (Argmax)** | **0** | **0** | **0** | **189** | **49.74%** | **0 (Reference)** |
| **1.0 pp** | 0 | 0 | 0 | 189 | 49.74% | 0 |
| **3.0 pp** | 0 | 0 | 0 | 189 | 49.74% | 0 |
| **5.0 pp** | 1 | 0 | 1 | 188 | 49.47% | -1 match |
| **7.5 pp** | 3 | 0 | 3 | 186 | 48.95% | -3 matches |
| **10.0 pp** | 9 | 1 | 5 | 185 | 48.68% | -4 matches |

**Scientific Conclusion:** Forcing draw predictions via heuristic threshold adjustments does NOT increase net accuracy; it destroys more correct favorite calls than the few draws it captures.

