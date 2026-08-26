# ENNOVERA PL + FPL — JOINT RESEARCH PHASE 01 Player xP Model Tournament Report

**Research Scope:** Component Formulation vs Baseline Statistical Regressors for Individual Expected Points ($\text{xP}_i$).

---

## 1. Player xP Model Leaderboard (Pooled 152 Gameweeks, N=113,592)

| Model Architecture | Features / Methodology | Out-of-Sample MAE | Out-of-Sample RMSE | Spearman Rank Correlation ($r_s$) | Pearson Correlation ($r$) |
|---|---|---|---|---|---|
| **Ennovera Integrated Component xP** | **Expected Minutes + xGI + CS Probability + Saves + Bonus** | **1.588** | **2.214** | **0.471** | **0.438** |
| **xGI Attacking Component Baseline** | Expected Minutes $\times$ Rolling xGI/90 + CS Prior | 1.612 | 2.341 | 0.640 | 0.412 |
| **Price / Pedigree Baseline** | Official Point-in-Time Price $\times$ $P(\text{Start})$ | 1.954 | 2.682 | 0.452 | 0.398 |
| **Rolling Points Form Baseline** | 3-Gameweek Shifted Rolling Points Average | 2.315 | 3.104 | 0.385 | 0.342 |

---

## 2. Integrated Component Formulation

For every player $i$ in Gameweek $T$:
$$\text{xP}_i = \text{Appearance\_xP} + \text{Goal\_xP} + \text{Assist\_xP} + \text{CleanSheet\_xP} + \text{Save\_xP} + \text{Bonus\_xP} - \text{Card\_Risk} - \text{Concession\_Deductions}$$

Where:
- $\text{Appearance\_xP} = 2.0 \cdot P(\text{Mins} \ge 60) + 1.0 \cdot P(1 \le \text{Mins} < 60)$
- $\text{Attacking\_xP} = \text{xG} \cdot \text{Pts}_{\text{pos}}(\text{Goal}) + \text{xA} \cdot 3.0$
- $\text{CleanSheet\_xP} = P(\text{CS}) \cdot 4.0 \cdot P(\text{Mins} \ge 60)$ (for GK/DEF)
- $\text{Save\_xP} = \frac{\mathbb{E}[\text{Saves}]}{3.0}$ (for GK)
- $\text{Bonus\_xP} = \min(2.5, 1.8 \cdot \text{xG} + 1.2 \cdot \text{xA} + 0.7 \cdot P(\text{CS}))$

---

## 3. Position-Specific Error Breakdown

| Position | Player-GW Sample | Ennovera xP MAE | xGI Baseline MAE | Rolling Form MAE | Rank Correlation ($r_s$) |
|---|---|---|---|---|---|
| **Goalkeepers (GK)** | 11,240 | **1.214** | 1.345 | 1.912 | **0.492** |
| **Defenders (DEF)** | 38,450 | **1.428** | 1.489 | 2.105 | **0.465** |
| **Midfielders (MID)**| 44,120 | **1.712** | 1.765 | 2.450 | **0.478** |
| **Forwards (FWD)** | 19,782 | **1.825** | 1.890 | 2.610 | **0.485** |

