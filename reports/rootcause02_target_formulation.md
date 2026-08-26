# ENNOVERA PL — ROOT-CAUSE-02 Target Formulation & Architecture Comparison Report

**Research Focus:** Comparative Analysis of Direct Multiclass Classification vs Score-Generation Poisson Grids vs Hierarchical Decisive-vs-Draw Decomposition.

---

## 1. Multi-Paradigm Architecture Comparison (2025–26 Holdout Season)

| Target Formulation Paradigm | Exemplar Candidate Architecture | Holdout Correct / 380 | Holdout Accuracy (%) | Holdout Log-Loss | Draw Recall (%) | Decisive Match Accuracy (%) | Structural Strengths & Weaknesses |
|---|---|---|---|---|---|---|---|
| **Direct Multiclass Logistic (Log-Loss)** | **C-PLAYER** | **186 / 380** | **48.95%** | **1.04607** | **0.0%** | **67.4%** | **Optimal calibration, smooth probabilities, zero Draw argmax** |
| **Score-Generation Poisson Grid (S2)** | **S2 Dixon-Coles** | **187 / 380** | **49.21%** | **1.04244** | **0.0%** | **67.8%** | **Direct goal expectancies ($\lambda_H, \lambda_A$), highly interpretable, 39 winner diffs** |
| **Hierarchical Decisive-vs-Draw (HIER)** | **HIER-DRAW** | **183 / 380** | **48.16%** | **1.04948** | **0.0%** | **66.3%** | **Decouples Draw parity from Home/Away direction, stable** |
| **Direct Non-Linear Tree (Categorical)** | **C-HYBRID-RAW** | **176 / 380** | **46.32%** | **1.18794** | **13.5%** | **58.7%** | **Recovers 14 draws, but suffers higher false-draw penalties** |

---

## 2. Definitive Conclusion on Target Formulation:
- **Score modeling (S2 Dixon-Coles)** matches or outperforms direct classification (**49.21% accuracy, 187/380**), while providing genuine structural diversity (39 differing winner calls vs F2).
- It provides a viable, mathematically grounded foundation for future multi-task goal modeling.

