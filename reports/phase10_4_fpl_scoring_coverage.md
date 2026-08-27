# ENNOVERA PHASE 10.4 — FPL SCORING COVERAGE MAP

| FPL Scoring Element | Points / Rule | Current Model Coverage | Coverage Classification |
| :--- | :--- | :--- | :--- |
| **Appearance (1-59m)** | 1 pt | Phase 9 Expected Minutes | **FULLY MODELED** |
| **60+ Minutes** | +1 pt (2 pts total) | Phase 9 P(60+) Logistic Head | **FULLY MODELED** |
| **Goals (FWD / MID / DEF)** | 4 / 5 / 6 pts | Phase 10.1 Decomposed Goal Head | **FULLY MODELED** |
| **Assists** | 3 pts | Phase 10.1 Decomposed Assist Head | **FULLY MODELED** |
| **Clean Sheets (GK / DEF / MID)** | 4 / 4 / 1 pt | Phase 10.2 Clean-Sheet Engine | **FULLY MODELED** |
| **Goals Conceded (-1 per 2)** | -1 pt / 2 goals | Phase 10.2 Poisson Concession | **FULLY MODELED** |
| **Saves (GK)** | 1 pt / 3 saves | Historical average proxy | **PROXY MODELED (Gap)** |
| **Penalty Saves (GK)** | 5 pts | Historical average proxy | **PROXY MODELED** |
| **Penalty Misses** | -2 pts | Phase 10.1 Penalty Expectation | **PARTIALLY MODELED** |
| **Yellow / Red Cards** | -1 / -3 pts | Historical team/player rate | **PROXY MODELED** |
| **Bonus Points (3, 2, 1)** | 1-3 pts | Regression proxy from xP | **PROXY MODELED (MAJOR GAP)** |
| **Defensive Contributions** | Official Thresholds | Not modeled explicitly | **NOT MODELED (CRITICAL GAP)** |
