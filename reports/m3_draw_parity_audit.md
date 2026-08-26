# ENNOVERA PL — M3 Draw & Parity Cluster Forensic Audit

**Audit Objective:** Investigating why draws account for 52.8% of all model errors and testing whether a 2-Stage Hierarchical Parity Architecture is mathematically viable.

---

## 1. The Draw Barrier in 3-Way Multinomial Classification

In the English Premier League, draws occur in **$\approx 25.8\%$ of all matches**. However:
- Multinomial logistic regression models distribute probability across Home, Draw, and Away.
- Because Home Win baseline is ~44% and Away Win is ~30%, the predicted draw probability rarely rises above **$28\%\text{--}30\%$**.
- **The Argmax Paradox:** Because $P(\text{Draw}) < \max(P(\text{Home}), P(\text{Away}))$ in virtually every single fixture, a standard argmax classifier picks Draw on **$0\%$ of matches**, mechanically guaranteeing an error on all ~100 draws each season.

---

## 2. Empirical Draw Clustering across Parity Tiers (Holdout 2025–26)

| Elo Differential Bracket | Match Count ($N$) | Observed Actual Draws ($N$) | Empirical Draw Rate (%) | Model Mean Predicted Draw (%) | Draw Parity Classification |
|---|---|---|---|---|---|
| **0 – 50 pts (Tight Parity)** | **91 matches** | **24 draws** | **26.4%** | 25.2% | **HIGH PARITY ZONE** |
| **50 – 100 pts** | **90 matches** | **21 draws** | **23.3%** | 25.1% | **MODERATE PARITY** |
| **100 – 200 pts (Mid-Spread)**| **128 matches** | **41 draws** | **32.0%** | 25.0% | **TACTICAL STALEMATE ZONE** |
| **200 – 300 pts (Clear Favorite)**| **56 matches** | **14 draws** | **25.0%** | 24.7% | **UNDERDOG RESISTANCE** |
| **300 – 600 pts (Heavy Mismatch)**| **15 matches** | **4 draws** | **26.7%** | 22.3% | **OUTLIER DRAWS** |

---

## 3. The 2-Stage Hierarchical Architecture (M3 Concept)

To address the draw barrier without distorting decisive match calibration:

```mermaid
graph TD
    A["Pre-Match Features (Expected XI, Elo, Tactical Matchup)"] --> B["Stage 1: Parity / Draw Specialist Classifier"]
    B -->|P_draw >= Threshold (e.g. 33%)| C["Predict DRAW (Argmax Override)"]
    B -->|P_draw < Threshold| D["Stage 2: Decisive Match Classifier (Home vs Away)"]
    D --> E["Output Final 1X2 Probabilities"]
```

### Strategic Recommendation for M3:
- Keep direct probability regression for continuous Log-Loss optimization, but implement **Stage 1 Parity Gating** for discrete 1X2 selection in matches with high draw density (e.g. low total expected goals $\lambda_H + \lambda_A < 2.20$, high tactical defensive alignment).

