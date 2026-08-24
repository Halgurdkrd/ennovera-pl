# Ennovera PL Predictor — V3 Layered System: Training Report

**Verdict up front: V3 did NOT hit the 55% target, and does NOT beat V2 on any
backtestable feature.** The layered-FPL premise cannot be *proven* with our data, because
the signals that might reach 55% (historical xG, injuries/availability, per-season FPL
strength) **do not exist historically** — the FPL API serves only a current snapshot, and the
full player-history clone was never completed. This is the same conclusion the V1/V2 work
reached: we're at bookmaker accuracy; the remaining gap is data we don't have.

## Full comparison table — BACKTESTABLE configs (val 2024-25, holdout 2025-26)

| Config | Val acc | Val LL | Hold acc | Hold LL | Keep? |
|---|---|---|---|---|---|
| **V2 baseline (Elo+Platt, 3f)** | 197/380 | 1.010 | 184/380 | 1.053 | ref |
| Layer 1 (split Elo, 6f) | **203/380** | **1.003** | 177/380 | 1.072 | ❌ overfit val, worse holdout |
| LSTM (10-match seq) | 191/380 | 1.024 | 172/380 | 1.053 | ❌ worse |
| **XGBoost + LSTM (50/50)** | 196/380 | 1.010 | **187/380** | **1.045** | ⚠️ best holdout, but tied val |
| Layer 1+2 (strength) | — | — | — | — | 🚫 not backtestable |
| Layer 1+2+3 (form/xG) | — | — | — | — | 🚫 not backtestable |
| Layer 1+2+3+4 (pre-match) | — | — | — | — | 🚫 not backtestable |
| Stacked | — | — | — | — | 🚫 not backtestable |
| **Bet365 benchmark** | — | — | 186/380 | 1.019 | ref |

**Target: >210/380 (55%) on both seasons, log-loss <1.020. → NOT MET.** Best holdout
accuracy is 187/380 (49.2%); the only config to clear 55% on validation (Layer 1, 203) then
*failed* the holdout (177). Nothing hits 55% on both.

## Layer-by-layer findings

- **Layer 1 (split attack/defence Elo):** BETTER on validation (203 vs 197) but WORSE on
  holdout (177 vs 184) — a textbook overfit-to-validation. Splitting Elo adds parameters
  without robust signal. **Rejected → keep regular Elo (V2's).** (Per your own rule.)
- **Layers 2-4 (FPL strength / xG-form / availability):** **cannot be backtested.** They need
  each *past* match's contemporaneous FPL data; we have only today's snapshot. Applying current
  values to 2024-25 matches is anachronistic *and* a leak. So no honest holdout number exists —
  I built them as **live-season overlays** (see below), not validated model components.
- **LSTM (Step 10):** alone it's worse than V2 (172 vs 184 holdout) — LSTMs overfit 2,660
  matches. The **XGBoost+LSTM 50/50 blend** is the one bright spot: **holdout 187/380 (best,
  beats Bet365's 186) and log-loss 1.045 (best after Bet365)**. But it's only *tied* with V2 on
  validation (196 vs 197), so it does **not** clear the "beat V2 on BOTH seasons" bar. The
  3-match holdout gain is within noise and adds a TensorFlow dependency — **not worth it.**
- **Stacking (Step 11):** skipped — with Layers 2-4 unbacktestable there's nothing meaningful
  to stack; stacking the split-Elo/LSTM variants would just relearn the overfit.

## What V3 actually is
**V3 = the validated V2 base (regular Elo + Platt) + Layer 2/4 FPL overlays applied at
prediction time for the live 2026-27 season.** The overlays are *principled but UNVALIDATED*
heuristics (fixed coefficients, clipped to ±6%). They look sensible — but we have no evidence
they improve accuracy, and they must be treated as experimental.

## V2 vs V3 predictions (the overlays in action)
The FPL squad data drives exactly the hypothesized shifts:

**Champion probability:**
| Team | V2 | V3 | why |
|---|---|---|---|
| Manchester City | 54.6% | **51.7%** | high key-player dependency (0.40) → downgraded |
| Arsenal | 31.2% | **36.0%** | balanced squad → upgraded |
| Manchester United | 2.2% | 3.5% | low dependency (0.275) → upgraded |

**Biggest match changes (all ±6%, the clip limit):** Coventry (promoted, thin squad)
downgraded across all fixtures; Man Utd & Arsenal upgraded; Tottenham (high dependency, low
cohesion) downgraded. The signal is intuitive — City's reliance on one player, Coventry's weak
squad — but again, **unproven**.

## Confidence display (Step 15)
Each prediction carries **HIGH** (both teams established) or **LOW** (a promoted team involved)
— e.g. `Man Utd 77% (HIGH) vs Ipswich`, `Coventry 18% (LOW) vs Hull`. (A MEDIUM tier for
new-manager/injury cases needs live availability data, absent pre-season.)

## Honest conclusion
1. **The 55% target is not achievable with the data we have.** No config beats V2 on both
   seasons; split Elo overfits, LSTM doesn't hold up, and the FPL layers can't be validated.
2. **V2 remains the honest production model** (bookmaker-level accuracy, best-validated).
3. **The V3 overlays are a reasonable *live-season experiment*** — deploy them shadowed
   (log V2 and V3, compare as real 2026-27 results arrive) rather than as the trusted model.
4. **The real path to 55%+ is unchanged:** genuinely new signal — *historical* xG (finish the
   vaastav clone; note real xG only exists 2022-23+), lineups, and market odds — not more
   engineered features or deeper models on the data we already have.

### Artifacts
`data/v3/` (fpl_team_strength / players / fdr / squad_features .json, split_elo.csv,
current_split_elo.json), `data/experiments/v3_layer_tests.json`,
`data/predictions/v3_predictions.json`. No V2 files modified.
