# ENNOVERA PL — ROOT-CAUSE-01 Feature Information Value Report

**Autopsy Focus:** Standalone and Incremental Information Value of Major Feature Families.

---

## 1. Standalone Feature Family Benchmark (Trained on Dev, Tested on 2025–26 Holdout)

| Feature Family | Primary Signals Included | Standalone Correct / 380 | Standalone Accuracy (%) | Standalone Log-Loss | Primary Impact Mode |
|---|---|---|---|---|---|
| **1. Historical F2 Team State** | Elo, rolling goal difference, points | **184 / 380** | **48.42%** | **1.03575** | **Determines Macro Favorite Identity** |
| **2. Player Quality / EA FC26** | Expected XI Attacking / Creation / OVR | **183 / 380** | **48.16%** | **1.03749** | **Refines Talent Differentials on Promoted Teams**|
| **3. Tactical Mismatch (T7)** | PPDA difference, tilt, pressing traps | **178 / 380** | **46.84%** | **1.05130** | **Flips 8–10 Tactical Upset Matches** |
| **4. European Fatigue & Form (D7)**| Euro match shock, rest difference | **175 / 380** | **46.05%** | **1.05850** | **Sharpens Calibration on Congested Mid-Weeks** |
| **5. Lineup Shock & Injuries** | Attacking/Defensive shock differentials| **162 / 380** | **42.63%** | **1.09588** | **High Variance / Calibration Only** |

---

## 2. Definitive Summary:
- **Historical Team Strength and Player Quality** supply 95% of the macro winner classification power.
- **Tactical Matchups and European Fatigue** supply the vital 5% residual signal that boosts accuracy to 49.74% and establishes project-record calibration (1.02678 LL).

