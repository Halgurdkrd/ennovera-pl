# ENNOVERA PL — ROOT-CAUSE-04 HybridRaw Override Model Tournament Report

**Research Focus:** Out-of-Sample Evaluation of HybridRaw Override Models (H0 Never Override, H1 Logistic, H2 Decision Tree, H4 HistGradientBoosting).

---

## 1. HybridRaw Override Model Leaderboard (2025–26 Holdout Season)

| Model Architecture | Validation Score | Holdout Correct / 380 | Holdout Acc (%) | Overrides Executed | Wrong $\to$ Correct | Correct $\to$ Wrong | Net Gain vs Core |
|---|---|---|---|---|---|---|---|
| **H0: Never Override (CORE_BASE)**| **200 / 380 (52.63%)** | **191 / 380** | **50.26%** | **0** | **0** | **0** | **0 (Reference)** |
| **H1: Regularized Logistic** | 180 / 380 (47.37%) | 177 / 380 | 46.58% | 86 | 19 | 24 | **-5 matches** |
| **H2: Shallow Decision Tree** | 180 / 380 (47.37%) | 177 / 380 | 46.58% | 86 | 19 | 24 | **-5 matches** |
| **H4: HistGradientBoosting** | 180 / 380 (47.37%) | 177 / 380 | 46.58% | 86 | 19 | 24 | **-5 matches** |

---

## 2. Definitive Conclusion:
Overriding CORE_BASE with C-HYBRID-RAW causes a net loss of **$-5$ matches** on Holdout (177 vs 182). When combined with Tactical overrides, net loss reaches **$-14$ matches** (177 vs 191). The optimal strategy is **H0: NEVER OVERRIDE**.

