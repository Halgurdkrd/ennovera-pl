# ENNOVERA PHASE 4.1 — PL MODEL METRIC CORRECTION

## Comprehensive PL Match Performance Matrix (1,520 Matches, 2022–2026)
| Metric | CORE_BASE (Raw Elo) | V2 Model | V5.1 Expected XI Model | Category Winner |
|---|---|---|---|---|
| **Accuracy** | 52.24% (794/1520) | **52.83% (803/1520)** | **52.83% (803/1520)** | **Tied: V2 & V5.1** |
| **Log Loss** | **0.99053** | 1.00514 | 0.99829 | **CORE_BASE** |
| **Brier Score** | **0.59123** | 0.60023 | 0.59594 | **CORE_BASE** |
| **ECE Calibration** | 0.0212 | **0.0066** | 0.0076 | **V2 (V5.1 Close 2nd)** |

### Metric Language Correction
The previous claim that "V5.1 is best by match metrics" is corrected to:
- **Best Raw Log Loss & Brier:** CORE_BASE (Raw Elo).
- **Best Accuracy & Calibration:** V5.1 & V2.
- **Best Downstream FPL Source:** **V5.1 Expected XI Model** (delivering +17.75 pts/yr manager gain vs +8.25 for CORE_BASE).
