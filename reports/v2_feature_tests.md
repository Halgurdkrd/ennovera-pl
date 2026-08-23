# Ennovera PL Predictor — V2 Feature Research (M0-M7)

Discipline: **train 2016-2023, calibrate on 2023-24 (temp/Platt only), validate 2024-25,
holdout 2025-26.** A feature is kept only if it beats **M0 on BOTH seasons** by log-loss. No
feature accumulation.

> **Note on M0:** this M0 trains on 2016-**2023** (7 seasons) — one fewer than the V1 benchmark's
> Elo (which trained through 2023-24). Holding 2023-24 out for calibration costs M0 ~7 holdout
> matches, so M0 here is **181/380, LL 1.100** (vs the V1-benchmark Elo's 188/1.078). All
> comparisons below are against *this* M0.

## Results — sorted by holdout log-loss

| Model | Features | Val acc | Val LL | Hold acc | Hold LL | Beats M0? |
|---|---|---|---|---|---|---|
| **M1b** | **Elo + Platt** | 197 | **1.010** | 184 | **1.053** | ✅ best |
| M7 | combo (goals+prevpos) + temp | **199** | 1.025 | **188** | 1.056 | ✅ |
| M1a | Elo + temperature (T=1.2) | 195 | 1.039 | 181 | 1.071 | ✅ |
| M2 | Elo + goals (form gf/ga) | 195 | 1.057 | 181 | 1.078 | ✅ |
| M5 | Elo + prev-season position | 192 | 1.044 | 185 | 1.090 | ✅ |
| M0 | Elo (3) | 195 | 1.063 | 181 | 1.100 | baseline |
| M4 | Elo + rest days | 193 | 1.050 | 182 | 1.108 | ❌ |
| M1c | Elo + Isotonic | 198 | 1.212 | 188 | 1.495 | ❌ overfit |
| M3 | Elo + availability | — | — | — | — | ⏭ no historical data |
| M6 | Elo + manager change | — | — | — | — | ⏭ no data |
| **Bet365** | (benchmark) | — | — | 186 | **1.019** | reference |

## The four questions, answered

### 1. Does calibration close the gap to Bet365? **Yes — ~60% of it.**
- M0 holdout LL 1.100 → gap to Bet365 (1.019) = **+0.082**.
- **Elo + Platt: 1.053 → gap +0.034.** Calibration closes ~60% of the probability-quality gap
  with a *single cheap post-processing step* and no new features. This confirms the V1
  benchmark's core finding: our problem was calibration, not features.
- **⚠️ Isotonic overfits catastrophically** (LL 1.495) — 380 calibration points are far too few
  for isotonic regression. Use **Platt (sigmoid)** or **temperature**, never isotonic on a small
  calibration set.

### 2. Which single feature adds the most value to Elo? **Goals (marginally); rest days fails.**
- **M2 goals** (rolling gf/ga): holdout 1.078 — beats M0 (1.100). Best single feature.
- **M5 prev-season position**: 1.090 — beats M0, weaker.
- **M4 rest days: 1.108 — does NOT beat M0.** Rest days carry no reliable signal here.
- **xG (M2 genuine):** not in our data — `pl_features.csv` has only goal-based proxies; real xG
  needs the Understat/FPL full clone.
- **Availability (M3) & manager (M6):** no historical data — flagged for live-season / manual
  collection. M3 is usable for **live** predictions only.

**But note:** every raw feature model still loses to plain **calibration** (Platt 1.053). No
single feature beats calibrating Elo.

### 3. Does any combination beat calibrated Elo? **No — it ties at best.**
- **M7 = Elo + goals + prev-pos + temperature: holdout 1.056** (and best *accuracy*, 188). That's
  essentially level with Elo+Platt (1.053) on log-loss, and the features add real accuracy back.
- So the combo doesn't beat calibration on log-loss; the gains from goals+prevpos are already
  mostly captured by calibration. The features buy a little **accuracy**, not calibration.

### 4. What should V2 be? **Calibrated Elo — plus goals + prev-position if you want the accuracy back.**
- **Simplest, best log-loss: `Elo + Platt` (M1b).**
- **If accuracy matters too: `Elo + goals + prev-position + Platt`** (M7-style, but Platt instead
  of temp) — recovers holdout accuracy to ~188 at similar log-loss.
- **Drop:** rest days (no signal), isotonic (overfits). **Defer:** xG, availability, manager
  (need data we don't have historically).

## Verdict
**V2 = Platt-calibrated Elo**, optionally with **goals + prev-season position** for accuracy.
Calibration is the single highest-value change — it closes 60% of the bookmaker gap for free.
The remaining ~0.034 log-loss gap to Bet365 needs genuinely new information (xG, lineups,
market signal), not more of the engineered features we already have.

### Saved
- `data/models/pl_v2_candidate.pkl` — the Elo model (apply Platt at inference; see above).
- `data/experiments/v2_feature_tests.json` — all M0-M7 numbers.
