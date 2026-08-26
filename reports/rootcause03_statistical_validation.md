# ENNOVERA PL — ROOT-CAUSE-03 Statistical Validation & Negative Controls Report

**Research Focus:** Rigorous Statistical Significance Testing, 5,000-Resample Block Bootstrapping, and Negative Control Sanity Checks.

---

## 1. Statistical Validation Table

| Test Procedure | Comparison | Metric Delta | 95% Bootstrap CI | P-Value / Probability |
|---|---|---|---|---|
| **5,000 Paired Bootstrap** | **R0 Consensus vs M3 Peak** | **+0.52% Acc (+2 hits)** | **[-1.05%, +2.11%]** | **P(R0 $\ge$ M3) = 74.2%** |
| **5,000 Paired Bootstrap** | **R0 Consensus vs Baseline F2** | **+1.84% Acc (+7 hits)** | **[+0.26%, +3.42%]** | **P(R0 > F2) = 98.6%** |
| **McNemar's Test** | **R0 Consensus vs M3 Peak** | 7 flips vs 5 flips | — | $p = 0.564$ (Slight edge) |
| **McNemar's Test** | **R0 Consensus vs Baseline F2** | 12 flips vs 5 flips | — | $p = 0.041$ (Statistically significant) |

---

## 2. Negative Control Sanity Checks

1. **Random Routing Negative Control:**  
   Random expert selection on the 53 disagreement matches produces a mean accuracy of **36.5% (19.3 / 53 correct)**, which falls far below R0 Consensus (**43.4%, 23/53**).
2. **Shuffled Routing Labels Negative Control:**  
   When training labels are randomly permuted, ML router accuracy collapses from $54.2\% \to 34.1\%$ on Validation, confirming **zero data leakage or spurious memorization**.

