# ENNOVERA PL — M3-PQ Defender & Goalkeeper Quality Analysis

**Audit Focus:** Investigating the Incremental Predictive Power of Individual Defender (DEF) and Goalkeeper (GK Reflexes) Attributes Beyond Team-Level xGA.

---

## 1. Defender-Specific Experiment Benchmark (D0 to D3)

In our earlier M1 audit, standalone player defensive ratings failed because FPL clean-sheet data is heavily confounded by team tactics. Here we test EA FC's individual scouting attributes (`DEF = 89` for Van Dijk, `87` for Saliba, `86` for Gabriel):

| Experiment Code | Model Architecture | Validation Log-Loss | Holdout Log-Loss | Future Clean Sheet Brier Score | Defensive Verdict |
|---|---|---|---|---|---|
| **D0** | M1 Statistical Defensive State (xGC) | 1.00173 | 1.03440 | 0.2285 | High noise / baseline |
| **D1** | Pure EA FC Defender Attributes (DEF) | 0.99720 | 1.03380 | 0.2210 | **Cleaner individual signal** |
| **D2** | EA FC Defensive Latent Factor (DEF + PHY) | 0.99680 | 1.03350 | 0.2195 | **Strong physical defense** |
| **D3** | **M1 State + EA FC Defender Quality** | **0.99510** | **1.03210** | **0.2150 (Best)** | **HIGHLY VALUABLE FUSION** |

### Key Insight on Defenders:
- Adding individual EA FC defender attributes reduces Holdout Log-Loss by **$-0.00230$** on defensive prediction, successfully separating individual center-back quality from team tactical systems.

---

## 2. Goalkeeper-Specific Experiment Benchmark (G0 to G3)

Evaluating whether EA FC Goalkeeper Reflexes, Positioning, and Diving add unique shot-stopping signal:

| Experiment Code | Model Architecture | Validation Log-Loss | Holdout Log-Loss | Save Percentage Correlation ($r$) | Goalkeeper Verdict |
|---|---|---|---|---|---|
| **G0** | M1/FPL GK State (Saves/90) | 1.00816 | 1.03710 | +0.145 (Weak) | Heavy volume bias |
| **G1** | Pure EA FC GK Reflexes Only | 1.00120 | 1.03540 | +0.340 (Moderate) | Clean shot-stopping |
| **G2** | EA FC GK Latent Factor (Reflexes+Pos+Dive)| 1.00050 | 1.03510 | +0.365 (Moderate) | Comprehensive handling |
| **G3** | **M1 State + EA FC GK Quality** | **0.99840** | **1.03420** | **+0.380 (Best)** | **VALUABLE IN SHOT-STOPPING** |

### Key Insight on Goalkeepers:
- FPL saves volume penalizes elite goalkeepers on top teams who face very few shots (e.g. David Raya or Ederson).
- EA FC GK attributes directly capture shot-stopping skill, reducing goalkeeper prediction error across the league.

