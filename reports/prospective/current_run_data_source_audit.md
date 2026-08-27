# ENNOVERA 2026-27 PROSPECTIVE RUN DATA SOURCE AUDIT
**Run ID:** `PROSPECTIVE_RUN_2026_08_28_001`  
**Execution Timestamp:** `2026-08-27T21:54:00Z`  

| Source Family | Endpoint / Provider | Status | Coverage | Latency | Point-in-Time Safe | Operational Fallback |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PL Fixtures & Kickoff** | Official Calendar API | **CONNECTED** | 100% | <1s | YES | Season Fixture Cache |
| **FPL Deadlines & Rulebook** | FPL Official Endpoint | **CONNECTED** | 100% | <1s | YES | Rulebook Snapshot V1 |
| **FPL Prices & Ownership** | FPL Live API Store | **CONNECTED** | 100% | <5m | YES | GW2 Final Price Matrix |
| **Confirmed Injuries & News** | Club Presser NLP Engine | **CONNECTED** | 98% | <15m | YES | Neutral Squad Prior |
| **Pre-match Expected XI** | Shared Football Core | **CONNECTED** | 100% | <30m | YES | Starter Frequency Prior |
| **Underlying xG & Shot Quality** | Opta Historical Ingestor | **CONFIGURED_OFFLINE_CORE** | 100% | <2h | YES | Bayesian Decoupled Prior |
| **Player Actions & DefCon** | Opta Historical Ingestor | **CONFIGURED_OFFLINE_CORE** | 100% | <2h | YES | Role Resistance Prior |
| **Tactical Style Vectors** | Internal Event Aggregator | **CONNECTED** | 100% | <4h | YES | Historical Style Matrix |
| **European Calendar & Travel** | UEFA Calendar Registry | **CONNECTED** | 100% | <1s | YES | Group Schedule Cache |
| **Domestic Cup Workload** | FA/EFL Cup Scorecard DB | **CONNECTED** | 100% | <1h | YES | Round History Store |
| **Managerial Changes** | Official Statement Feed | **CONNECTED** | 100% | <10m | YES | Variance Expansion Model |
| **Set-Piece & Penalty Roles** | Internal Role Tracker | **CONNECTED** | 100% | <12h | YES | Historical Hierarchy |

- **Real Authenticated Feeds:** 10 / 12 verified live; 2 offline historical registries operated via fail-closed internal priors.
- **Mock / Test Feeds Contamination:** **0 (Zero synthetic/mock records detected)**.
- **Critical Blockers:** **NONE**.
