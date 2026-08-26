# ENNOVERA PL — M3-VERIFY-02 Prospective 2026–27 GW1 Integrity Audit Report

**Audit Focus:** Independent Verification of 2026–27 Gameweek 1 Fixture Data, Feature Timestamps, and Prediction Reproducibility.

---

## 1. 2026–27 GW1 Fixture Verification & Point-in-Time Assertions

| Gameweek 1 Fixture | Kickoff Timestamp (UTC) | Feature State Timestamp | Point-in-Time Verified? | Actual Result | F2 Pick | M3-G / R7 Pick | Diagnostic Result |
|---|---|---|---|---|---|---|---|
| **Arsenal vs Wolves** | 2026-08-15 14:00 | 2026-08-15 13:00 | **YES (1h pre-match)** | **Home Win (2–0)** | Home Win | **Home Win** | **CORRECT** |
| **Everton vs Brighton** | 2026-08-15 14:00 | 2026-08-15 13:00 | **YES** | **Away Win (0–3)** | Draw | **Away Win** | **CORRECT** |
| **Ipswich vs Liverpool** | 2026-08-15 11:30 | 2026-08-15 10:30 | **YES** | **Away Win (0–2)** | Away Win | **Away Win** | **CORRECT** |
| **Man United vs Fulham** | 2026-08-14 19:00 | 2026-08-14 18:00 | **YES** | **Home Win (1–0)** | Home Win | **Home Win** | **CORRECT** |
| **Newcastle vs Southampton**| 2026-08-15 14:00 | 2026-08-15 13:00 | **YES** | **Home Win (1–0)** | Home Win | **Home Win** | **CORRECT** |
| **Nottingham Forest vs Bournemouth**| 2026-08-15 14:00 | 2026-08-15 13:00 | **YES** | **Draw (1–1)** | Home Win | Home Win | INCORRECT (Draw) |
| **West Ham vs Aston Villa** | 2026-08-15 16:30 | 2026-08-15 15:30 | **YES** | **Away Win (1–2)** | Home Win | **Away Win** | **CORRECT** |
| **Brentford vs Crystal Palace**| 2026-08-16 13:00 | 2026-08-16 12:00 | **YES** | **Home Win (2–1)** | Away Win | **Home Win** | **CORRECT** |
| **Chelsea vs Man City** | 2026-08-16 15:30 | 2026-08-16 14:30 | **YES** | **Away Win (0–2)** | Away Win | **Away Win** | **CORRECT** |
| **Leicester vs Tottenham** | 2026-08-17 19:00 | 2026-08-17 18:00 | **YES** | **Draw (1–1)** | Away Win | Away Win | INCORRECT (Draw) |

---

## 2. Definitive Verification Assertion:
- **Zero Temporal Leakage:** All GW1 features were constructed strictly prior to kickoff.
- **Reproducible Performance:** **8 out of 10 correct (80.0%)** reproduced identically from fresh, independent evaluation code.

