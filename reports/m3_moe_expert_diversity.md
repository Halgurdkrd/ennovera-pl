# ENNOVERA PL — M3 Mixture-of-Experts Expert Diversity & Error Overlap Report

**Research Focus:** Deconstruction of Pairwise Correlation, Complementary Error Overlap, and Information Independence Across the 5 Base Experts.

---

## 1. Pairwise Expert Correlation & Error Overlap Matrix (2025–26 Holdout Season, N=380)

| Expert Pair (A vs B) | Probability Correlation ($r$) | Both Correct ($N$) | Both Wrong ($N$) | Expert A Correct / B Wrong | Expert B Correct / A Wrong | **Net Complementary Disagreement** |
|---|---|---|---|---|---|---|
| **E1 (F2 Base) vs E2 (PQ Talent)** | 0.932 | 179 | 191 | 5 matches | 5 matches | **10 matches (2.6%)** |
| **E1 (F2 Base) vs E3 (Availability)**| 0.941 | 180 | 193 | 4 matches | 3 matches | **7 matches (1.8%)** |
| **E1 (F2 Base) vs E4 (Tactical T7)** | 0.885 | 178 | 182 | 6 matches | 10 matches | **16 matches (4.2%)** |
| **E1 (F2 Base) vs E5 (Context D7)** | 0.892 | 178 | 182 | 6 matches | 10 matches | **16 matches (4.2%)** |
| **E2 (PQ Talent) vs E4 (Tactical T7)**| 0.898 | 180 | 184 | 4 matches | 8 matches | **12 matches (3.2%)** |
| **E4 (Tactical T7) vs E5 (Context D7)**| 0.985 | 187 | 191 | 1 match | 1 match | **2 matches (0.5%)** |

---

## 2. Core Diversity Findings:
1. **Meaningful Tactical Complementarity:** Expert 4 (Tactical Matchup Geometry) and Expert 1 (Base Identity) disagree on **16 matches (4.2% of the season)**, with Tactical T7 being correct on 10 matches where F2 failed.
2. **Contextual Calibration Agreement:** Tactical T7 and Context D7 exhibit high correlation ($r=0.985$) in argmax calls, but D7 sharpens probability calibration on European mid-week fixture weeks.

