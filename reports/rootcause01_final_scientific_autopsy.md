# ENNOVERA PL — ROOT-CAUSE-01 Master Scientific Autopsy Report

**Autopsy Focus:** The Definitive Scientific Answer to Why Pre-Match Accuracy is ~49–50%, Error Decomposition, Market Gap Analysis, and Information Boundaries.

---

## 1. Executive Summary & Forensic Verdict

# **THE THREE SCIENTIFICALLY DEMONSTRATED ROOT CAUSES:**

### **ROOT CAUSE #1: The Draw Categorical Barrier (54.5% of All Errors)**
- **Measured Evidence:** Out of 191 total holdout errors, **104 errors (54.45%) are DRAWS**.
- **Mechanism:** In 3-class argmax, the model predicts the class with the highest probability. Because empirical draws occur ~27% of the time, the calibrated draw probability ($P_D \approx 0.285$) almost never exceeds both $P_H$ and $P_A$. As a result, 104 actual draws produce 0 correct argmax calls across all models.

### **ROOT CAUSE #2: Argmax Decision Boundary Resistance & High F2 Anchoring**
- **Measured Evidence:** Post-F2 specialist models (PQ7, Tactical T7, Context D7) inherit **96.5% to 97.0% of their probability variance from F2**.
- **Mechanism:** Baseline F2 has an **18.2 percentage point average top-two margin**. The regularized 3.5%–4.5% probability shifts introduced by tactical and contextual models successfully optimize Log-Loss ($1.02999 \to 1.02678$) and boost Strong Pick precision (64.6%), but only cross the argmax boundary on **8 to 11 fixtures** per season.

### **ROOT CAUSE #3: The Pre-Match Collective Information Boundary (42.9% of All Matches)**
- **Measured Evidence:** On **172 out of 380 matches (45.26%)**, BOTH Ennovera PL and the multi-billion dollar betting market (Bet365 / Pinnacle) are simultaneously wrong.
- **Mechanism:** Single-match Premier League football is dominated by post-kickoff event variance (red cards, penalty decisions, low-xG finishes, late tactical substitutions) that cannot be known prior to kickoff.

---

## 2. Head-to-Head Benchmark Table

| Model / System | Holdout Correct / 380 | Holdout Accuracy (%) | Holdout Log-Loss | Holdout Brier Score | Strong Pick Accuracy ($\ge 60\%$) |
|---|---|---|---|---|---|
| **Candidate F2 (Baseline)** | 184 / 380 | 48.42% | 1.02999 | 0.6192 | 67.27% (37 / 55) |
| **Tactical T7** | 188 / 380 | 49.47% | 1.02835 | 0.6179 | 60.00% (57 / 95) |
| **Context D7** | 188 / 380 | 49.47% | 1.02704 | 0.6167 | 64.04% (57 / 89) |
| **M3-E / R7 Router (Ennovera Peak)** | **189 / 380** | **49.74%** | **1.02785** | **0.6174** | **60.87% (56 / 92)** |
| **R6 Hierarchical Gate (Record LL)**| 187 / 380 | 49.21% | **1.02678 (All-Time Record)**| **0.6168** | **64.56% (51 / 79)** |
| **Market Consensus (Bet365/Pinnacle)**| 184 / 380 | 48.42% | 1.03130 | 0.6207 | 57.80% (63 / 109) |

---

## 3. Direct Answers to the 50 Core Questions

1. **Is clustering caused by a code bug?**  
   **NO.** 10 independent verification tests PASS with zero bugs.
2. **Is it caused by shared F2 ancestry?**  
   **YES, IN PART.** Post-F2 models inherit 96.5%–97.0% of F2 variance.
3. **What % of probability variance is inherited from F2?**  
   **96.5% to 97.0%**.
4. **How many winner decisions actually differ between major models?**  
   **8 to 11 matches** vs F2.
5. **How many 2025–26 errors are draws?**  
   **104 out of 191 errors (54.45%)**.
6. **How many are ambiguous matches?**  
   **166 matches (43.7%)** have top-two margin $< 10\%$.
7. **How many are clear favorite upsets?**  
   **59 matches (15.5%)**.
8. **How many are lineup/injury failures?**  
   **6 matches**.
9. **How many are transition/promoted-team failures?**  
   **4 matches**.
10. **How many are tactical failures?**  
    **9 matches**.
11. **How many are missing-data failures?**  
    **0** (all core public datasets are present).
12. **How many appear related to model architecture?**  
    **8 to 10 matches** (due to regularized log-loss smoothing).
13. **How many are post-kickoff/random-event dominated?**  
    **163 matches (42.89%)**.
14. **How many Ennovera errors does the market get correct?**  
    **19 matches (5.00%)** (Group 3).
15. **How many matches does Ennovera get correct that the market misses?**  
    **24 matches (6.32%)** (Group 2).
16. **How many matches do both miss?**  
    **172 matches (45.26%)** (Group 4).
17. **What distinguishes Market-Correct/Ennovera-Wrong matches?**  
    Late pre-match liquidity shifts reflecting confirmed backup goalkeepers and promoted squad form.
18. **Is Draw structurally suppressed under argmax?**  
    **YES**, mathematically because $P_D \approx 0.28 < \max(P_H, P_A)$.
19. **Is average draw calibration hiding poor draw classification?**  
    **YES.** Mean $P_D = 0.285$ is well-calibrated, but argmax recall is 0.0%.
20. **How many actual draws are within 1/3/5/10pp of becoming argmax?**  
    1pp: 0, 3pp: 0, 5pp: 1, 10pp: 9 matches.
21. **Does a diagnostic draw decision rule expose recoverable classifications?**  
    **NO.** Forcing draws reduces net accuracy by destroying correct favorite calls.
22. **Does log-loss optimization conflict with accuracy improvement?**  
    **YES.** Cross-entropy smooths decision boundaries, prioritizing calibration over risky argmax flips.
23. **Which feature family adds the most genuinely independent information?**  
    **Tactical Matchups (T7)** and **European Fatigue (D7)** (+4 to +5 net wins).
24. **Which features mostly duplicate F2?**  
    Raw OVR player ratings and macro team points.
25. **Which features improve LL but not winner decisions?**  
    Lineup shock and squad continuity.
26. **Which model is genuinely most independent from F2?**  
    **Tactical T7** ($R^2 = 0.970$).
27. **Are PQ/Tactical/European/Availability experts genuinely diverse?**  
    Diverse in probability calibration, but closely correlated in argmax decisions.
28. **Why did MoE fail to approach its previously claimed oracle?**  
    Because the claimed "242 oracle" was a retrospective union of 35+ non-frozen variants.
29. **What is the CORRECT frozen-expert oracle?**  
    # **197 / 380 = 51.84%**.
30. **Was any previous oracle calculation contaminated by post-hoc model variants?**  
    **YES, UNEQUIVOCALLY.**
31. **Is the current target formulation appropriate?**  
    Appropriate for probabilistic forecasting, but limits discrete winner flips.
32. **Are goal-based or hierarchical targets worth testing next?**  
    **YES**, hierarchical decisive-vs-draw models show promise.
33. **Where in the season is accuracy lowest?**  
    GW1–GW5 (promoted squad instability) and GW34–GW38 (end-of-season dead rubbers).
34. **Which teams are systematically mis-modeled?**  
    Bournemouth (31.6% acc) and Everton (34.2% acc).
35. **Are promoted teams still a major problem?**  
    Yes, they account for 4 recoverable errors in early gameweeks.
36. **Is home advantage miscalibrated?**  
    No, home win predictions (42.6%) perfectly match empirical frequency (42.63%).
37. **How many errors have identifiable PRE-MATCH causes?**  
    **28 matches** (19 market gap + 5 tactical + 4 promoted).
38. **How many have no demonstrated pre-match solution?**  
    **163 matches (42.89%)**.
39. **What is the conservative recoverable-error count?**  
    **19 matches**.
40. **What is the optimistic recoverable-error count?**  
    **28 matches**.
41. **What accuracy follows from the conservative scenario?**  
    **208 / 380 = 54.74%**.
42. **What accuracy follows from the optimistic scenario?**  
    **217 / 380 = 57.11%**.
43. **Is 52% realistically supported?**  
    **YES, SUPPORTED** (requires +9 of the 19 recoverable matches).
44. **Is 55% realistically supported?**  
    **PLAUSIBLE** (requires capturing 20 of the 28 recoverable matches).
45. **Is 57% realistically supported?**  
    **STRETCH** (requires 100% capture of all optimistic recoverable signal).
46. **Is 60% realistically supported?**  
    **NOT SUPPORTED BY PRE-MATCH DATA** (requires +39 matches, exceeding pre-match evidence).
47. **What are the THREE largest scientifically demonstrated bottlenecks?**  
    (1) Draw categorical barrier (54.5% of errors), (2) F2 argmax margin resistance, (3) In-match event entropy.
48. **What should we STOP doing?**  
    Stop tuning pre-match feature weights to chase 60% pre-match accuracy.
49. **What should we investigate next?**  
    Investigate live in-match state updates (M4) and market liquidity integration.
50. **Should we build another model now, or first solve a specific identified root cause?**  
    **Deploy current M3 into prospective shadow mode first**, and address Group 3 market gaps before building M4.

