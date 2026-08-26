# ENNOVERA — WC2026 Player Ratings vs Current PL Player Engine

**Audit Focus:** Conceptual and Empirical Comparison between the WC2026 EA FC–Based Player System and the Premier League M1-D Expected-XI Latent Engine.

---

## 1. Signal-by-Signal Comparison Matrix

| Predictive Signal Dimension | WC2026 Player Rating System | Current Premier League M1-D Engine | Overlap Level | Unique Value / Signal Contribution |
|---|---|---|---|---|
| **Attacking Quality** | EA FC SHO (0–99) + Finishing | Rolling FPL xG/90 + Goals/90 | High Overlap | M1-D is purely empirical; WC2026 adds technical scouts' finishing rating |
| **Creativity / Playmaking** | EA FC PAS (0–99) + Vision | Rolling FPL xA/90 + Assists/90 | High Overlap | M1-D is match-grounded; WC2026 adds passing range baseline |
| **Defensive Quality** | **EA FC DEF (0–99) + Outfield Tackling** | FPL xGC/90 (High noise team metric)| **LOW OVERLAP (NEW VALUE)** | **CRITICAL: EA FC DEF captures individual defender quality (Saliba 87 vs Maguire 78)** |
| **Goalkeeping Quality** | **EA FC GK Reflexes / Diving (0–99)** | FPL Saves/90 (High volume noise) | **LOW OVERLAP (NEW VALUE)** | **CRITICAL: Directly differentiates elite keepers (Raya 87 vs Verbruggen 78)** |
| **Lineup Selection Probability**| Static top-11 / called-up squad | **$P(\text{start})$ + Expected Minutes** | Low Overlap | **M1-D is vastly superior for dynamic lineup rotation** |
| **Squad Continuity / Turnover**| Static squad list | **Pre-match minute retention %** | Low Overlap | **M1-D is vastly superior for transition shocks** |
| **Foreign Transfer Prior** | **Global 16,228 database (EA FC 26)**| Heuristic $0.75 \times \text{prior}$ | Moderate Overlap | **CRITICAL: Provides pre-trained ratings for newly arrived foreign transfers** |

---

## 2. Key Insights on What EA FC Ratings Add to the Premier League Model

1. **Massive Upgrade for Defenders and Goalkeepers:**  
   In our M1 forensic audit, standalone player defensive ratings contributed almost zero marginal Log-Loss gain because FPL defensive stats are team-aggregated clean sheets and goals conceded (which heavily confound individual talent with team tactics). EA FC's individual scouting attributes (`DEF = 89` for Van Dijk, `87` for Saliba, `86` for Gabriel) provide the **first clean, player-level defensive signal in the repository**.
2. **Instant Priors for Foreign Signings (Zero PL History):**  
   When a player transfers from Serie A, Bundesliga, or South America, FPL has zero data points. EA FC ratings instantly provide a calibrated baseline prior.
3. **What NOT to Adopt from WC2026:**  
   Do NOT adopt the static top-11 aggregation or the hardcoded $65\% / 25\% / 10\%$ formula. M1-D's dynamic Expected XI minutes weighting ($P(\text{start}) \times \frac{\text{Mins}}{90}$) is mathematically superior.

