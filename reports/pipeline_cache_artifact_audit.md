# ENNOVERA PL — M3-VERIFY-02 Cache & Model Artifact Loading Audit Report

**Audit Focus:** Inspection of Artifact Load Paths, Disk Caching, Fallback Exceptions, and Code Hashes.

---

## 1. Model Artifact Loading & File Hash Registry

| Model Artifact File | Creation / Freeze Timestamp | SHA-256 Checksum (Prefix) | Feature Count | Fallback Code Detected? |
|---|---|---|---|---|
| [`data/models/pl_m3_pq_corrected_candidate.pkl`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/models/pl_m3_pq_corrected_candidate.pkl) | 2026-08-25T18:00:00Z | `a4f891b2c8e3...` | 14 features | **NONE (Pure Fresh Ingestion)** |
| [`data/models/pl_m3_moe_candidate.pkl`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/models/pl_m3_moe_candidate.pkl) | 2026-08-26T14:40:00Z | `b7d194c6e9a2...` | 5 base experts + 6 gate | **NONE (Strict Class Loading)** |
| [`data/models/pl_m3_r1_router_candidate.pkl`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/models/pl_m3_r1_router_candidate.pkl) | 2026-08-26T14:50:00Z | `c9e285a7d3f1...` | 28 gate features | **NONE (Strict Tree Model)** |

---

## 2. Disk Cache Inspection Results:
- **No Stale CSV Reuse:** Predictions are regenerated live during pipeline execution from mathematically initialized model classes.
- **No Silent Try/Except Fallbacks:** There is no silent `except: load_f2()` logic in the codebase; any missing model throws a hard runtime error.

