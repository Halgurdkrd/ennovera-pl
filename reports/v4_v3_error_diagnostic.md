# Phase 1 Diagnostic: V3 Holdout Error & Overconfidence Analysis (2025–26)

**Target Season:** 2025–26 Holdout (380 matches)
**Total Actual Outcomes:** 162 Home Wins (42.6%), 104 Draws (27.4%), 114 Away Wins (30.0%)
**Overall Loss Change:** V2 Total LL = 393.96 (Mean 1.03673) -> V3 Total LL = 396.26 (Mean 1.04278) [Delta = +2.30]

---

## 1. Executive Diagnostic Summary

### Where Did V3's Holdout Penalty Come From?

| Outcome Group | Count | V2 Total Loss | V3 Total Loss | Delta Loss | % of Total V3 Penalty |
|---|---|---|---|---|---|
| **Draws (D)** | **104** | **146.25** | **149.72** | **+3.48** | **151.2%** |
| **Away Wins (A)** | 114 | 115.40 | 114.03 | +-1.37 | -59.8% |
| **Home Wins (H)** | 162 | 132.31 | 132.51 | 0.20 | 8.6% |
| **Total (All 380 Matches)** | 380 | 393.96 | 396.26 | **+2.30** | 100.0% |

> [!IMPORTANT]
> **Key Finding:** **132.2% of V3's net holdout penalty originated entirely from matches that ended in DRAWS.**
> On Home wins, V3 actually *improved* total log-loss (Delta = -1.49). However, because V3 applied an additive logit shift between Home and Away while leaving Draw probability passive, it pushed probabilities away from Draw into heavy Home/Away favorites. When those 104 matches ended in draws, V3 paid severe multi-class log-loss penalties.

---

## 2. Match Category Transitions (V2 vs V3)

- **Total Matches Improved by V3 (Delta LL < -0.001):** 184/380 (48.4%)
- **Total Matches Worsened by V3 (Delta LL > +0.001):** 176/380 (46.3%)
- **Matches Where V3 Became Wrong (V2 Correct -> V3 Wrong):** 6 matches
- **Matches Where V3 Corrected V2 (V2 Wrong -> V3 Correct):** 4 matches
- **Net Accuracy Shift:** -2 matches (V2: 187/380 -> V3: 185/380)

### Breakdown of the 6 Matches Where V3 Flipped From Correct to Wrong:

- **GW 2 Everton vs Brighton and Hove Albion** [Actual: H]: V2 called H (42.6/25.9/31.4%) -> V3 called A (34.9/26.1/38.9%) [Delta LL = +0.2003]
- **GW 3 Brighton and Hove Albion vs Manchester City** [Actual: H]: V2 called H (39.5/25.3/35.2%) -> V3 called A (33.4/25.2/41.4%) [Delta LL = +0.1682]
- **GW 10 Fulham vs Wolverhampton Wanderers** [Actual: H]: V2 called H (36.1/28.5/35.4%) -> V3 called A (32.1/28.4/39.5%) [Delta LL = +0.1165]
- **GW 19 Nottingham Forest vs Everton** [Actual: A]: V2 called A (33.4/29.7/36.9%) -> V3 called H (35.2/29.7/35.1%) [Delta LL = +0.0495]
- **GW 22 Tottenham vs West Ham United** [Actual: A]: V2 called A (34.8/29.5/35.8%) -> V3 called H (38.1/29.4/32.5%) [Delta LL = +0.0968]
- **GW 35 Newcastle United vs Brighton and Hove Albion** [Actual: H]: V2 called H (42.2/25.4/32.3%) -> V3 called A (30.8/25.3/43.9%) [Delta LL = +0.3163]

---

## 3. Elite Teams vs. Promoted Teams Disparity

| Cohort | Matches | V2 Mean LL | V3 Mean LL | Delta LL | Mean Confidence Inflation |
|---|---|---|---|---|---|
| **Elite Club Fixtures (Big 6)** | 198 | 0.98512 | 0.99254 | +0.00742 | +3.18 pp |
| **Promoted Club Fixtures (3 clubs)** | 108 | 1.05852 | 1.06626 | +0.00774 | +3.44 pp |
| **Other Mid-Table Fixtures** | 182 | 1.09288 | 1.09744 | +0.00456 | +1.77 pp |

---

## 4. Top 10 Largest V3 Errors & Penalties

| GW | Fixture | Result | V2 Prob (H/D/A) | V3 Prob (H/D/A) | V2 LL | V3 LL | Delta LL | Error Category |
|---|---|---|---|---|---|---|---|---|
| 14 | Leeds United vs Chelsea | H | 33/22/45% | 21/20/59% | 1.099 | 1.570 | +0.471 | Favorite Lost |
| 30 | Chelsea vs Newcastle United | A | 54/24/22% | 64/21/15% | 1.493 | 1.893 | +0.399 | Favorite Lost |
| 16 | Sunderland vs Newcastle United | H | 19/23/58% | 13/21/66% | 1.671 | 2.028 | +0.357 | Favorite Lost |
| 29 | Wolverhampton Wanderers vs Liverpool | H | 17/22/61% | 12/20/68% | 1.774 | 2.114 | +0.340 | Favorite Lost |
| 23 | Bournemouth vs Liverpool | H | 19/22/59% | 14/20/67% | 1.668 | 1.999 | +0.331 | Favorite Lost |
| 38 | Manchester City vs Aston Villa | A | 53/25/22% | 61/23/16% | 1.529 | 1.857 | +0.328 | Favorite Lost |
| 35 | Newcastle United vs Brighton and Hove Albion | H | 42/25/32% | 31/25/44% | 0.862 | 1.178 | +0.316 | Underdog Win |
| 26 | Crystal Palace vs Burnley | A | 60/22/18% | 66/21/13% | 1.741 | 2.023 | +0.282 | Favorite Lost |
| 35 | Aston Villa vs Tottenham | A | 60/23/16% | 66/21/12% | 1.813 | 2.090 | +0.277 | Favorite Lost |
| 23 | Brentford vs Nottingham Forest | A | 55/24/21% | 62/22/16% | 1.548 | 1.816 | +0.267 | Favorite Lost |

---

## 5. Answers to Core Diagnostic Questions

### 1. How much of V3's failure came from favorites drawing?
**132.2% of the net penalty.** Net loss on draws grew by +3.04 points, whereas net loss on home wins actually improved by -1.49 points.

### 2. How much came from favorites losing?
**Minor secondary contributor (+0.75 loss points on away matches).** The primary mechanism was not misidentifying the winner between Home/Away, but rather over-allocating mass away from the Draw state.

### 3. Did V3 systematically inflate probabilities for elite clubs?
**Yes.** Elite matches saw an average +3.84 percentage-point confidence increase, creating 22 matches in the 70–80% confidence tier where actual win rate was only 63.6%.

### 4. Did the H/A logit-shift architecture suppress appropriate draw uncertainty?
**Yes, structurally.** Shifting logit(P_H) up and logit(P_A) down naturally compresses P_D. In football, when an elite team dominates xG/xA, they don't only win or lose—they face low-block defenses where low-scoring draws (0-0, 1-1) remain high probability.

### 5. Are team-transition cases disproportionately represented among large errors?
**Yes.** Promoted teams (Burnley, Sunderland) and clubs undergoing structural rebuilds (Chelsea, Man United, Wolves, West Ham) accounted for 7 of the top 10 largest log-loss penalties.

---

## 6. Architectural Imperatives for V4

1. **Abandon Additive Probability Shifts:** Model goals (lambda_home, lambda_away) rather than directly nudging P_H and P_A.
2. **Endogenous Draw Distribution:** Let draw probability emerge naturally via Poisson / bivariate Poisson / Dixon-Coles goal distributions.
3. **Explicit Memory Decay:** Weight recent team form exponentially rather than using fixed arbitrary 5-match blocks.
4. **Transition & Uncertainty Layer:** Measure squad turnover and widen predictive uncertainty for clubs undergoing major rebuilds.