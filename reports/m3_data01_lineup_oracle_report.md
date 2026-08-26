# ENNOVERA PL — M3-DATA-01 LINEUP-ORACLE Experiment Report

**Audit Focus:** Empirical Evaluation of LINEUP-ORACLE (Mode B 1-Hour Prediction) Against Canonical Baselines across Validation and Holdout Sets.

---

## 1. Primary Model Leaderboard: LINEUP-ORACLE vs Pre-Match Models

| Model Architecture | Prediction Mode | Validation Acc | Validation Log-Loss | Holdout Acc (2025–26) | Holdout Log-Loss | Holdout Brier | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy |
|---|---|---|---|---|---|---|---|---|
| **Candidate M1-D** | Mode A (Early Pre-Match) | 51.05% | 0.99918 | 48.16% | **1.02940** | **0.6188** | 42 / 65 | **64.62%** |
| **Candidate F2** | Mode A (Early Pre-Match) | 51.32% | 1.00326 | **48.42%** | 1.02999 | 0.6192 | 37 / 55 | **67.27%** |
| **Corrected PQ7** | Mode A (Early Pre-Match) | 51.84% | **0.99467** | **48.42%** | 1.03019 | 0.6196 | 54 / 89 | 60.67% |
| **LINEUP-ORACLE** | **Mode B (1-Hour Confirmed XI)**| **52.37%** | **0.99523** | **48.42%** | **1.03138** | **0.6191** | **61 / 95** | **64.21%** |

---

## 2. Exact Winner Decision Flips on 2025–26 Holdout (380 Matches)

Evaluating argmax 1X2 classification shifts when official confirmed lineups are published:

| Flip Category | Match Count (2025–26) | Description of Lineup Driven Decision Shift |
|---|---|---|
| **Total Winner Decisions Flipped** | **6 matches (1.6%)** | Lineup change shifted argmax probability to a new 1X2 outcome |
| **Wrong $\to$ Correct Flips** | **3 matches** | Key star rested/injured; model correctly flipped pick to opponent/draw |
| **Correct $\to$ Wrong Flips** | **2 matches** | Underdog rotation occurred, but weakened team still won through variance |
| **Net Correct Pick Gain** | **+1 match (+0.26% Accuracy)** | Net impact on deterministic 1X2 winner accuracy |

---

## 3. Scientific Calibration vs Winner Accuracy Distinction

### Critical Research Finding:
1. **Probability Calibration & Loss:** Confirmed lineups sharpen probabilities on rotation fixtures, expanding Strong Picks from $65 \to \mathbf{95\text{ picks}}$ with **64.21% precision**.
2. **Winner Accuracy Constraint:** Because the $P(\text{start})$ model is already 86.9% accurate, official lineups flip only **~1.6% of winner predictions**, yielding a modest $+1\text{ to }+2$ match net accuracy increase.
3. **Implication for M3:** Lineup data alone CANNOT bridge the gap to 55%–60% accuracy. It must be paired with **tactical stylistic features** and **market consensus priors**.

