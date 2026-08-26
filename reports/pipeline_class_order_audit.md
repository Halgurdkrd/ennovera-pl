# ENNOVERA PL — M3-VERIFY-02 Class Order Integrity Audit Report

**Audit Focus:** Forensic Verification of Internal Class Mapping, Probability Array Slices, and Argmax Conversions Across All Pipelines.

---

## 1. Class Order Verification Matrix

| Model Architecture | Training Label Mapping | `model.classes_` | Probability Output Vector | Argmax Conversion | Evaluation Matrix Mapping | Audit Status |
|---|---|---|---|---|---|---|
| **Candidate F2** | `0=Home, 1=Draw, 2=Away` | `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |
| **Candidate M1-D** | `0=Home, 1=Draw, 2=Away` | `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |
| **Candidate PQ7** | `0=Home, 1=Draw, 2=Away` | `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |
| **Availability Expert**| `0=Home, 1=Draw, 2=Away`| `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |
| **Tactical T7** | `0=Home, 1=Draw, 2=Away` | `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |
| **Context D7** | `0=Home, 1=Draw, 2=Away` | `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |
| **M3-E / M3-G / R7** | `0=Home, 1=Draw, 2=Away` | `[0, 1, 2]` | `[P_H, P_D, P_A]` | `argmax() in [0, 1, 2]` | `0=Home, 1=Draw, 2=Away` | **100% CONSISTENT** |

---

## 2. Definitive Verification Assertion:
- **Zero Class Mismatches:** Every model, evaluation script, and metric helper strictly adheres to the standard `0=Home Win, 1=Draw, 2=Away Win` indexing.
- Saved table: [`data/experiments/pipeline_integrity/class_order_audit.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/experiments/pipeline_integrity/class_order_audit.csv).

