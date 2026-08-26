# ENNOVERA PL — ROOT-CAUSE-03 Selective Override Ledger & Analysis Report

**Research Focus:** Forensic Accounting of Selective Override Decisions Under R-SELECTIVE ($\tau = 0.080$).

---

## 1. Selective Override Ledger Summary (2025–26 Holdout Season)

| Override Category | Count ($N$) | Percentage of Overrides (%) | Net Impact on Season Correct Count |
|---|---|---|---|
| **Total Overrides Executed** | **135 matches** | 100.0% | — |
| **WRONG $\to$ CORRECT Flips** | **14 matches** | 10.37% | **+14 matches recovered** |
| **CORRECT $\to$ WRONG Flips** | **16 matches** | 11.85% | **-16 matches destroyed** |
| **WRONG $\to$ WRONG (Neutral)** | **105 matches** | 77.78% | 0 |
| **NET OVERRIDE IMPACT** | — | — | **-2 matches (187 vs 189)** |

---

## 2. Forensic Conclusion:
- While R-SELECTIVE recovers **14 genuine errors where M3 failed**, it inadvertently flips **16 fixtures where M3 was already correct**.
- To achieve a net positive gain ($+9$ matches $\to 52\%$), override rules must be restricted to higher confidence thresholds ($\tau \ge 0.15$) and strictly validated against the Competence Map (e.g. Promoted clubs and low-goal fixtures only).

