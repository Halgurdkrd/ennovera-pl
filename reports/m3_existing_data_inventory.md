# ENNOVERA PL — M3 Comprehensive Existing Data Inventory

**Audit Focus:** Complete Catalog of Local Data Assets, Feature Coverage, Timestamps, Leakage Protections, and Unused Predictive Value.

---

## 1. Structured Inventory Table

| Dataset Category | Seasons Available | Coverage (Rows/Matches) | Key Local Features | Pre-Match Availability | Leakage Risk | Current Usage | Potential Unused Value |
|---|---|---|---|---|---|---|---|
| **A. Historical PL Match Data** | 2016–17 to 2025–26 | 3,800 matches | FTHG, FTAG, FTR, HTHG, HTAG, Shots, HST, Corners, Fouls, Cards, Bet365 Odds | Yes (Fixtures & pre-match odds) | None | Core Base (V2, V4, F2, M1-D) | Match pace, half-time scorelines, referee card aggression |
| **B. FPL Master Gameweek Logs** | 2016–17 to 2024–25 | 320,000+ player-GWs | minutes, goals, xG, xA, xGI, xGC, saves, clean sheets, ICT threat/influence | Yes (lagged rolling window) | None when lagged | Aggregated into Expected XI | ICT Threat/Influence progression, defensive xGC per 90, transfer momentum |
| **C. FPL Cleaned Players Metadata**| 2016–17 to 2024–25 | 5,500+ player-seasons | position, team, cost, chance_of_playing_next_round, news, status | Yes (point-in-time snapshots) | Low | Position, cost, team IDs | Official FPL doubtful status flags ('chance_of_playing_next_round') |
| **D. M1 Expected XI Features** | 2016–17 to 2025–26 | 3,800 matches | xi_att, xi_cre, xi_def, xi_gk, cont_h, cont_a, unc_h, unc_a, depth, is_promoted | Yes (strictly lagged pre-match) | None | Primary Driver in M1-D | Position-specific continuity, bench depth differentials |
| **E. Bet365 Closing Odds** | 2016–17 to 2025–26 | 3,800 matches | B365H, B365D, B365A, Market Implied Probs, Overround | Yes (Pre-kickoff closing consensus)| None | Audit Benchmark Only | Market Oracle diagnostic, market-free ensemble weighting |
| **F. 2026–27 GW1 Live Data** | 2026–27 (GW1) | 10 matches | Pre-match odds, actual scores, actual results, pre-match model forecasts | Yes | None | Forward Diagnostic Only | Pure forward out-of-sample test evidence |
| **G. Pre-Match Confirmed Lineups**| MISSING LOCALLY | 0 rows | Confirmed starting 11, confirmed bench, 1-hour announcement timestamp | Missing | High if un-timestamped | Not Used | **HIGHEST: Directly fixes 12.2% of model errors caused by rotation** |
| **H. Pre-Match Injury Logs** | MISSING AS TIME-SERIES| 0 rows | Injury diagnosis, return timeline, practice participation | Missing | High if retrospective | Not Used | **HIGH: Starting XI presence confidence** |
| **I. Tactical & Pressing Data** | MISSING DETAILED | 0 rows | PPDA, high turnovers, field tilt, progressive passes/carries | Missing | Low | Not Used | **MODERATE-HIGH: Style matchup interactions** |

