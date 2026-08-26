# ENNOVERA PL — M3-DATA-02 Dedicated Draw Specialist Report

**Research Question:** Can a Dedicated Draw Specialist Model Predict Draws as the Argmax Highest-Probability Outcome Often Enough to Improve Total Winner Accuracy?

---

## 1. Empirical Evaluation Across Draw Prediction Thresholds (Holdout 2025–26, N=380)

We trained a dedicated binary draw probability model $P(\text{Draw} \mid \text{Tactical State})$ using tactical symmetry entropy, low-block frustration, and Expected Goals compression, testing across decision thresholds:

| Draw Decision Rule | Total Draws Predicted | Draw Precision (%) | Draw Recall (%) | Wrong Decisive $\to$ Correct Draw Flips | Correct Decisive $\to$ Wrong Draw Flips | **Net Winner Accuracy Impact (Matches)** | Total Holdout Accuracy (%) |
|---|---|---|---|---|---|---|---|
| **$P(\text{Draw}) \ge 33\%$** | 68 matches | 26.47% | 18.0% | +18 matches | -34 matches | **-16 matches** | **44.21% (Severe drop)** |
| **$P(\text{Draw}) \ge 35\%$** | 48 matches | 29.17% | 14.0% | +14 matches | -22 matches | **-8 matches** | **46.32% (Drop)** |
| **$P(\text{Draw}) \ge 38\%$** | 26 matches | 34.62% | 9.0% | +9 matches | -13 matches | **-4 matches** | **47.37% (Drop)** |
| **$P(\text{Draw}) \ge 40\%$** | 12 matches | 41.67% | 5.0% | +5 matches | -6 matches | **-1 match** | **48.16% (Drop)** |
| **Natural 1X2 Argmax (Baseline)**| **0 matches** | **N/A** | **0.0%** | **0 matches** | **0 matches** | **0 (Baseline)** | **48.42% (Optimal Winner Acc)**|

---

## 2. Mathematical Proof of the "Draw Trap" in 1X2 Prediction

$$\mathbb{E}[\Delta \text{Accuracy}] = N_{\text{draw\_calls}} \times (P(\text{True Draw} \mid \text{Call}) - P(\text{True Decisive} \mid \text{Call}))$$

1. **Draw Base Rate Barrier:** In the Premier League, approximately 26% of matches end in draws.
2. **Maximum Predicted Draw Probability:** Even in maximum-entropy matches (e.g. 0–0 between two low-block squads), the true conditional probability of a draw rarely exceeds $34\%\text{--}38\%$.
3. **Decisive Probability Supremacy:** Even when $P(\text{Draw}) = 36\%$, the combined probability of a decisive winner (Home Win + Away Win) remains $64\%$.
4. **Conclusion:** Whenever an algorithm forces a draw prediction ($P = 36\%$), it is wrong $64\%$ of the time. While this successfully catches some draws, it **destroys more correct decisive predictions than it recovers**.

### Definitive Recommendation:
**DO NOT FORCE DRAW ARGMAX PREDICTIONS.** Draws must remain an intrinsic component of multi-class probability calibration (minimizing Log-Loss and Brier score) rather than a forced deterministic winner call.

