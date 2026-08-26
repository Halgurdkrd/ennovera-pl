# ENNOVERA PL — M3 Mixture-of-Experts Match-by-Match Winner Prediction Flips Report

**Research Focus:** Transparent Ledger of Argmax 1X2 Prediction Shifts Across the 2025–26 Holdout Season (380 Matches).

---

## 1. Candidate Decision Flip Ledger vs Baseline F2 (184 / 380 Correct)

| Candidate Model Architecture | Total Argmax Flips | Wrong $\to$ Correct Flips | Correct $\to$ Wrong Flips | **Net Winner Gain vs F2** | **Total Holdout Correct Matches** | **Holdout Accuracy (%)** |
|---|---|---|---|---|---|---|
| **Candidate F2 (Baseline)** | 0 matches | 0 matches | 0 matches | **0 matches** | **184 / 380** | **48.42%** |
| **M3-A: Equal Expert Blend** | 9 matches | 3 matches | 2 matches | **+1 match** | **185 / 380** | **48.68%** |
| **M3-C: Rule-Based Gate** | 11 matches | 4 matches | 3 matches | **+1 match** | **185 / 380** | **48.68%** |
| **M3-D: Softmax Gating Network**| 10 matches | 5 matches | 1 match | **+4 matches** | **188 / 380** | **49.47%** |
| **M3-G: Best Hybrid MoE** | 10 matches | 5 matches | 1 match | **+4 matches** | **188 / 380** | **49.47%** |
| **M3-E: Shallow Tree Gate** | 14 matches | 7 matches | 2 matches | **+5 matches** | **189 / 380** | **49.74% (Peak)** |

---

## 2. Match-Level Transition Case Studies:
1. **Wrong $\to$ Correct Transition (M3 Routing):**  
   - *Nottingham Forest 1–0 Liverpool (GW23):* The routing gate detected an extreme low-block counter matchup, routing weight heavily to Expert 4 (Tactical T7) and Expert 2 (PQ Talent), correctly flipping the prediction to a Forest victory.
2. **Correct $\to$ Wrong Transition (Stochastic Draw Variance):**  
   - *Tottenham 1–2 Newcastle (GW15):* High home offensive pressure favored Spurs in probability, flipping an away upset call.

