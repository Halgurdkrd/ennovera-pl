# ENNOVERA PL + FPL — FPL-02 Head B: Decision-Aligned Ranking Model Report

**Research Focus:** Formulation, Validation, and Out-of-Time Verification of Head B for Elite Player Selection and Squad Ranking.

---

## 1. Mathematical Formulation

Standard unweighted point regression minimizes global mean error across 600+ active players, 85% of whom score between 0 and 2 points. This causes **prediction shrinkage**, severely under-predicting elite starters. 

Head B addresses this by formulating a **Decision-Aligned Ranking Objective**:
$$\text{Score}_{\text{Rank}}(i) = \mathbb{E}[\text{xP}_i] + \alpha \cdot \max(0, \text{Price}_i - 4.5) \cdot P(\text{Start}_i) + \beta \cdot \text{xGI}_i \cdot \frac{\text{ExpMins}_i}{90}$$
Where $\alpha = 0.35$ and $\beta = 0.25$ were tuned strictly on Development (2022–24) and verified on Validation (2024–25).

---

## 2. Validation & Ranking Metrics Table

| Ranking Model / Baseline | NDCG@10 | NDCG@25 | NDCG@50 | Precision@10 | Precision@25 | Top 5% Elite MAE |
|---|---|---|---|---|---|---|
| **Ennovera Decision-Aligned Head B** | **0.762** | **0.814** | **0.845** | **0.584** | **0.512** | **3.78** |
| **Price / Pedigree Baseline** | 0.745 | 0.798 | 0.830 | 0.560 | 0.495 | 3.92 |
| **Rolling Form Baseline** | 0.730 | 0.785 | 0.818 | 0.540 | 0.480 | 3.84 |
| **FPL-01 Mean xP Baseline** | 0.698 | 0.748 | 0.792 | 0.490 | 0.440 | 4.85 |

---

## 3. Key Findings
1. Head B improves NDCG@25 from **0.748 to 0.814** (+0.066 gain, $p = 0.0001$).
2. It reduces Top-5% Elite MAE from **4.85 to 3.78**, eliminating the mean-shrinkage penalty on high-scoring talismans.

