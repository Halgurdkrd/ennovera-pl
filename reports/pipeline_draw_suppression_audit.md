# ENNOVERA PL — M3-VERIFY-02 Draw Suppression & Argmax Decision Boundary Audit Report

**Audit Focus:** Mathematical Investigation of Why Multiclass Argmax Predictions Rarely Select Draws Across All Models.

---

## 1. Mathematical Analysis of Draw Probabilities Across 2025–26 Holdout Season

| Model Architecture | Mean $P(\text{Draw})$ on Actual Draws | Mean $P(\text{Draw})$ on Non-Draws | Maximum Observed $P(\text{Draw})$ | Argmax Draw Predictions ($N$) | Actual Draws in Season ($N$) | Draw Recall (%) |
|---|---|---|---|---|---|---|
| **Candidate F2** | 0.274 | 0.252 | 0.328 | **0 matches** | 104 matches | **0.0%** |
| **Candidate PQ7** | 0.278 | 0.251 | 0.334 | **0 matches** | 104 matches | **0.0%** |
| **Tactical T7** | 0.282 | 0.248 | 0.342 | **0 matches** | 104 matches | **0.0%** |
| **Context D7** | 0.285 | 0.246 | 0.348 | **0 matches** | 104 matches | **0.0%** |
| **M3-E / R7 Router** | 0.284 | 0.247 | 0.345 | **0 matches** | 104 matches | **0.0%** |

---

## 2. Why Argmax Never Picks Draw (The Mathematics of 3-Class Argmax):
1. **The Argmax Condition:** A model predicts Draw if and only if $P(\text{Draw}) > P(\text{Home})$ AND $P(\text{Draw}) > P(\text{Away})$.
2. **The Empirical Draw Rate:** In the Premier League, the base draw rate is $\approx 26.5\%$. Even in a perfectly even parity match (e.g. 50/50 coin flip on neutral ground), empirical probabilities split roughly:
   $$P(\text{Home}) = 0.37, \quad P(\text{Draw}) = 0.28, \quad P(\text{Away}) = 0.35$$
3. **No Structural Suppression Bug:** $P(\text{Draw})$ is accurately calibrated around 26%–28%. It rarely exceeds 34%, so under standard argmax rules, it is almost never the largest scalar.
4. **Forced Draw Rule Reminder:** In M3-DATA-02, forcing draw predictions whenever $P(\text{Draw}) \ge 30\%$ resulted in a severe loss of net accuracy ($-8$ matches, $48.4\% \to 46.3\%$), proving that suppressing forced draw calls is mathematically correct.

