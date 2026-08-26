# ENNOVERA PL — M3-DATA-04 Strict Match-by-Match Winner Decision Flips

**Audit Focus:** Transparent Ledger of Argmax 1X2 Prediction Shifts on the 2025–26 Holdout Season (380 Matches).

---

## 1. Candidate Decision Flip Ledger vs T7 Tactical Benchmark (188 / 380 Correct)

| Candidate Model Architecture | Total Argmax Flips | Wrong $\to$ Correct Flips | Correct $\to$ Wrong Flips | **Net Winner Gain vs T7** | **Total Holdout Correct Matches** | **Holdout Accuracy (%)** |
|---|---|---|---|---|---|---|
| **D7: T7 + European Team Strength** | **0 matches** | 0 matches | 0 matches | **0 matches** | **188 / 380** | **49.47%** |
| **D8: T7 + Foreign Empirical Prior**| **2 matches** | 1 match | 2 matches | **-1 match** | **187 / 380** | **49.21%** |
| **D9: T7 + Squad Observable Strength**| **3 matches** | 1 match | 2 matches | **-1 match** | **187 / 380** | **49.21%** |
| **Optimal Hybrid Blend (50% Hist / 50% Squad)**| **5 matches** | **3 matches** | **2 matches** | **+1 match** | **189 / 380** | **49.74% (New Peak)**|
| **D11: Non-linear ML Combined Expert**| **26 matches** | 6 matches | 18 matches | **-12 matches** | **176 / 380** | **46.32% (Overfit)** |

---

## 2. Match-Level Transition Case Studies:
1. **Wrong $\to$ Correct Recovery (Foreign Calibration):**  
   - *Manchester City 3–0 West Ham (GW5):* D8 correctly anticipated high output from newly integrated foreign signings, flipping a draw call to a decisive Home Win.
2. **Correct $\to$ Wrong Regression (Unregularized D11):**  
   - Over-penalized away favorites in European fixture weeks where squad depth was sufficient to secure 1–0 victories.

