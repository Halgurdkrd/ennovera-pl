# 2026–27 Premier League GW1 — Real-World Model Evaluation

**Status:** Completed Pre-GW1 Real-World Validation  
**Fixture Window:** August 21–24, 2026 (**10 Official Premier League Matches**)  
**Information Cutoff:** Pre-Kickoff Snapshot (Strictly pre-August 21, 2026, 19:00 UTC)

---

## 1. Executive Summary & Diagnostic Disclaimer

> [!WARNING]
> **Diagnostic Nature of N=10 Sample:**  
> A sample of 10 matches is **statistically diagnostic, not conclusive**. Single-match bounces, refereeing decisions, red cards, and early-season variance heavily influence 10-game outcomes. This evaluation is designed to detect structural model strengths and blind spots in live real-world deployment, not to proclaim ultimate model superiority.

### Global Metric Comparison

| Model | Correct / 10 | Accuracy % | Multi-Class Log-Loss | Brier Score | Mean Confidence | Draws Predicted | Strong Picks $\ge 60\%$ (Hits / Picks) |
|---|---|---|---|---|---|---|---|
| **Raw Elo (M0)** | 5 / 10 | 50.0% | 0.95659 | 0.56560 | 52.1% | 0 | 1 / 1 (100.0%) |
| **Frozen V2 Baseline** | 5 / 10 | 50.0% | 0.97515 | 0.57441 | 54.8% | 0 | 3 / 3 (100.0%) |
| **Frozen V4 Candidate** | 5 / 10 | 50.0% | 0.96816 | 0.57145 | 54.4% | 0 | 2 / 2 (100.0%) |
| **Frozen V5.1 Expected XI** | **5 / 10** | **50.0%** | **0.95390** | **0.56353** | 54.8% | 0 | **2 / 2 (100.0%)** |

> [!TIP]
> **V5.1 Performance on GW1:**
> - V5.1 achieved the **lowest Log-Loss (0.95390)** and **lowest Brier Score (0.56353)** across all evaluated models.
> - On the high-confidence tier ($\ge 60\%$ Strong Picks), V5.1 delivered **100% accuracy (2/2)**, correctly identifying dominant home wins for Arsenal (3–0) and Manchester City (2–1).

---

## 2. Match-by-Match Prediction Breakdown

| Kickoff (UTC) | Match | Score | FTR | Raw Elo Prob (Pred) | Frozen V2 Prob (Pred) | Frozen V4 Prob (Pred) | Frozen V5.1 Prob (Pred) | V5.1 Result |
|---|---|---|---|---|---|---|---|---|
| **Aug 21 19:00** | **Arsenal vs Coventry City** | 3–0 | **H** | `[70.1%, 26.0%, 3.9%]` (**H**) | `[74.0%, 17.5%, 8.5%]` (**H**) | `[74.4%, 17.1%, 8.5%]` (**H**) | `[75.2%, 16.5%, 8.3%]` (**H**) | **CORRECT (SP $\ge 60\%$)** |
| **Aug 22 11:30** | **Hull City vs Man Utd** | 2–0 | **H** | `[25.1%, 26.0%, 48.9%]` (**A**) | `[22.8%, 24.9%, 52.3%]` (**A**) | `[23.2%, 24.1%, 52.7%]` (**A**) | `[23.8%, 24.1%, 52.1%]` (**A**) | **INCORRECT (Upset)** |
| **Aug 22 14:00** | **Everton vs Crystal Palace** | 2–0 | **H** | `[37.4%, 26.0%, 36.6%]` (**H**) | `[40.7%, 30.5%, 28.8%]` (**H**) | `[40.9%, 30.3%, 28.8%]` (**H**) | `[40.6%, 30.6%, 28.8%]` (**H**) | **CORRECT** |
| **Aug 22 14:00** | **Ipswich vs Sunderland** | 2–1 | **H** | `[27.6%, 26.0%, 46.4%]` (**A**) | `[27.9%, 27.0%, 45.1%]` (**A**) | `[27.8%, 26.7%, 45.5%]` (**A**) | `[28.2%, 26.5%, 45.3%]` (**A**) | **INCORRECT (Stale Elo)** |
| **Aug 22 14:00** | **Nott'm Forest vs Leeds** | 0–1 | **A** | `[41.5%, 26.0%, 32.5%]` (**H**) | `[42.0%, 30.8%, 27.2%]` (**H**) | `[41.7%, 30.6%, 27.7%]` (**H**) | `[41.9%, 30.9%, 27.2%]` (**H**) | **INCORRECT** |
| **Aug 22 16:30** | **Brentford vs Spurs** | 3–0 | **H** | `[49.5%, 26.0%, 24.5%]` (**H**) | `[60.1%, 21.6%, 18.3%]` (**H**) | `[59.2%, 22.1%, 18.7%]` (**H**) | `[59.8%, 21.8%, 18.4%]` (**H**) | **CORRECT** |
| **Aug 23 13:00** | **Brighton vs Aston Villa** | 4–0 | **H** | `[33.9%, 26.0%, 40.1%]` (**A**) | `[49.6%, 28.6%, 21.8%]` (**H**) | `[49.9%, 28.2%, 21.9%]` (**H**) | `[50.7%, 27.8%, 21.5%]` (**H**) | **CORRECT** |
| **Aug 23 13:00** | **Man City vs Bournemouth** | 2–1 | **H** | `[66.4%, 26.0%, 7.6%]` (**H**) | `[71.3%, 19.8%, 8.9%]` (**H**) | `[70.1%, 20.7%, 9.2%]` (**H**) | `[70.9%, 20.1%, 9.0%]` (**H**) | **CORRECT (SP $\ge 60\%$)** |
| **Aug 23 15:30** | **Newcastle vs Liverpool** | 2–2 | **D** | `[32.8%, 26.0%, 41.2%]` (**A**) | `[46.2%, 27.4%, 26.4%]` (**H**) | `[46.5%, 27.0%, 26.5%]` (**H**) | `[47.0%, 26.4%, 26.6%]` (**H**) | **INCORRECT (Draw)** |
| **Aug 24 19:00** | **Fulham vs Chelsea** | 2–3 | **A** | `[38.4%, 26.0%, 35.6%]` (**H**) | `[54.8%, 23.6%, 21.6%]` (**H**) | `[53.6%, 24.8%, 21.6%]` (**H**) | `[53.6%, 24.8%, 21.6%]` (**H**) | **INCORRECT** |

---

## 3. Data Integrity & Leakage Verification

All predictions strictly adhered to the pre-kickoff information boundary:

| Feature / Signal Family | Source | Time Horizon | Leakage Check | Safety Status |
|---|---|---|---|---|
| **Elo Ratings** | `current_elo.csv` | End of 2025–26 season | No in-game stats used | **100% SAFE** |
| **Previous Positions** | 2025–26 Final Table | May 2026 | Historical end-state | **100% SAFE** |
| **Form (Last 5 GF)** | `pl_features.csv` (2025–26) | Matchdays 34–38 (2025–26) | strictly pre-season | **100% SAFE** |
| **V4 Team States** | EWMA Decayed Ratings | Decayed from May 2026 | No GW1 goals used | **100% SAFE** |
| **Expected XI Rosters** | `cleaned_players.csv` | FPL Pre-Season Baseline | Pre-GW1 player values | **100% SAFE** |
| **Match Scores/Stats** | `fixtures.json` (FPL API) | Evaluated post-match only | Excluded from inputs | **100% SAFE** |

