# ENNOVERA PL — M3-DATA-03 Manager Data & Field Inventory Report

**Audit Focus:** Complete Forensic Inventory of Premier League Managerial Appointments, Departures, Tenures, and Point-in-Time Status (2016–2026).

---

## 1. Managerial Data Asset Inventory Table

| Manager Metric / Field | Historical Seasons Available | Match-by-Match Granularity | Point-in-Time Verified? | Current Repository Role | Proposed Role in M3 Mixture-of-Experts |
|---|---|---|---|---|---|
| `manager_name` | **2016–2026 (10 Seasons)** | Matchday Head Coach / Manager | **YES (Match Kickoff Gated)** | Feature Prior | **Managerial Identity Tracking** |
| `appointment_date` | **2016–2026 (10 Seasons)** | Official Club Announcement Date | **YES ($\text{Announced} \le \text{MatchDate}$)** | Unused in V2/F2 | **Tenure Duration Calculation** |
| `is_new_manager_1` | **2016–2026 (10 Seasons)** | First Premier League Match in Charge | **YES** | Unused in V2/F2 | **Interim / New Manager Reset Flag** |
| `is_new_manager_3` | **2016–2026 (10 Seasons)** | Within First 3 Matches of Appointment | **YES** | Unused in V2/F2 | **Transition Regime Window** |
| `manager_tenure` | **2016–2026 (10 Seasons)** | Cumulative Matches in Charge | **YES** | Unused in V2/F2 | **Tactical Stability Metric** |

---

## 2. Point-in-Time Verification:
- **Zero Lookahead:** All manager records satisfy $\text{appointment\_date} \le \text{match\_date}$. Mid-season sackings taking effect after a matchday are strictly applied to the subsequent fixture.
- Saved feature table: [`data/v5_features/m3_manager_state.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/v5_features/m3_manager_state.csv).

