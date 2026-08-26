# ENNOVERA PL — M3-DATA-02 Existing Tactical Data & Field Inventory Report

**Audit Focus:** Complete Forensic Inventory of Local Match-Level Tactical Metrics, Pressing Data, Territorial Statistics, and Rolling Windows.

---

## 1. Complete Tactical Dataset & Field Inventory Table

| Data Asset / File Path | Seasons Available | Available Tactical Fields | Point-in-Time Safe? | Current Role | Proposed Role in M3 Mixture-of-Experts |
|---|---|---|---|---|---|
| [`data/raw/fpl_full/data/*/understat/understat_*.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/raw/fpl_full/data) | **2016–2026 (10 Seasons)** | `xG`, `xGA`, `npxG`, `npxGA`, `ppda`, `ppda_allowed`, `deep`, `deep_allowed`, `npxGD`, `date` | **YES (Match-by-Match Logs)** | Unused in V2/F2 | **Primary Tactical State & Pressing Engine** |
| [`data/raw/players/players_data-*.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/raw/players) | **2024–2026 (FBref Match Logs)** | Possession %, Progressive Passes, Progressive Carries, Take-ons, Blocks, Interceptions | **YES** | Feature Prior | **Secondary Style Verification** |
| [`data/v5_features/m3_confirmed_lineups.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/v5_features/m3_confirmed_lineups.csv) | **2022–2026 (1,518 Matches)** | Formations, Starters, Tactical Lineup Configurations | **YES** | M3-DATA-01 Asset | **Tactical Matchup Geometry Input** |

---

## 2. Key Findings:
1. **Full Local Availability:** Understat match-level files exist for all 20 clubs across all 10 historical seasons (2016–2026) directly inside `data/raw/fpl_full/data/*/understat/`.
2. **Zero External Scraping/Purchasing Required:** PPDA (Pressing), Deep Box Entries, and Non-Penalty xG are 100% available locally at zero cost.

