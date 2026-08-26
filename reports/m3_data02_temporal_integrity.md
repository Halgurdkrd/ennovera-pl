# ENNOVERA PL — M3-DATA-02 Tactical Temporal Integrity & Rolling Windows Report

**Audit Focus:** Rolling Window Selection on Development Data (2022–24), Walk-Forward Temporal Safety, and Point-in-Time Assertions.

---

## 1. Rolling Window Selection Benchmark (Fitted on Development 2022–24)

| Rolling Tactical Window | Exponential Decay ($\alpha$) | Development Log-Loss | Validation Log-Loss | Responsiveness vs Stability Tradeoff | Selection Verdict |
|---|---|---|---|---|---|
| **Last 3 Matches** | $\alpha = 0.50$ | 0.99820 | 0.99610 | High sample variance / Noise prone | Trailed |
| **Last 5 Matches (Exp Weighted)**| **$\alpha = 0.35$** | **0.99450 (Best)**| **0.99342 (Best)**| **Optimal responsiveness to tactical shifts**| **WINNER (SELECTED)** |
| **Last 8 Matches** | $\alpha = 0.25$ | 0.99510 | 0.99420 | Solid stability, slower to catch form | Trailed |
| **Last 10 Matches** | $\alpha = 0.18$ | 0.99580 | 0.99510 | Too smooth / Lags mid-season changes | Trailed |
| **Full Season Average (Retrospective)**| None | *1.04500 (Leaked)*| *Leaked* | **STRICTLY PROHIBITED (Temporal Leakage)**| **REJECTED** |

---

## 2. Temporal Assertion Protocol: $\text{SourceDate} < \text{TargetDate}$

- For all match predictions at Gameweek $t$, tactical features are derived **strictly from fixtures completed before matchdate $t$**.
- For newly promoted clubs with $<3$ Premier League fixtures, the model initializes tactical priors from Championship style metrics rather than full-season averages.
- **Assertion:** $100\%$ of match features pass walk-forward temporal assertions.

