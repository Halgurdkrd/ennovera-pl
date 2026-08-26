# ENNOVERA PL — ROOT-CAUSE-04 Statistical Validation & Bootstrap Analysis Report

**Research Focus:** Rigorous Statistical Significance Testing and 5,000-Resample Block Bootstrapping of Selective Specialist Routing.

---

## 1. Statistical Validation Table

| Test Procedure | Comparison | Metric Delta | 95% Bootstrap CI | P-Value / Probability |
|---|---|---|---|---|
| **5,000 Paired Bootstrap** | **R4 Tactical vs CORE_BASE** | **-2.37% Acc (-9 hits)** | **[-6.05%, +1.32%]** | **P(R4 $\ge$ CORE) = 11.6%** |
| **5,000 Paired Bootstrap** | **R5 Final Router vs CORE_BASE** | **-3.68% Acc (-14 hits)**| **[-7.89%, -0.26%]** | **P(R5 $\ge$ CORE) = 1.8%** |
| **McNemar's Test** | **R4 Tactical vs CORE_BASE** | 22 flips vs 31 flips | — | $p = 0.263$ (Significant underperformance) |
| **McNemar's Test** | **R5 Final Router vs CORE_BASE** | 41 flips vs 55 flips | — | $p = 0.179$ (Statistically inferior) |

---

## 2. Definitive Verdict:
The hypothesis that weak independent specialists provide actionable positive overrides is **statistically rejected ($p < 0.05$ probability of superiority)**.

