# ENNOVERA PL + FPL — FPL-01-VERIFY Holdout Contamination & Classification Report

**Verification Focus:** Forensic Evaluation of Model Development History, Component Tuning Periods, and Formal Classification of the 2025–26 Season.

---

## 1. Component Provenance & Exposure Matrix

| Model Component | Training Period | Validation Period | Holdout Period | 2025–26 Inspected During Development? | Exposure Classification |
|---|---|---|---|---|---|
| **Expected Minutes Engine** | 2022–24 (Dev) | 2024–25 (Val) | 2025–26 | No direct parameter tuning | Clean |
| **xG / xA Attacking Rates** | 2022–24 (Dev) | 2024–25 (Val) | 2025–26 | No direct parameter tuning | Clean |
| **S2 Dixon-Coles Parameters**| 2022–24 (Dev) | 2024–25 (Val) | 2025–26 | Frozen from PL research | Clean |
| **C-PLAYER Quality Vectors** | Historical EA FC | 2024–25 (Val) | 2025–26 | Frozen attributes | Clean |
| **Integer Linear Optimizer** | None (Rule-Based)| 2024–25 (Val) | 2025–26 | Deterministic HiGHS solver | Clean |
| **Overall Season Environment** | — | — | 2025–26 | **Yes (in PL-01 to PL-04 audits)** | **Research-Exposed** |

---

## 2. Definitive Holdout Classification: H1

### **Classification: H1 — TEMPORALLY CLEAN BUT RESEARCH-EXPOSED**

- **Why Not H0 (Pristine)?** Because the engineering team and research trajectory have repeatedly evaluated and inspected 2025–26 match outcomes and player distributions in prior PL research (M1 through ROOT-CAUSE-04).
- **Why Not H2 / H3 (Contaminated / Leaked)?** Because no feature or model parameter was directly fitted using 2025–26 target labels or future timestamps.
- **Future Protocol:** For future FPL model development, 2025–26 must be treated as a research-exposed benchmark, with **2026–27 prospective locked predictions** serving as the ultimate out-of-sample test.

