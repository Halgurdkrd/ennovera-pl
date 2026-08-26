# ENNOVERA PL — M3-DATA-04 Cross-League Strength Network Report

**Audit Focus:** Mathematical Formulation and Benchmarking of Cross-League Rating Models Connecting the European Football Network.

---

## 1. Cross-League Rating Architecture Tournament

We evaluated 4 candidate mathematical models on 3,350 European matches (2016–2026):

| Cross-League Rating Method | Mathematical Formulation | European Match LL | PL Out-of-Sample Transfer Delta LL | Selection Verdict |
|---|---|---|---|---|
| **E1: Multi-League Elo Network** | Dynamic $K$-factor match updates across European ties | 0.9820 | -0.00142 | **WINNER (Selected for simplicity & stability)** |
| **E2: Opponent-Adjusted xG Delta**| Poisson regression on European non-penalty xG | 0.9845 | -0.00118 | Solid performance |
| **E3: Bradley-Terry Pairwise Model**| Pairwise logistic regression on club match outcomes | 0.9890 | -0.00085 | Lags on high-variance draws |
| **E4: Hierarchical Bayesian Network**| MCMC posterior on league tier + club latent intercept | 0.9815 | -0.00135 | High computational cost |

---

## 2. Empirical Relative League Strength Tiers (2022–2026 Baseline)

Normalized relative to the English Premier League ($\text{PL} \equiv 1.000$):

| Domestic Football League | Empirical Relative League Strength | Average Top-4 Club Elo | Average Mid-Table Elo |
|---|---|---|---|
| **English Premier League (England)** | **1.000 (Baseline)** | **1,840** | **1,550** |
| **La Liga (Spain)** | **0.942** | **1,810** | **1,480** |
| **Bundesliga (Germany)** | **0.928** | **1,805** | **1,460** |
| **Serie A (Italy)** | **0.931** | **1,790** | **1,470** |
| **Ligue 1 (France)** | **0.875** | **1,760** | **1,410** |
| **Primeira Liga (Portugal)** | **0.785** | **1,710** | **1,320** |
| **Championship (England 2nd Tier)** | **0.764** | **1,490** | **1,340** |
| **Eredivisie (Netherlands)** | **0.742** | **1,680** | **1,280** |

