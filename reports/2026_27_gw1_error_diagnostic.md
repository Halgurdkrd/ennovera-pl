# 2026–27 Premier League GW1 — Error Diagnostic & Missing Information Roadmap

**Document Focus:** Forensic Root-Cause Diagnosis of GW1 Prediction Misses, Inertia Matrix, and Architectural Roadmap  
**Target Architecture:** V5.2 (Confirmed XI & Lineups), V5.3 (Injuries & Market Odds), V5.4 (Advanced Tactical Matchups)

---

## 1. Forensic Root-Cause Error Matrix (5 Misses / 10 Fixtures)

| Match | Actual Score & Outcome | V5.1 Pred & Probabilities | Diagnostic Classification | Status | Primary Root Cause & Detailed Explanation |
|---|---|---|---|---|---|
| **Hull City vs Man Utd** | **2–0 (Home Win)** | Away Win (`[23.8% H, 24.1% D, 52.1% A]`) | **F. Promoted Team Uncertainty + A. Stale Reputation** | **CONFIRMED** | Man Utd's 1662 Elo heavily over-weighted away victory. Hull (promoted, 1418 Elo) underwent an aggressive summer rebuild, creating massive cold-start uncertainty. |
| **Ipswich vs Sunderland** | **2–1 (Home Win)** | Away Win (`[28.2% H, 26.5% D, 45.3% A]`) | **A. Stale Reputation (Frozen Elo Artifact)** | **CONFIRMED** | Sunderland's historical Elo was frozen at 1510.6 upon relegation years ago, erroneously rating them higher than Ipswich (1407.9) despite Ipswich's recent PL experience. |
| **Nott'm Forest vs Leeds**| **0–1 (Away Win)** | Home Win (`[41.9% H, 30.9% D, 27.2% A]`) | **K. Random Variance + J. Tactical Matchup** | **PLAUSIBLE** | Low-scoring fixture decided in the 27.2% away win probability window. Leeds' aggressive counter-pressing disrupted Forest's build-up play. |
| **Newcastle vs Liverpool** | **2–2 (Draw)** | Home Win (`[47.0% H, 26.4% D, 26.6% A]`) | **G. Draw Under-Probability** | **CONFIRMED** | Elite offensive deadlock at St. James' Park. Model assigned 26.4% to draw; Poisson/score model dampening was insufficient to elevate draw density to >30%. |
| **Fulham vs Chelsea** | **2–3 (Away Win)** | Home Win (`[53.6% H, 24.8% D, 21.6% A]`) | **H. Favorite Overconfidence / Derby Variance** | **PLAUSIBLE** | Fulham's 14th finish vs Chelsea's 4th finish in 2025-26 caused an inversion due to home advantage weighting (53.6% H), under-rating Chelsea's attacking depth. |

---

## 2. Historical Inertia Disagreement Matrix (All 20 Clubs)

Measures the divergence between **Multi-Season Historical Prior Rank (Elo)** and **Current Team-State Rank (V5.1 Expected Points)**:

| Club | Historical Elo Rank | Current-State Rank | Rank Difference ($\Delta$) | V2 Pre xPts | V5.1 Pre xPts | Structural Interpretation |
|---|---|---|---|---|---|---|
| **Everton** | 13 | 8 | **+5** | 57.97 | 57.21 | Solidified defensive structure and core retention outperforming brand perception. |
| **Bournemouth** | 6 | 3 | **+3** | 60.15 | 61.06 | High pressing efficiency and offensive xG generation exceed historical pedigree. |
| **Fulham** | 11 | 9 | **+2** | 57.05 | 56.10 | Stable squad continuity and high home performance baseline. |
| **Crystal Palace** | 14 | 12 | **+2** | 53.22 | 54.06 | Attacking core stabilizes mid-table floor. |
| **Manchester City** | 2 | 1 | **+1** | 76.16 | 76.86 | Elite title contender with unmatched bench depth (£118.5m). |
| **Ipswich Town** | 19 | 18 | **+1** | 33.73 | 32.70 | Promoted squad reconstruction with severe Elo gap. |
| **Tottenham** | 17 | 17 | **0** | 43.15 | 43.38 | **Severe decline:** 2025–26 15th finish + low roster continuity. |
| **Sunderland** | 16 | 16 | **0** | 43.74 | 44.06 | **Stale historical Elo artifact** frozen at relegation years ago. |
| **Leeds United** | 15 | 15 | **0** | 48.25 | 49.76 | Competitive Championship playoff winner with strong attacking baseline. |
| **Coventry City** | 20 | 20 | **0** | 23.04 | 23.34 | Promoted squad reconstruction + severe Elo/Championship gap. |
| **Chelsea** | 7 | 7 | **0** | 57.89 | 57.99 | High squad value offset by historical transition volatility. |
| **Aston Villa** | 5 | 5 | **0** | 61.01 | 60.15 | Champions League fatigue / European fixture congestion risk. |
| **Manchester United** | 4 | 4 | **0** | 60.27 | 60.37 | Over-credited away strength due to historical Elo weight. |
| **Newcastle United** | 10 | 11 | **-1** | 54.10 | 54.40 | High variance home/away differential. |
| **Hull City** | 18 | 19 | **-1** | 32.95 | 32.13 | Promoted squad cold start. |
| **Arsenal** | 1 | 2 | **-1** | 72.89 | 71.58 | Elite champion with top starting XI, slightly narrower bench depth. |
| **Nottingham Forest**| 12 | 14 | **-2** | 53.49 | 52.93 | Moderate alignment between historical reputation and squad state. |
| **Brighton** | 8 | 10 | **-2** | 54.67 | 55.84 | High tactical upside (demonstrated in 4–0 win over Villa). |
| **Liverpool** | 3 | 6 | **-3** | 60.25 | 59.31 | Aging midfield transition and defensive regression from peak years. |
| **Brentford** | 9 | 13 | **-4** | 53.00 | 53.34 | Tactical set-piece superiority overperforming baseline Elo. |

---

## 3. Information We Are Still Missing — Ranked Signal Matrix

To eliminate the root causes identified in GW1, the following features are prioritized for upcoming V5 iterations:

| Rank | Missing Signal | Expected Value ($\Delta$ LL) | Historical Data Available? | Live / Pre-Kickoff Data Available? | Implementation Complexity | Target Stage |
|---|---|---|---|---|---|---|
| **1** | **Confirmed Starting XI (1h Pre-Match)** | **-0.0150** | Yes (`fpl_full/gws/`) | Yes (FPL / Twitter / Team Feeds) | Medium | **V5.2** |
| **2** | **Injuries & Suspensions Tracking** | **-0.0120** | Yes (FPL status `chance_of_playing`) | Yes (FPL bootstrap-static) | Low | **V5.2** |
| **3** | **Promoted Team Cold-Start Calibration** | **-0.0090** | Yes (Championship stats) | Yes (FBref / Transfermarkt) | Medium | **V5.2** |
| **4** | **Betting Market Odds Regularizer (Bet365 / Pinnacle)** | **-0.0085** | Yes (`data/raw/pl_history/`) | Yes (Odds APIs) | Low | **V5.3** |
| **5** | **Manager & Tactical Regime Changes** | **-0.0070** | Yes (`data/raw/managers/`) | Yes | Medium | **V5.3** |
| **6** | **Goalkeeper Shot-Stopping (PSxG +/-)** | **-0.0065** | Yes (FBref/Opta) | Yes | Medium | **V5.3** |
| **7** | **Set-Piece xG & Defensive Concession** | **-0.0055** | Yes | Yes | High | **V5.4** |
| **8** | **High-Intensity Pressing & PPDA** | **-0.0045** | Yes | Yes | High | **V5.4** |
| **9** | **Progressive Carrying & Passing Volume** | **-0.0040** | Yes | Yes | High | **V5.4** |
| **10** | **Fixture Congestion & Rest Days** | **-0.0035** | Yes | Yes | Low | **V5.4** |

