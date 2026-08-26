# ENNOVERA PL — M3-VERIFY-01 Winner Decision Flips Forensic Audit Report

**Audit Focus:** Transparent Match-by-Match Accounting of Argmax Winner Predictions Across the 2025–26 Holdout Season (380 Matches).

---

## 1. Authoritative Winner Accuracy Leaderboard

| Model Architecture | 2025–26 Correct Matches | Holdout Accuracy (%) | Holdout Log-Loss | Holdout Brier Score | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy (%) | Historical Dependence |
|---|---|---|---|---|---|---|---|
| **Candidate F2 (Baseline)** | 184 / 380 | 48.42% | 1.02999 | 0.6192 | 37 / 55 | **67.27%** | 82.6% |
| **Candidate M1-D (Baseline)** | 183 / 380 | 48.16% | 1.02940 | 0.6188 | 42 / 65 | **64.62%** | 76.5% |
| **Candidate PQ7 (Corrected)** | 184 / 380 | 48.42% | 1.02976 | 0.6194 | 56 / 91 | 61.54% | 68.4% |
| **LINEUP-ORACLE (Confirmed XI)** | 184 / 380 | 48.42% | 1.03138 | 0.6191 | 61 / 95 | 64.21% | 65.0% |
| **T7 Tactical Matchup Expert** | **188 / 380** | **49.47%** | **1.02835** | **0.6180** | **57 / 95** | **60.00%** | **60.0%** |
| **DATA-04 D7 (European Form)** | **188 / 380** | **49.47%** | **1.02713 (Record)**| **0.6174** | **57 / 89** | **64.04%** | **55.0%** |
| **DATA-04 Peak Hybrid (50% Squad)**| **189 / 380** | **49.74% (Peak)** | **1.02710** | **0.6172** | **59 / 92** | **64.13%** | **50.0%** |

---

## 2. Match-Level Transition Case Studies:

| Gameweek | Match Fixture | Actual 1X2 Outcome | Baseline F2 / PQ7 Pick | Advanced Model Pick (T7 / D7) | Decision Transition Type |
|---|---|---|---|---|---|
| **GW5** | **Manchester City vs West Ham** | **Home Win (3–0)** | Draw (Stale Low Block) | **Home Win (Elite Talent Prior)** | **WRONG $\to$ CORRECT (+1)** |
| **GW8** | **Brentford vs Crystal Palace** | **Home Win (2–1)** | Away Win | **Home Win (Pressing Trap Signal)** | **WRONG $\to$ CORRECT (+1)** |
| **GW12**| **Newcastle vs Chelsea** | **Home Win (4–1)** | Away Win | **Home Win (European Travel Fatigue)** | **WRONG $\to$ CORRECT (+1)** |
| **GW19**| **Brighton vs Crystal Palace** | **Home Win (3–1)** | Draw | **Home Win (PPDA Transition Trap)**| **WRONG $\to$ CORRECT (+1)** |
| **GW23**| **Nottingham Forest vs Liverpool** | **Home Win (1–0)** | Away Win | **Home Win (Low Block Counter Shot)** | **WRONG $\to$ CORRECT (+1)** |
| **GW15**| **Tottenham vs Newcastle** | **Away Win (1–2)** | Away Win | Home Win | **CORRECT $\to$ WRONG (-1)** |

**Net Verified Winner Accuracy Gain:** **+4 to +5 matches over baseline F2/PQ7 (pushing accuracy to 49.47%–49.74%)**.

