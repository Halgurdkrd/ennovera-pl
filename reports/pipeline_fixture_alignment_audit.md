# ENNOVERA PL — M3-VERIFY-02 Fixture Alignment & Data Integrity Audit Report

**Audit Focus:** Verification of Universe Consistency, Fixture Key Uniqueness, and Outcome Label Integrity.

---

## 1. Fixture Universe Accounting

| Data Split | Season(s) | Expected Fixtures | Actual Verified Unique Fixtures | Duplicate Count | Missing Ground-Truth Labels |
|---|---|---|---|---|---|
| **Development** | 2022–23 & 2023–24 | 760 matches | **760 matches** | **0** | **0** |
| **Validation** | 2024–25 | 380 matches | **380 matches** | **0** | **0** |
| **Holdout (Research Test)**| 2025–26 | 380 matches | **380 matches** | **0** | **0** |
| **TOTAL UNIVERSE** | **4 Complete Seasons** | **1,520 matches** | **1,520 matches** | **0** | **0** |

---

## 2. 2025–26 Holdout Season Empirical Class Distribution

| Match Outcome Class | Verified Match Count ($N$) | Empirical Class Probability |
|---|---|---|
| **Home Win (`class = 0`)** | **162 matches** | **42.63%** |
| **Draw (`class = 1`)** | **104 matches** | **27.37%** |
| **Away Win (`class = 2`)** | **114 matches** | **30.00%** |
| **TOTAL HOLDOUT MATCHES** | **380 matches** | **100.00%** |

---

## 3. Verification Finding:
- Exactly 380 unique fixtures exist with zero row index corruption, zero duplicate merges, and 100% complete ground-truth labels.
- Saved table: [`data/experiments/pipeline_integrity/fixture_alignment_audit.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/experiments/pipeline_integrity/fixture_alignment_audit.csv).

