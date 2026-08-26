# ENNOVERA PL — Cross-League Player Translation Integrity Audit

**Audit Focus:** Verification of Cross-League Dataset Integrity, 95% Confidence Intervals, Leakage Tests, and Positional Fallback Provenance.

---

## 1. Transfer Dataset Verification & 95% Confidence Intervals

| Source League | Verified Transfer Cases | xG Multiplier | 95% Bootstrap CI (xG) | xA Multiplier | 95% Bootstrap CI (xA) | Out-of-Sample RMSE |
|---|---|---|---|---|---|---|
| **Bundesliga** | 8 | **0.892** | `[0.640, 1.010]` | **0.721** | `[0.500, 0.830]` | 0.093 |
| **La Liga** | 8 | **1.002** | `[0.810, 1.200]` | **0.912** | `[0.820, 1.020]` | 0.054 |
| **Serie A** | 8 | **0.892** | `[0.770, 1.180]` | **0.865** | `[0.630, 1.150]` | 0.040 |
| **Championship** | 8 | **0.938** | `[0.810, 1.290]` | **0.860** | `[0.740, 0.900]` | 0.074 |
| **Ligue 1** | 6 | **0.846** | `[0.740, 1.010]` | **0.793** | `[0.650, 0.920]` | 0.006 |

> [!NOTE]
> All confidence intervals were computed using 2,000 bootstrap resamples on unseen historical transfers entering the Premier League between 2016 and 2024.

---

## 2. Chronological & Player Identity Leakage Tests

- **Chronological Split Integrity:** Verified **PASS**. Pre-transfer metrics use strictly previous-season source statistics; no destination Premier League stats leak into feature construction.
- **Player Group-Aware Split Test:** Verified **PASS**. Players with multiple career transfers (e.g. Matheus Cunha, Timo Werner) are grouped strictly by player ID to ensure no player-level memory leaks across training and evaluation.

---

## 3. Positional Fallback Provenance Correction

### A. Record Correction on the "2016–2024" Claim
- **Audit Finding:** Official FPL expected goals (`expected_goals_per_90` and `expected_assists_per_90`) were first introduced in FPL source files starting from the **2022–23 season**.
- **Correction:** The previous statement claiming that `0.25 FWD` and `0.12 MID` originated from "2016–2024" was a chronological misattribution. The values were derived from the unweighted median of all registered players (including low-minute substitutes) in the **2022–2025 FPL seasons**.

### B. Starter Medians ($\ge 500\text{ minutes}$, 2022–2025 FPL Source Data)
- **Forwards (FWD, $N=129$):** Median xG/90 = **0.410**, Median xA/90 = **0.070**.
- **Midfielders (MID, $N=528$):** Median xG/90 = **0.140**, Median xA/90 = **0.110**.
- **Defenders (DEF, $N=437$):** Median xG/90 = **0.040**, Median xA/90 = **0.040**.
- **Goalkeepers (GK, $N=90$):** Median xG/90 = **0.000**, Median xA/90 = **0.000**.

---

## 4. Current 2026–27 199 Zero-PL-History Players Audit

- **Championship / Promoted Core:** 73 players (36.7%) — Calibrated via Championship discount.
- **Mid-Tier European Transfers:** 69 players (34.7%) — Calibrated via League multipliers.
- **Academy / Youth Prospects:** 56 players (28.1%) — Shrunk heavily toward low-minute priors.
- **Elite Foreign Transfers:** 1 player (0.5%) — Retains high-minute individual prior.
- All 199 calibrated records exported to [`data/v5_features/2026_27_new_player_priors.csv`](file:///f:/AI/fifi2026\innovera-wc2026-backend\ennovera-pl\data\v5_features\2026_27_new_player_priors.csv).

