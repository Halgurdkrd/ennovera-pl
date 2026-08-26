# ENNOVERA PL + FPL — JOINT RESEARCH PHASE 01 Data Inventory & Temporal Integrity Report

**Research Scope:** Deep Inventory of Historical FPL Data (2016–17 through 2025–26) and Verification of Point-in-Time Zero-Leakage Constraints.

---

## 1. Historical FPL Data Inventory

| Season Cohort | Data Path | Fixtures / GWs Available | Player Records | Field Completeness | Usability Status |
|---|---|---|---|---|---|
| **2016–17 to 2021–22** | `data/raw/fpl_full/data/{season}/` | 38 GWs per season | ~500–600 players/GW | Points, Goals, Assists, CS, Saves, Price, BPS | **Usable for Training / Secondary Validation** |
| **2022–23 (Dev 1)** | `data/raw/fpl_full/data/2022-23/` | 38 GWs (GW1–38) | 28,312 player-GW rows | Full xG, xA, xGI, xGC, ICT, Minutes, Starts | **Primary Historical Replay Benchmark** |
| **2023–24 (Dev 2)** | `data/raw/fpl_full/data/2023-24/` | 38 GWs (GW1–38) | 28,940 player-GW rows | Full xG, xA, xGI, xGC, ICT, Minutes, Starts | **Primary Historical Replay Benchmark** |
| **2024–25 (Validation)** | `data/raw/fpl_full/data/2024-25/` | 38 GWs (GW1–38) | 27,980 player-GW rows | Full xG, xA, xGI, xGC, ICT, Minutes, Starts | **Primary Validation Benchmark** |
| **2025–26 (Holdout)** | `data/raw/fpl_full/data/2025-26/` | 38 GWs (GW1–38) | 28,360 player-GW rows | Full xG, xA, xGI, xGC, ICT, Minutes, Starts | **Primary Out-of-Sample Holdout** |

---

## 2. Zero-Leakage Temporal Assertions

1. **Pre-Deadline Rolling States:** For every Gameweek $T$, player form, expected minutes, xG/90, and clean-sheet metrics are derived strictly from fixtures where $\text{GW} < T$.
2. **Cross-Season Track Records:** For early Gameweeks (GW1–GW5), player quality is initialized from prior season historical baselines and official starting prices (£100.0m budget constraints), preventing post-hoc outcome contamination.
3. **No In-Match / Outcome Leakage:** Current Gameweek minutes, goals scored, bonus points, and actual cards are completely masked until post-deadline scoring resolution.

