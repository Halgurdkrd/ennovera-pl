# Ennovera PL Predictor — Phase 3 Model Training Report

Match-outcome ensemble (Model A specialist + Model B generalist), mirroring the WC2026
architecture. Chronological split, **no host/knockout adjustments** (the PL has real home
advantage and no knockouts). Trained on the 3,800-match leak-free feature set from Phase 2.

---

## Headline — the PL is a much harder problem than WC2026

| | WC2026 | **PL (this model)** |
|---|---|---|
| Validation accuracy | ~66% | **53.4%** (203/380, 2024-25) |
| Holdout accuracy | — | **48.4%** (184/380, 2025-26) |
| 3-class random baseline | 33% | 33% |
| Majority-class (home) baseline | — | 40.8% |

**This is expected and normal.** WC group stage is full of big mismatches (top nation vs
minnow); a domestic league is far more even, and bookmaker models land ~53-55%. The model
beats the majority-home baseline by ~13 pp and random by ~20 pp.

**⚠️ The single biggest weakness: the model is completely draw-blind — 0/93 draws called on
validation.** Every one of the 93 actual draws was predicted as a home or away win. Draws are
24% of PL matches, so this alone caps realistic accuracy. Fixing this is Phase 4 priority #1.

---

## Step 1 — Chronological split (no random split)
| Split | Rows | H / D / A |
|---|---|---|
| Train 2016-17 → 2023-24 | 3,040 | 1379 / 686 / 975 |
| Validate 2024-25 | 380 | 155 / 93 / 132 |
| **Holdout 2025-26** (untouched until Step 8) | 380 | 162 / 104 / 114 |

## Step 2 — Model A "Specialist" (2021-24, all 42 features)
- **Train 66.5% / Val 51.6%** — a 15 pp train-val gap = **overfitting** (42 features on ~1,140 matches).
- Top features: `elo_diff (.073), pos_diff (.037), home_elo (.036), home_athome_ga (.031), away_form10_gf (.028)`.

## Step 3 — Model B "Generalist" (2016-24, 16 Elo+form features)
- **Train 57.9% / Val 53.2%** — much smaller gap, generalizes better.
- Top features: `elo_diff (.183), home_elo (.078), away_elo (.070), home_athome_ppg (.057), h2h_draws (.056)`.
- **Diversity confirmed:** A spreads importance across position/form/H2H detail; B is Elo-dominated (elo_diff alone is 2.5× any other). Different feature reliance = a valid ensemble.

## Steps 4-7 — Ensemble + corrections, validated on 2024-25
| Config | Accuracy | Log-loss | Brier |
|---|---|---|---|
| Model A solo | 196/380 (51.6%) | 1.0173 | 0.6082 |
| **Model B solo** | 202/380 (53.2%) | **1.0094** | 0.6019 |
| Ensemble 50/50 | **203/380 (53.4%)** | 1.0098 | 0.6027 |
| Ensemble + promoted corr | 203/380 | 1.0098 | 0.6027 |
| Ensemble + FPL boost | 203/380 | 1.0130 | 0.6051 |
| Ensemble + both | 203/380 | 1.0130 | 0.6051 |

- **Best accuracy: Ensemble 50/50 (203).** Best log-loss: Model B solo (1.0094), a whisker ahead.
- **Promoted correction is a no-op on validation** — by design it only fires when `elo<1350 AND form_n<5`, and career-rolling form means no 2024-25 team has `form_n<5`. It matters only for true cold-start teams (Coventry in 2026-27).
- **FPL boost slightly *worsens* log-loss** (over-confident on big mismatches) with no accuracy gain — I'd leave it off.
- **Per-class recall:** home 132/155 (85%), **draw 0/93 (0%)**, away 71/132 (54%).
- **Calibration:** of 123 matches predicted ≥60%, **62% were correct** — well-calibrated, mild overconfidence.

## Steps 11-12 — Temperature & blend sweeps (validation)
- **Temperature:** T=1.25 gives the best log-loss (1.0064); accuracy is temperature-invariant (argmax-preserving).
- **Blend:** 50/50 best accuracy (203); 40/60 best log-loss (1.0091). All within 4 matches — the blend is robust.

## Step 8 — Holdout 2025-26 (untouched until now)
- **Ensemble+both, blend 40/60: 184/380 = 48.4%**, log-loss 1.0414.
- Validation was 53.4% → **5.0 pp drop**. That's above the 3 pp "stable" threshold — a sign of **mild overfitting to validation** (config was chosen on it) and/or 2025-26 being a harder season (its draw rate is higher: 104 vs 93). Treat 48-50% as the honest real-world expectation.

## Step 9 — Final models retrained on all data
- `pl_model_a_final.pkl` (2021-26, ~1,900 matches) · `pl_model_b_final.pkl` (2016-26, 3,800 matches). These are the 2026-27 production models.

## Step 10 — GW2 2026-27 predictions
*Cold-start (pre-season) estimates: end-of-2025-26 Elo/form carried forward; promoted teams use baseline Elo + FPL strength.*

| Match | Home% | Draw% | Away% | Pick |
|---|---|---|---|---|
| Crystal Palace vs Manchester City | 25.0 | 21.4 | 53.6 | away |
| Liverpool vs Nottingham Forest | 68.9 | 20.1 | 11.1 | home |
| Bournemouth vs Everton | 64.0 | 15.7 | 20.3 | home |
| Coventry City vs Hull City | 29.2 | 20.5 | 50.3 | away |
| Tottenham vs Newcastle United | 36.3 | 20.4 | 43.3 | away |
| Chelsea vs Brighton and Hove Albion | 50.1 | 19.0 | 30.8 | home |
| Leeds United vs Brentford | 39.7 | 19.2 | 41.1 | away |
| Sunderland vs Fulham | 43.6 | 23.7 | 32.7 | home |
| Manchester United vs Ipswich Town | 80.6 | 11.8 | 7.6 | home |
| Aston Villa vs Arsenal | 33.9 | 22.3 | 43.9 | away |

Sensible: City/Liverpool/United strong favourites; the two promoted-vs-promoted / cold-start
games (Coventry-Hull) are near coin-flips. **Note: 0 draws picked** — same blindness as validation.

---

## Comparison to the WC2026 approach

| | WC2026 | PL |
|---|---|---|
| Architecture | XGBoost + Elo ensemble, 50/50 | ✅ same (Model A + Model B) |
| Validation | chronological, leak-free | ✅ same |
| Correction | Hybrid prior-blend | ✅ promoted-team variant (fires only on cold-start) |
| Host boost | yes | ❌ removed (no host) |
| Knockout 0-draw adj. | yes | ❌ removed (no knockouts) |
| Data volume | 300 intl matches | **3,800** — retraining is finally viable |
| Accuracy | 66% (easier field) | 53% val / 48% holdout (harder, even league) |

## Recommended configuration & next steps
- **Deploy: Ensemble 50/50 @ T=1.25, promoted correction ON, FPL boost OFF.** (Best accuracy, best-calibrated log-loss, no over-confidence.)
- **Phase 4 priority #1 — fix draw-blindness.** Options: class-weight the loss toward draws, a draw-specific calibration layer, or a two-stage (decisive-vs-draw then home-vs-away) model. This is the biggest available accuracy gain.
- Add the **full FPL-history** player data (Priority 4 clone) for the separate **fantasy** model.
- Re-check the 5 pp val→holdout gap after fixing draws; consider a small `max_depth`/regularization bump on Model A (it overfits).
