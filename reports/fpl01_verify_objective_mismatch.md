# ENNOVERA PL + FPL — FPL-01-VERIFY The Objective Mismatch: Regression MAE vs FPL Decision Quality

**Research Focus:** Mathematical and Statistical Explanation of Why Minimizing Global Player xP MAE Does Not Maximize Fantasy Points.

---

## 1. The Statistical Anomaly Explained

In standard machine learning, lower Mean Absolute Error (MAE) is assumed to indicate a superior model. However, in Fantasy Premier League, **Ennovera achieves the lowest global MAE (1.588 vs 2.315 for Rolling Form and 1.954 for Price)**, yet Price and Form produce more total Fantasy points:

| Evaluation Cohort | Sample Size | Ennovera xP MAE | Price Baseline MAE | Rolling Form MAE | Best Model in Cohort |
|---|---|---|---|---|---|
| **All Active Players (Global)** | 113,592 | **1.588** | 1.954 | 2.315 | **Ennovera (Lowest Error)** |
| **Top 20% xP Cohort** | 22,718 | 3.412 | 3.120 | **3.085** | **Rolling Form** |
| **Top 5% Elite Talismans** | 5,680 | 4.850 | 3.920 | **3.840** | **Rolling Form / Price** |
| **Selected Starting XI Starters**| 1,661 | 3.680 | 3.310 | **3.250** | **Rolling Form / Price** |

---

## 2. The Core Mathematical Mechanism: The Zero-Inflation & Shrinkage Trap

1. **85% of the Player Pool is Irrelevant:** In any given Gameweek, ~500 out of 600 available players score between 0 and 2 points (benchwarmers, defensive mids, unselected reserves).
2. **Mean Shrinkage:** A regression model optimizing global MAE minimizes loss by predicting conservative values ($1.2 - 2.5$) for almost everyone. This drives global MAE down to **1.588**.
3. **The Penalty on Elite Hauls:** In doing so, the model under-predicts the explosive tail (e.g. predicting 6.5 for Haaland when he scores 17). 
4. **FPL is a Tail-Risk / Tail-Reward Game:** FPL squad selection and captaincy only care about the **top 2–5% of the distribution**. The Price and Form baselines tolerate higher error on benchwarmers in exchange for aggressively selecting and captaining high-ceiling explosive assets.

---

## 3. Future Architectural Recommendation
For future FPL modeling, replace unweighted L1/L2 regression with:
- **Top-Tail Weighted Regression / Haul Probability Models** ($P(\text{Points} \ge 10)$).
- **Ranking-Oriented Loss Functions (Pairwise / NDCG Optimization)** rather than point regression across non-selectable players.

