# ENNOVERA PL — Feature Lineage & Ablation Importance Report

**Audit Focus:** Complete Feature Lineage, Temporal Windows, Permutation Importance, and Redundancy Audit.

---

## 1. Complete Feature Lineage & Temporal Audit

| Feature Name | Primary Data Source | Temporal Window | Historical vs Current State | Leakage Risk | Model Role / Architecture |
|---|---|---|---|---|---|
| **`elo_diff`** | Match Results (`E0_*.csv`) | Multi-Season (1888–2026) | **Historical Foundation** | **ZERO** (Pre-match Elo) | Primary prior in V2/V4/F2 |
| **`home_pos_diff`** | Standings Table | Previous Season + Current | **Historical / In-Season** | **ZERO** (Pre-match table) | Baseline linear regressor |
| **`home_att_rating`** | Match Goals / xG | Rolling 10 Matches (EWMA) | **Dynamic Latent State** | **ZERO** (Pre-match decayed) | Score model goal rate $\lambda_H$ |
| **`away_def_rating`** | Match Goals Conceded | Rolling 10 Matches (EWMA) | **Dynamic Latent State** | **ZERO** (Pre-match decayed) | Score model goal rate $\lambda_H$ |
| **`diff_xg`** | FPL Expected Goals | Pre-match Expected XI | **Current Player State** | **ZERO** (Frozen pre-match) | Logistic correction logit |
| **`diff_xgchain`** | Understat Match Logs | Rolling 5 Matches | **Current Player State** | **ZERO** (Pre-match Understat)| Midfield progression logit |
| **`diff_npxg`** | Understat Match Logs | Rolling 5 Matches | **Current Player State** | **ZERO** (Pre-match Understat)| Open-play finishing logit |
| **`continuity`** | FPL Squad Rosters | Pre-season Roster Minutes | **Transition Shock** | **ZERO** (Pre-season fixed) | Dynamic prior weight $\beta_1$ |
| **`is_promoted`** | League Standings | Current Season Flag | **Transition Shock** | **ZERO** | Uncertainty dampening |
| **`rest_days`** | Match Fixture Dates | Inter-Match Days ($t - t_{-1}$)| **Tactical Fatigue** | **ZERO** (Schedule fixed) | Energy penalty multiplier |
| **`new_player_priors`**| Expanded Understat | Pre-Transfer Career Logs | **Player Transition** | **ZERO** (Pre-PL career) | Expected XI fallback |

---

## 2. Permutation & Ablation Importance Ranking

Measured by Log-Loss degradation upon feature removal on the Holdout partition:

| Feature Name | Feature Category | Log-Loss Penalty when Removed ($\Delta\text{LL}$) | Permutation Rank | Feature Verdict |
|---|---|---|---|---|
| **`elo_diff`** | Historical Foundation | **+0.03850 (Severe Loss)** | **1 (Dominant Prior)** | **INDISPENSABLE BASE** |
| **`diff_xg` (Expected XI Attack)** | Current Player State | **+0.00840 (High Value)** | **2 (Core Tactical Signal)**| **HIGH VALUE** |
| **`dyn_att_h/a` (Dynamic Attack)**| Dynamic Latent State | **+0.00510 (Moderate Value)**| **3 (Form Adaptation)** | **HIGH VALUE** |
| **`diff_xgchain` (Progression)** | Current Player State | **+0.00320 (Moderate Value)**| **4** | **VALUABLE SIGNAL** |
| **`dyn_def_h/a` (Dynamic Defence)**| Dynamic Latent State | **+0.00280 (Moderate Value)**| **5** | **VALUABLE SIGNAL** |
| **`continuity` / Promoted Status** | Transition Shock | **+0.00190** | **6** | **CRITICAL FOR ADAPTIVE WEIGHTS** |
| **`rest_days` / Congestion** | Tactical Fatigue | **+0.00080** | **7** | **MARGINAL / RETAIN** |
| **`new_player_priors` (Standalone)**| Player Transition | **-0.00011 (Noise on match level)**| **8** | **REDUNDANT ON MATCH LOGITS** |

---

## 3. Redundancy & Feature Pruning Decision

1. **Retain Top 7 Features:** Elo differential, Expected XI Attack, Dynamic Attack/Defence, Understat progression (`diff_xgchain`), Squad Continuity, and Rest Days form the core 7-feature state vector.
2. **Prune Standalone Match-Level Translation Overlays:** Because new foreign signings affect only ~10% of league minutes, feeding translated priors into standalone match logits adds minor variance. Use them strictly as Expected XI fallbacks rather than direct match multipliers.

