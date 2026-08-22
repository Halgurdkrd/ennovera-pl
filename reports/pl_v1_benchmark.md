# Ennovera PL Predictor — V1 Final Benchmark (FROZEN)

Benchmark on the **2025-26 holdout (380 matches, 104 draws)** — the untouched test season.
This is the frozen reference for V1.

## Results

| Config | Accuracy | Log-loss | Brier | Draw recall |
|---|---|---|---|---|
| Random (uniform) | 33% * | 1.099 | 0.667 | 0/104 |
| Home-always | 162/380 (43%) | 1.086 | 0.657 | 0/104 |
| **Elo-only (3 features)** | **188/380 (49%)** | **1.078** | **0.647** | 2/104 |
| **Our V1 ensemble (49 features)** | 185/380 (49%) | 1.084 | 0.654 | 4/104 |
| **Bookmaker (Bet365)** | 186/380 (49%) | **1.019** | **0.612** | 0/104 |

\* Random accuracy is 33% by theory; an argmax of a flat `[⅓,⅓,⅓]` degenerates to always-home (43%). Its log-loss/Brier are the true uniform-model values.

## The three questions, answered

### 1. Do our 49 features beat simple Elo? **No — they slightly *lose* to it.**
- **Elo-only (3 features): 188/380, log-loss 1.078, Brier 0.647.**
- **Our V1 (49 features): 185/380, log-loss 1.084, Brier 0.654.**

The 46 extra engineered features (form, league position, H2H, home/away splits, rolling
goals) add **−3 matches of accuracy and worse calibration** vs raw Elo. Elo already
encapsulates team strength; the rest is mostly noise the model overfits to. **This is the
headline finding: V1 is over-engineered.** It mirrors the WC2026 lesson — simplicity and a
strong single signal (Elo) beat feature cleverness.

### 2. How far are we from bookmakers? **Level on accuracy, behind on calibration.**
- **Accuracy:** V1 48.7% vs Bet365 48.9% — a **0.3 pp gap**. We pick winners as well as the market.
- **Calibration:** Bet365 log-loss **1.019** vs our 1.084 (Brier 0.612 vs 0.654). The bookmaker's
  *probabilities* are meaningfully better even though its argmax accuracy is the same.

### 3. Where is the gap? **Probability calibration, not winner-picking.**
We are essentially at bookmaker *accuracy*, but ~**0.065 log-loss** behind on probability
quality. The market prices in information we don't have (injuries, lineups, sharp money) and
expresses it as better-calibrated odds. **The V2 frontier is calibration, not accuracy.**

### Bonus: draw-blindness is *universal*
Bet365 predicts **0/104 draws** as the single most-likely outcome; Elo 2; V1 4. Even the
market never makes a draw its top pick — draws aren't a modeling failure, they're structurally
un-favourite (the true most-likely outcome is almost always a team). Our draw-blindness is
normal, not a bug.

## Verdict — V1 is competitive but over-built
- **At bookmaker-level accuracy (~49%)** — a legitimate, useful predictor.
- **Beaten by a 3-feature Elo model** on both accuracy and calibration — so the 49-feature
  pipeline is not earning its complexity.
- **Calibration is the gap to close**, and it likely needs market/lineup/xG signal, not more
  of the same engineered features.

## Recommendations for V2
1. **Simplify.** Start from Elo + a *small* set of proven features; add engineered features only
   if they beat Elo-only on the holdout (most here did not).
2. **Chase calibration, not accuracy.** Temperature/Platt calibration on the probabilities;
   consider blending the market's implied odds as a feature or prior.
3. **Add genuinely new signal:** xG (from the FPL/Understat full clone), injuries/lineups, rest
   days — the information the bookmaker has that we don't.
4. **Stop trying to "fix" draws by argmax** — instead report calibrated draw probability (the
   two-stage gate from Phase 3b does this well: holdout log-loss 1.066, better than V1's 1.084).

## V1 frozen reference
- **Accuracy:** 185/380 (48.7%) holdout · 203/380 (53.4%) validation.
- **Log-loss:** 1.084 holdout.
- **Benchmark position:** = bookmaker accuracy, −0.065 log-loss vs bookmaker, ≈ Elo-only.
- **Models:** `pl_model_a_final.pkl`, `pl_model_b_final.pkl` (+ optional `pl_draw_gate_final.pkl`).
