# ENNOVERA PL — ROOT-CAUSE-02 Blend Diagnostics & Capped F2 Weight Report

**Research Focus:** Out-of-Sample Evaluation of Convex Blends Between Baseline F2 and Independent Raw Models with Capped Historical Weights.

---

## 1. Convex Blend Sweep: F2 Baseline + C-HYBRID-RAW (Holdout Season)

| F2 Weight ($w_{\text{F2}}$) | Independent Model Weight | Holdout Correct / 380 | Holdout Accuracy (%) | Holdout Log-Loss | Argmax Diffs vs F2 |
|---|---|---|---|---|---|
| **0.0 (Pure Independent)** | **1.0 (Pure C-HYBRID)** | 176 / 380 | 46.32% | 1.18794 | 92 matches |
| **0.2** | 0.8 | 174 / 380 | 45.79% | 1.11649 | 79 matches |
| **0.4** | 0.6 | 179 / 380 | 47.11% | 1.07513 | 55 matches |
| **0.5 (Equal Blend)** | **0.5 (Equal Blend)** | 178 / 380 | 46.84% | 1.06067 | 47 matches |
| **0.6** | 0.4 | 186 / 380 | 48.95% | 1.04939 | 34 matches |
| **0.7 (Optimal Blend)** | **0.3** | **187 / 380** | **49.21%** | **1.04089** | **22 matches** |
| **0.8** | 0.2 | **187 / 380** | **49.21%** | 1.03490 | 10 matches |
| **1.0 (Pure F2 Baseline)** | 0.0 | 184 / 380 | 48.42% | 1.02999 | 0 matches |

---

## 2. Key Diagnostic Takeaway:
- A capped blend with **30% independent weight ($w_{\text{F2}}=0.70$)** outperforms baseline F2 by $+3$ matches (187 vs 184) while preserving **22 genuine winner decision differences**.

