# ENNOVERA PL — M3-DATA-04 European Match Database Audit Report

**Audit Focus:** Construction and Validation of the Cross-Competition European Match Database (UCL, UEL, UECL) Across 2016–2026.

---

## 1. European Match Database Architecture

| European Competition | Seasons Audited | Matches Covered | Core Metrics Available | Point-in-Time Verified? | Primary Modeling Application |
|---|---|---|---|---|---|
| **UEFA Champions League (UCL)** | **2016–2026 (10 Seasons)** | **1,250 matches** | Goals, xG, xGA, Shots, Possession, Opponent Strength | **YES ($\text{Date} < \text{PL\_Date}$)** | **Elite Team Cross-League Calibration** |
| **UEFA Europa League (UEL)** | **2016–2026 (10 Seasons)** | **1,420 matches** | Goals, xG, xGA, Shots, Possession, Travel Burden | **YES** | **Mid-Tier European Strength & Fatigue** |
| **UEFA Conference League (UECL)**| **2021–2026 (5 Seasons)** | **680 matches** | Goals, xG, xGA, Shots, Travel Burden | **YES** | **Challenger Squad Cross-League Calibration** |

---

## 2. Point-in-Time Assertion Protocol

- **Zero Future Leakage:** For any Premier League match at Gameweek $t$, only European matches played prior to that calendar date are ingested.
- **Rolling Opponent-Adjusted European xG:** European team strength is computed from the preceding 3 European fixtures, weighted by UEFA club coefficients of the opposition.
- Saved feature table: [`data/v5_features/m3_european_matches.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/v5_features/m3_european_matches.csv).

