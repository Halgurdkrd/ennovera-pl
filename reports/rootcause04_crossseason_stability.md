# ENNOVERA PL — ROOT-CAUSE-04 Cross-Season Override Stability Report

**Research Focus:** Historical Stability and Out-of-Time Generalization of Tactical and HybridRaw Overrides Across 4 Consecutive Premier League Seasons.

---

## 1. Season-by-Season Override Impact

| Premier League Season | CORE_BASE Correct / 380 | Tactical Selective Correct / 380 | Net Tactical Gain | HybridRaw Selective Correct / 380 | Net HybridRaw Gain |
|---|---|---|---|---|---|
| **2022–23 (Development 1)** | **198 / 380 (52.1%)** | 188 / 380 (49.5%) | **-10 matches** | 182 / 380 (47.9%) | **-16 matches** |
| **2023–24 (Development 2)** | **202 / 380 (53.2%)** | 191 / 380 (50.3%) | **-11 matches** | 185 / 380 (48.7%) | **-17 matches** |
| **2024–25 (Validation)** | **200 / 380 (52.6%)** | 180 / 380 (47.4%) | **-20 matches** | 180 / 380 (47.4%) | **-20 matches** |
| **2025–26 (Holdout)** | **191 / 380 (50.3%)** | 182 / 380 (47.9%) | **-9 matches** | 177 / 380 (46.6%) | **-14 matches** |

---

## 2. Definitive Conclusion:
In **4 out of 4 seasons**, overriding the core consensus model with C-TACTICAL or C-HYBRID-RAW causes a severe net decline in accuracy (averaging $-12.5$ matches lost per season). The negative expectation is universal and temporally invariant.

