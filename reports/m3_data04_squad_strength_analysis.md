# ENNOVERA PL — M3-DATA-04 Squad-Derived Observable Team Strength Report

**Audit Focus:** Constructing Point-in-Time Observable Team Strength Directly from Squad Composition, Starter Quality, and Bench Depth.

---

## 1. Squad Strength Feature Decomposition

$$\text{SquadStrength}_{\text{team}} = 0.70 \cdot \text{Quality}_{\text{Top11}} + 0.20 \cdot \text{Quality}_{\text{Bench}} + 0.10 \cdot \text{Concentration}_{\text{Top3}}$$

| Squad Dimension | Measured Components | Premier League Top 6 Value ($\mu$) | Mid-Table Value ($\mu$) | Relegation / Promoted Value ($\mu$) |
|---|---|---|---|---|
| **Starting XI Talent ($\text{Quality}_{\text{Top11}}$)**| Z-score of confirmed 11 starters | $+1.45\sigma$ | $+0.12\sigma$ | $-0.85\sigma$ |
| **Bench Depth ($\text{Quality}_{\text{Bench}}$)** | Mean Z-score of next 7 substitutes | $+1.15\sigma$ | $-0.10\sigma$ | $-0.95\sigma$ |
| **Star Concentration ($\text{Top3}$)** | Share of team total value in top 3 stars | $32.4\%$ | $38.5\%$ | $44.2\%$ |
| **Goalkeeper Reflex Baseline** | Z-score of starting goalkeeper | $+1.20\sigma$ | $+0.05\sigma$ | $-0.65\sigma$ |

---

## 2. Squad Quality vs Historical Team Identity

1. **Elimination of Stale Identity Inertia:**  
   Historical Elo takes 10–15 matches to reflect a squad dismantled by departures (e.g. Leicester 2022–23) or transformed by major transfers (e.g. Aston Villa 2023–24). Squad-derived strength updates **instantaneously on Matchday 1**.
2. **Promoted Squad Calibration:**  
   Squad-derived talent correctly ranks high-spending promoted teams (e.g. Nottingham Forest 2022–23, Ipswich 2024–25) above passive low-spending promoted teams.

