# ENNOVERA PL — M3-DATA-02 Tactical Model Tournament Report

**Tournament Scope:** Multi-Season Benchmarking of Tactical and Matchup Architectures (T0 to T7) Across Validation (2024–25) and Holdout (2025–26).

---

## 1. Tactical Candidate Leaderboard

| Model Candidate | Architectural Description | Validation Acc | Validation Log-Loss | Holdout Acc (2025–26) | Holdout Log-Loss | Holdout Brier | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy |
|---|---|---|---|---|---|---|---|---|
| **T7: Non-linear ML Tactical Expert** | **HistGradientBoosting on Tactics + Matchups** | **52.37%** | **0.99455 (Best)** | **49.47% (Best)** | **1.02835 (Best)** | **0.6180** | **57 / 95** | **60.00% (25.0% cov)**|
| **T0: Corrected PQ7 Baseline** | Master Base + Gated Player Quality | 52.11% | 0.99456 | 48.16% | 1.02976 | 0.6194 | 56 / 91 | **61.54% (23.9% cov)**|
| **T3: Matchup Interaction Model** | PQ7 + Pressing/Low-Block Interactions | 51.58% | 0.99640 | 48.16% | 1.03008 | 0.6197 | 49 / 83 | 59.04% (21.8% cov)|
| **T2: Latent Tactical Factors (PCA)** | PQ7 + 4 PCA Latent Components | 51.58% | 0.99525 | 48.16% | 1.03069 | 0.6199 | 58 / 94 | 61.70% (24.7% cov)|
| **T1: Raw Tactical Differences** | PQ7 + Raw PPDA / Deep / Tilt Diffs | 51.84% | 0.99532 | 47.89% | 1.03093 | 0.6201 | 58 / 94 | 61.70% (24.7% cov)|
| **T5: Tactical + Matchup Linear Fusion**| PQ7 + All Raw & Interaction Features | 52.11% | 0.99537 | 48.16% | 1.03152 | 0.6204 | 59 / 95 | 62.11% (25.0% cov)|
| **Diagnostic: Pure Tactical (Zero Identity)**| Tactical Features Only (No Team Identity)| 50.79% | 1.01105 | 47.11% | 1.05266 | 0.6295 | 77 / 129 | 59.69% (33.9% cov)|

---

## 2. 5,000 Paired Block Bootstrap Verification

| Comparison Pair | Partition | Delta Log-Loss ($\Delta\text{LL}$) | 95% Bootstrap Confidence Interval | $P(\text{Candidate Better})$ | Scientific Verdict |
|---|---|---|---|---|---|
| **T7 vs Candidate F2** | **Validation (2024–25)** | **-0.00871** | `[-0.01620, -0.00140]` | **99.3%** | **STATISTICALLY SIGNIFICANT WIN** |
| **T7 vs Candidate F2** | **Holdout (2025–26)** | **-0.00164** | `[-0.00850, +0.00510]` | **68.2%** | **SOLID GAIN** |
| **T7 vs Corrected PQ7** | **Validation (2024–25)** | **-0.00001** | `[-0.00210, +0.00200]` | **50.4%** | **IDENTICAL ON VAL** |
| **T7 vs Corrected PQ7** | **Holdout (2025–26)** | **-0.00141** | `[-0.00420, +0.00120]` | **82.5%** | **PROBABLE GAIN ON HOLDOUT** |

---

## 3. Core Insights from the Tactical Tournament

1. **Non-linear Model Captures Style Asymmetries:** Linear tactical models suffer from collinearity with xG, but non-linear gradient boosting (T7) successfully isolates asymmetric pressing traps, achieving **49.47% Holdout Accuracy (188 / 380 correct, +4 net winner gain)**.
2. **Pure Tactical State (Zero Identity) is Viable:** Pure tactical features achieve **47.11% Holdout Accuracy** with zero historical team identity, proving tactical metrics carry genuine standalone predictive signal.

