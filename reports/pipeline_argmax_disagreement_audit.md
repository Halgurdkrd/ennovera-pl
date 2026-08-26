# ENNOVERA PL — M3-VERIFY-02 Pairwise Argmax Disagreement & Resistance Audit Report

**Audit Focus:** Deconstruction of the Pairwise Argmax Disagreement Matrix and Mathematical Analysis of Argmax Decision Boundary Resistance.

---

## 1. Authoritative Pairwise Argmax Disagreement Matrix (2025–26 Holdout Season, N=380)

*Values indicate the exact number of fixtures (out of 380) where the two models predict different 1X2 argmax winner classes.*

| Model Name | F2 | M1-D | PQ7 | Availability | Tactical T7 | Context D7 | DATA-04 Hyb | M3-E | M3-G | R6 Gate | R7 Router |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Candidate F2** | **0** | 3 | 10 | 27 | 10 | 10 | 8 | 10 | 9 | 8 | 11 |
| **Candidate M1-D** | 3 | **0** | 7 | 30 | 9 | 9 | 7 | 9 | 8 | 7 | 10 |
| **Candidate PQ7** | 10 | 7 | **0** | 37 | 8 | 8 | 6 | 8 | 7 | 6 | 9 |
| **Availability Expert**| 27 | 30 | 37 | **0** | 33 | 35 | 33 | 35 | 34 | 33 | 34 |
| **Tactical T7** | 10 | 9 | 8 | 33 | **0** | 6 | 2 | 2 | 1 | 2 | 1 |
| **Context D7** | 10 | 9 | 8 | 35 | 6 | **0** | 4 | 4 | 5 | 4 | 5 |
| **DATA-04 Hybrid** | 8 | 7 | 6 | 33 | 2 | 4 | **0** | 2 | 1 | 0 | 3 |
| **M3-E Router** | 10 | 9 | 8 | 35 | 2 | 4 | 2 | **0** | 1 | 2 | 1 |
| **M3-G Hybrid MoE** | 9 | 8 | 7 | 34 | 1 | 5 | 1 | 1 | **0** | 1 | 2 |
| **R6 Hierarchical** | 8 | 7 | 6 | 33 | 2 | 4 | 0 | 2 | 1 | **0** | 3 |
| **R7 Tree Router** | 11 | 10 | 9 | 34 | 1 | 5 | 3 | 1 | 2 | 3 | **0** |

---

## 2. Argmax Decision Boundary Resistance: Why Models Cluster at 48%–50%

| Probability Metric | Candidate F2 Baseline | Tactical T7 | Context D7 | M3-E / R7 Router |
|---|---|---|---|---|
| **Mean Margin Between Top 2 Classes** | **0.182 (18.2 percentage points)** | 0.178 | 0.176 | 0.175 |
| **Mean Maximum Delta $\Delta P$ vs F2** | **0.000 (Reference)** | **0.0454 (4.54 pp)** | **0.0376 (3.76 pp)** | **0.0414 (4.14 pp)** |
| **Fixtures where $\Delta P > \text{Margin}$**| **0** | **38 matches** | **29 matches** | **35 matches** |
| **Actual Argmax Winner Decision Flips** | **0** | **10 matches** | **10 matches** | **11 matches** |
| **Argmax Resistance Rate (%)** | **N/A** | **73.7%** | **65.5%** | **68.6%** |

---

## 3. Mathematical Conclusion:
- The fundamental reason accuracy clusters between 48.4% and 49.7% is that **F2's top-two probability margin (18.2 pp) resists the 3.5–4.5 pp corrections** introduced by tactical and contextual models on over 90% of fixtures.
- Only **8 to 11 fixtures** per season have small enough margins for tactical signals to cross the argmax boundary, yielding the observed $+4$ to $+5$ net winner improvement.

