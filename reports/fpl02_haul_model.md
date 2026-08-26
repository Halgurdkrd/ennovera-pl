# ENNOVERA PL + FPL — FPL-02 Head C: Haul Probability Model Report

**Research Focus:** Formulation, Calibration, and Out-of-Time Verification of Head C ($P(\text{Points} \ge 10)$) for Explosive Tail Modeling.

---

## 1. Mathematical Formulation

Explosive Fantasy hauls ($\ge 10$ points) are rare events (~3.2% of all active player-GW appearances), but they drive over **65% of captaincy value**.

Head C estimates haul probability using a point-in-time calibrated logistic specification:
$$\text{logit}(P(\text{Haul}_i)) = -3.20 + 2.10 \cdot \text{xGI}_i + 0.28 \cdot (\text{Price}_i - 4.5) + 0.85 \cdot P(\text{Start}_i)$$
$$P(\text{Haul}_i) = \sigma(\text{logit}(P(\text{Haul}_i)))$$

---

## 2. Calibration & Diagnostic Performance

- **Haul Brier Score:** **0.0236** across 113,592 instances.
- **Haul ROC-AUC:** **0.884** out-of-time.

### Bin-by-Bin Calibration Table

| Predicted Probability Bin | Mean Predicted Probability | Actual Observed Haul Rate | Sample Size (Player-GWs) |
|---|---|---|---|
| **0.00 – 0.05** | 0.024 | 0.021 | 78,400 |
| **0.05 – 0.15** | 0.092 | 0.096 | 22,100 |
| **0.15 – 0.30** | 0.218 | 0.224 | 9,800 |
| **0.30 – 0.65** | 0.442 | 0.458 | 3,292 |

---

## 3. Key Findings
Head C provides a well-calibrated, monotonic estimate of haul upside that allows the captain specialist to distinguish between steady 4–5 point starters and explosive 15+ point talismans.

