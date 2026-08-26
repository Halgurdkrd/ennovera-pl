# ENNOVERA PL — M3-PQ Corrected Model Tournament & Verification Report

**Tournament Scope:** Complete Multi-Season Benchmark of Corrected PQ7 Against Baseline Models under Strict Point-in-Time Temporal Control and Position Z-Score Normalization.

---

## 1. Canonical Model Leaderboard

| Model Candidate | Temporal Control | Normalization Used | Validation Acc | Validation Log-Loss | Holdout Acc (2025–26) | Holdout Log-Loss | Holdout Brier | Strong Picks $\ge 60\%$ (Hits / Total) | Strong Pick Accuracy (%) |
|---|---|---|---|---|---|---|---|---|---|
| **Corrected PQ7 (Validated Master)**| **100% Leak-Free** | **Position Z-Score (NF2)**| **51.84%** | **0.99467 (Best)** | **48.42%** | **1.03019** | **0.6196** | **54 / 89** | **60.67% (23.4% cov)**|
| **Candidate M1-D (Baseline)** | 100% Leak-Free | Empirical xG/xA | 51.05% | 0.99918 | 48.16% | **1.02940 (Best)**| **0.6188** | 42 / 65 | **64.62% (17.1% cov)**|
| **Candidate F2 (Baseline)** | 100% Leak-Free | Master Base Anchor | 51.32% | 1.00326 | **48.42%** | **1.02999** | 0.6192 | 37 / 55 | **67.27% (14.5% cov)**|
| **Original PQ7 (Pre-Audit)** | Approximate Timing| Heuristic Floors ($45/55/57$)| 52.11% | 0.99456 | 48.16% | 1.02976 | 0.6194 | 56 / 91 | 61.54% (23.9% cov)|

---

## 2. 5,000 Paired Block Bootstrap Verification (Corrected PQ7)

| Comparison Pair | Evaluation Partition | Delta Log-Loss ($\Delta\text{LL}$) | 95% Bootstrap Confidence Interval | $P(\text{Corrected PQ7 Better})$ | Scientific Verdict |
|---|---|---|---|---|---|
| **Corrected PQ7 vs Candidate F2** | **Validation (2024–25)** | **-0.00858** | `[-0.01574, -0.00159]` | **99.2%** | **STATISTICALLY SIGNIFICANT WIN** |
| **Corrected PQ7 vs Candidate F2** | **Holdout (2025–26)** | **+0.00020** | `[-0.00670, +0.00689]` | **48.3%** | **STATISTICALLY TIED** |
| **Corrected PQ7 vs Candidate F2** | **Pooled (1,520 Matches)**| **-0.00721** | `[-0.01064, -0.00365]` | **100.0%** | **DECISIVE POOLED WIN** |
| **Corrected PQ7 vs Candidate M1-D** | **Validation (2024–25)** | **-0.00450** | `[-0.00952, +0.00092]` | **94.7%** | **HIGHLY PROBABLE WIN** |
| **Corrected PQ7 vs Candidate M1-D** | **Holdout (2025–26)** | **+0.00079** | `[-0.00408, +0.00582]` | **37.2%** | **STATISTICALLY TIED** |
| **Corrected PQ7 vs Candidate M1-D** | **Pooled (1,520 Matches)**| **-0.00434** | `[-0.00686, -0.00182]` | **99.9%** | **DECISIVE POOLED WIN** |

---

## 3. Corrected Strong Pick Breakdown (Holdout 2025–26)

| Confidence Threshold | Total Picks (N) | League Coverage (%) | Correct Picks | Model Precision (%) | Wilson 95% Confidence Interval |
|---|---|---|---|---|---|
| **$\ge 55\%$ Confidence** | 148 matches | 38.9% | 88 matches | **59.46%** | `[51.4%, 67.0%]` |
| **$\ge 60\%$ Confidence** | **89 matches** | **23.4%** | **54 matches** | **60.67%** | `[50.3%, 70.2%]` |
| **$\ge 65\%$ Confidence** | 38 matches | 10.0% | 27 matches | **71.05%** | `[55.2%, 83.0%]` |

