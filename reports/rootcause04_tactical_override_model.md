# ENNOVERA PL — ROOT-CAUSE-04 Tactical Override Model Tournament Report

**Research Focus:** Out-of-Sample Evaluation of Candidate Override Architectures (T0 Never Override, T1 Logistic, T2 Decision Tree, T4 HistGradientBoosting).

---

## 1. Tactical Override Model Leaderboard (2025–26 Holdout Season)

| Model Architecture | Validation Score | Holdout Correct / 380 | Holdout Acc (%) | Overrides Executed | Wrong $\to$ Correct | Correct $\to$ Wrong | Net Gain vs Core |
|---|---|---|---|---|---|---|---|
| **T0: Never Override (CORE_BASE)**| **200 / 380 (52.63%)** | **191 / 380** | **50.26%** | **0** | **0** | **0** | **0 (Reference)** |
| **T1: Regularized Logistic** | 180 / 380 (47.37%) | 182 / 380 | 47.89% | 75 | 22 | 31 | **-9 matches** |
| **T2: Shallow Decision Tree** | 180 / 380 (47.37%) | 182 / 380 | 47.89% | 75 | 22 | 31 | **-9 matches** |
| **T4: HistGradientBoosting** | 180 / 380 (47.37%) | 182 / 380 | 47.89% | 75 | 22 | 31 | **-9 matches** |

---

## 2. Definitive Conclusion:
Across all mathematical paradigms (linear, tree-based, boosting), overriding CORE_BASE with C-TACTICAL reduces overall accuracy by **$-9$ matches on Holdout and $-20$ matches on Validation**. The mathematically optimal tactical override strategy is **T0: NEVER OVERRIDE**.

