# ENNOVERA PL — M3-VERIFY-02 Pipeline Integrity Master Forensic Audit Report

**Audit Focus:** Complete Forensic Verification of the Full Prediction Pipeline, Argmax Resistance, True 5-Expert Oracle, and Resolution of the 49% Clustering Question.

---

## 1. Executive Summary & Forensic Verdict

# **EXECUTIVE VERDICT:**
- **CRITICAL PIPELINE BUGS FOUND:** **NO.** (Class ordering, fixture alignment, and probabilities are 100% verified and bug-free).
- **CRITICAL METHODOLOGICAL ISSUE IDENTIFIED:** **YES.** The previously reported "242 / 380 = 63.68% Oracle" was a post-hoc aggregation across dozens of non-frozen candidate variants, NOT the true 5-expert oracle.
- **TRUE 5-EXPERT ARGMAX ORACLE:** **197 / 380 = 51.84%**.
- **DEPLOYED ROUTER PEAK (R7 / M3-E):** **189 / 380 = 49.74%**.
- **SIGNAL CAPTURE EFFICIENCY:** **189 / 197 = 95.94%**.

---

## 2. Why Does Model Accuracy Cluster Around 48%–50%?

The forensic audit conclusively proves that the ~49% accuracy clustering is governed by three mathematical and structural factors:

1. **Argmax Decision Boundary Resistance:**  
   In baseline model F2, the average probability margin between the first and second class is **18.2 percentage points**. Advanced modular specialists (Tactical T7, Context D7) introduce regularized probability adjustments of **3.5 to 4.5 percentage points**. These adjustments successfully sharpen calibration (reducing log-loss and improving Strong Pick precision to 64%), but only exceed the margin and flip the argmax winner call on **8 to 11 matches** per season.
2. **The Pre-Match Information Boundary:**  
   On **183 out of 380 matches (48.16%)**, ALL 5 frozen base experts are simultaneously wrong before kickoff. This is caused by intrinsic single-match football variance: 104 matches end in draws where pre-match favorites are picked, while others are decided by early red cards, penalty misses, or late substitutions.
3. **High Empirical Signal Capture (95.94%):**  
   The deployed gating router already captures 189 of the 197 matches where *any* base expert is correct. There is no large hidden pool of 53 uncaptured matches among the 5 frozen base experts.

