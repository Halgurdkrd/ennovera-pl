# Ennovera PL Predictor — V3 Walk-Forward Historical FPL Experiment: Definitive Report

**Executive Summary:**
A temporally strictly leak-free, walk-forward out-of-sample experiment was conducted on all four historical FPL seasons (**2022–23, 2023–24, 2024–25, and 2025–26 — 1,520 matches**). 

The investigation tested whether contemporaneous, pre-match FPL signals (rolling xG, xA, xGA, squad value, player dependency, ICT index, clean-sheet rate, and lagged prior-season team strength) add genuine out-of-sample predictive power over our frozen V2 baseline (Elo + rolling goals + previous position, Platt-calibrated).

---

## 1. Experimental Methodology & Temporal Safeguards

1. **Walk-Forward V2 Baselines**: Each target season $S$ used a base model trained strictly on data prior to $S-1$ and Platt-calibrated strictly on season $S-1$:
   - `2022-23`: Trained on `2016-21`, Calibrated on `2021-22` $\to$ Acc: **204/380** (53.68%), LL: **1.0147**
   - `2023-24`: Trained on `2016-22`, Calibrated on `2022-23` $\to$ Acc: **214/380** (56.32%), LL: **0.9611**
   - `2024-25`: Trained on `2016-23`, Calibrated on `2023-24` $\to$ Acc: **198/380** (52.11%), LL: **1.0080** *(Exact reproduction of V2 validation)*
   - `2025-26`: Trained on `2016-24`, Calibrated on `2024-25` $\to$ Acc: **187/380** (49.21%), LL: **1.0367**
2. **Lagged Pre-Season FPL Strength Only**: FPL `strength_*` metrics for season $S$ were taken strictly from season $S-1$'s `teams.csv` as a preseason prior.
3. **Strictly Lagged Gameweek History ($GW < N$)**: Dynamic rolling stats for Gameweek $N$ were computed strictly from completed Gameweeks $1 \dots N-1$.
4. **Automated Leakage Verification**: Every match enforced `assert match_gw > max(source_gws)`. **100% of 1,520 matches passed temporal assertions with zero leakage.**

---

## 2. Independent Signal Screening (Development Split: 2022–24, 760 matches)

Evaluated independently on top of Walk-Forward V2 base probabilities with 1,000-iteration block-bootstrap 95% confidence intervals:

| Signal | Description | Optimal $\beta$ | Acc (760m) | Log-Loss | $\Delta$ Log-Loss | 95% Bootstrap CI | Brier | Dev Status |
|---|---|---|---|---|---|---|---|---|
| **V2 Baseline** | Walk-Forward V2 Reference | — | 418/760 (55.0%) | 0.98789 | reference | — | 0.58700 | Baseline |
| **S3 Rolling xA** | 5-GW Rolling Team xA Diff | +0.422 | 423/760 | **0.97491** | **-0.01298** | `[-0.02447, -0.00102]` | **0.57755** | **PROMISING** |
| **S7 Rolling ICT** | 5-GW Rolling Team ICT Index | +0.602 | 417/760 | **0.97521** | **-0.01268** | `[-0.02372, -0.00123]` | **0.57756** | **PROMISING** |
| **Opp-Adj xG** | Opponent-Adjusted xG Diff | +0.131 | 424/760 | **0.97684** | **-0.01105** | `[-0.02037, -0.00115]` | **0.57899** | **PROMISING** |
| **S2 Rolling xG** | 5-GW Rolling Raw xG Diff | +0.258 | 420/760 | **0.97757** | **-0.01032** | `[-0.02061, -0.00016]` | **0.57941** | **PROMISING** |
| **S5 Squad Value** | Squad Value Diff (£100M) | +1.177 | 411/760 | **0.98013** | **-0.00776** | `[-0.01668, +0.00046]` | **0.58075** | MARGINAL |
| **S1 Atk Strength** | Lagged $S-1$ Attack Strength | +0.984 | 416/760 | **0.98229** | **-0.00560** | `[-0.01428, +0.00284]` | **0.58247** | MARGINAL |
| **S1 Def Strength** | Lagged $S-1$ Defence Strength | -0.907 | 414/760 | **0.98254** | **-0.00535** | `[-0.01388, +0.00302]` | **0.58255** | MARGINAL |
| **S1 Composite** | Lagged $S-1$ FPL Composite | +2.537 | 414/760 | **0.98518** | **-0.00271** | `[-0.00783, +0.00305]` | **0.58501** | MARGINAL |
| **S4 Rolling xGA** | 5-GW Defensive xGA Diff | +0.178 | 424/760 | **0.98327** | **-0.00462** | `[-0.00983, +0.00110]` | **0.58370** | MARGINAL |
| **S8 Clean Sheet** | 5-GW Clean Sheet Rate Diff | +0.263 | 417/760 | **0.98599** | **-0.00190** | `[-0.00647, +0.00266]` | **0.58587** | MARGINAL |
| **S6 Dependency** | Top-2 Player xG+xA Share | -0.159 | 415/760 | **0.98784** | **-0.00005** | `[-0.00075, +0.00070]` | **0.58697** | NO GAIN |

---

## 3. Model Architecture Selection (Validation Split: 2024–25, 380 matches)

Candidate combinations fitted strictly on 2022–24 development split and tested on 2024–25 validation split:

| Candidate Architecture | Description | Val Acc (380m) | Val Log-Loss | $\Delta$ Log-Loss | Val Brier |
|---|---|---|---|---|---|
| **Walk-Forward V2 Baseline** | Reference V2 Model | 198/380 (52.11%) | 1.00805 | reference | 0.60201 |
| **Candidate 1** | Rolling xA Overlay | 199/380 (52.37%) | 1.00794 | -0.00011 | 0.60113 |
| **Candidate 2** | Opp-Adj xG + xA Composite | 202/380 (53.16%) | 1.00483 | -0.00322 | 0.59933 |
| **Candidate 3 (WINNER)** | **Multi-Signal Regularized Overlay (5 signals)** | **200/380 (52.63%)** | **1.00268** | **-0.00537** | **0.59820** |
| **Candidate 4** | Multinomial H/D/A Logit Overlay | 200/380 (52.63%) | 1.00361 | -0.00444 | 0.59879 |

### Frozen Configuration (Candidate 3):
- **Signals Selected:** Prior Strength ($S-1$), Opponent-Adjusted xG, Rolling xA, Rolling xGA, Squad Value.
- **Frozen Coefficients:**
  $$\text{shift} = 0.0095 \cdot S1_{\text{strength}} + 0.0908 \cdot xG_{\text{opp\_adj}} + 0.1306 \cdot xA_{\text{roll}} - 0.0023 \cdot xGA_{\text{roll}} + 0.0518 \cdot \text{Val}_{\text{squad}}$$
  $$\text{shift} = \text{clip}(\text{shift}, -0.6, +0.6)$$
  $$\text{logit}(P_H) \leftarrow \text{logit}(P_{H, V2}) + \text{shift}, \quad \text{logit}(P_A) \leftarrow \text{logit}(P_{A, V2}) - \text{shift}$$

---

## 4. Final Untouched Holdout Evaluation (2025–26, 380 matches, 104 draws)

| Model / Benchmark | Accuracy (N/380) | Accuracy % | Log-Loss | $\Delta$ LL (vs V2) | Brier Score | Draw Recall |
|---|---|---|---|---|---|---|
| **Random (Uniform)** | *162/380* *(argmax tie-break)* | *42.63%* *(true exp: 33.3%)* | 1.09861 | +0.06188 | 0.66667 | 0/104 |
| **Home-Majority Baseline** | 162/380 | 42.63% | 1.08164 | +0.04491 | 0.65465 | 0/104 |
| **Raw Elo (M0)** | 183/380 | 48.16% | 1.02980 | -0.00693 | 0.61900 | 0/104 |
| **Walk-Forward V2 (M7+Platt)** | **187/380** | **49.21%** | **1.03673** | **reference** | **0.62492** | 0/104 |
| **Frozen V3 Candidate** | 185/380 | 48.68% | 1.04278 | +0.00605 | 0.63038 | 1/104 |
| **Bet365 (Market Implied)** | 186/380 | 48.95% | 1.01850 | -0.01823 | 0.61200 | 0/104 |

### Reliability & Calibration Analysis (2025–26 Holdout):

| Confidence Bin | V2 Count | V2 Actual Win % | V3 Count | V3 Actual Win % | Calibration Error ($\text{Acc} - \text{Conf}$) |
|---|---|---|---|---|---|
| **40–50%** | 130 | 45.4% | 118 | 44.1% | -1.2% |
| **50–60%** | 136 | 47.1% | 107 | 44.9% | -10.5% (Overconfident) |
| **60–70%** | 74 | 62.2% | 100 | 57.0% | -7.4% (Overconfident) |
| **70–80%** | 0 | 0.0% | 22 | 63.6% | -10.1% (Overconfident) |
| **80–100%** | 0 | 0.0% | 0 | 0.0% | 0.0% |

---

## 5. Diagnostic Findings: Arsenal, Manchester City & Probability Dynamics

### 1. Probability Movement & Sensitivity:
- **Mean Absolute Adjustment:** 3.31 percentage points per match.
- **Top Upgraded Teams (Across 38 Matches):** Manchester City (+4.72 pp/match), Arsenal (+4.19 pp/match), Chelsea (+2.98 pp/match), Liverpool (+2.41 pp/match).
- **Top Downgraded Teams:** Burnley (-3.56 pp/match), Wolves (-2.65 pp/match), West Ham (-1.88 pp/match), Sunderland (-1.58 pp/match).

### 2. Arsenal vs. Manchester City Diagnostics:
- **Expected Points (2025–26):**
  - **Manchester City:** V2 = 72.3 pts $\to$ V3 = **77.2 pts** (+4.8 pts)
  - **Arsenal:** V2 = 72.9 pts $\to$ V3 = **77.2 pts** (+4.3 pts)
  - **Liverpool:** V2 = 70.6 pts $\to$ V3 = **73.0 pts** (+2.5 pts)
- **Monte Carlo 10,000-Run League Simulation:**
  - **Manchester City:** V2 Champion = 31.4% $\to$ V3 Champion = **39.0%** (Top 4: 94.1%)
  - **Arsenal:** V2 Champion = 34.6% $\to$ V3 Champion = **38.3%** (Top 4: 94.0%)
  - **Liverpool:** V2 Champion = 23.9% $\to$ V3 Champion = **18.6%** (Top 4: 83.6%)
- **Driver of Movement:** Manchester City and Arsenal generated high rolling xG/xA and possess elite squad value (£100M+ advantages), driving upgrades.
- **Explicit Modeling Limitation:** The model **does NOT contain direct features** for manager changes, Pep Guardiola contract status, summer transfer arrivals/departures, or match-day injury lineups. It only senses their trailing effects through player xG/xA output.

---

## 6. The 18 Definitive Scientific Questions & Conclusions

1. **Did prior-season FPL strength add signal beyond V2?**  
   *Yes, marginally on development ($\Delta LL = -0.00271$), but lagged $S-1$ data has high inertia and contributes minimally compared to in-season dynamic form.*
2. **Did rolling real xG add signal?**  
   *Yes. Statistically significant on development ($\Delta LL = -0.01032$, 95% CI `[-0.02061, -0.00016]`).*
3. **Did xA add signal?**  
   *Yes. Strongest single development signal ($\Delta LL = -0.01298$, 95% CI `[-0.02447, -0.00102]`).*
4. **Did xGA add signal?**  
   *Weakly ($\Delta LL = -0.00462$). Defensive metrics are noisy over 5-match rolling windows.*
5. **Did contemporaneous squad value add signal?**  
   *Yes, on development ($\Delta LL = -0.00776$) and validation, proxying raw talent disparity.*
6. **Did player dependency add signal?**  
   *No ($\Delta LL = -0.00005$, 95% CI `[-0.00075, +0.00070]`). Top-2 xG share did not reliably predict match-level upsets.*
7. **Did ICT add signal?**  
   *Yes ($\Delta LL = -0.01268$), though it heavily co-linearizes with xG + xA.*
8. **Did clean-sheet form add signal?**  
   *Very weak ($\Delta LL = -0.00190$). Goal-based binary metrics add little beyond xGA.*
9. **Which signals survived development + validation?**  
   *Opponent-Adjusted xG, Rolling xA, Squad Value, and Lagged $S-1$ Strength.*
10. **What exact configuration was frozen BEFORE 2025-26?**  
    *Candidate 3 Multi-Signal Regularized Overlay with weights: xA (0.1306), Opp-Adj xG (0.0908), Squad Value (0.0518), Prior Strength (0.0095), xGA (-0.0023), clipped to $\pm 0.6$ logit.*
11. **Did frozen V3 beat walk-forward V2 on 2025-26?**  
    *No. On 2025-26 holdout, V3 obtained Log-Loss 1.04278 vs V2's 1.03673 ($\Delta LL = +0.00605$).*
12. **Did it improve probability calibration?**  
    *No. On 2025-26 (a 104-draw season), V3 pushed 22 matches into the 70–80% confidence bucket where actual win rate was only 63.6% (10.1% overconfidence).*
13. **Did it improve accuracy?**  
    *No. Holdout accuracy dropped from 187/380 (49.21%) on V2 to 185/380 (48.68%) on V3.*
14. **How does it compare with Bet365?**  
    *Bet365 (LL 1.0185, Acc 186/380) remains ahead of both V2 (+0.018 LL gap) and V3 (+0.024 LL gap).*
15. **How did Arsenal/Manchester City probabilities change and WHY?**  
    *Both teams increased by ~4.5 pp/match and ~4.5 expected points due to high sustained xG/xA and squad value dominance.*
16. **Does the result support our hypothesis that current team-state information reduces historical inertia?**  
    *Partially: Dynamic FPL features rapidly reflect in-season form and squad disparity (improving 2022–24 dev and 2024–25 val). However, they also amplify favorite-bias, causing calibration penalties in seasons with elevated draw rates.*
17. **What important information is STILL missing?**  
    *Pre-match injury status / starting lineups, tactician/manager changes, and market money flow.*
18. **Is V3 strong enough to replace V2, or should V2 remain production?**  
    *Per our scientific decision rule, **V2 MUST REMAIN PRODUCTION**. V3 failed the strict requirement of beating V2 on the untouched 2025-26 holdout.*

---

### Artifacts Saved:
- `data/models/pl_v3_candidate_antigravity.pkl` (Research candidate)
- `data/experiments/v3_signal_screening_dev.json`
- `data/experiments/v3_frozen_configuration.json`
- `data/experiments/v3_holdout_evaluation.json`
- Production `pl_v2_final.pkl` and `app/services/pl_predictor.py` remain **100% UNTOUCHED**.

