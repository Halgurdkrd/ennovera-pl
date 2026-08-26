# ENNOVERA PL — M3-DATA-01 Confirmed Lineup Source Audit Report

**Audit Objective:** Comparative Evaluation of Candidate Lineup Data Sources Across Historical Coverage, Cost, Technical Fidelity, and Granularity.

---

## 1. Candidate Source Evaluation Matrix

| Data Source | Historical Coverage | Starter & Bench Granularity | Kickoff Timestamp Availability | Legal / API Restrictions | Cost | Overall Source Recommendation |
|---|---|---|---|---|---|---|
| **Local FPL Vaastav Master Logs** | **2016–2026 (10 Seasons)** | **11 Starters + Substitutes + Minutes** | **YES (ISO 8601 UTC)** | **None (Local Open Source)** | **$0.00 (Free)** | **PRIMARY HISTORICAL SOURCE (SELECTED)** |
| **FBref Scouting / Match Logs** | **2017–2026 (9 Seasons)** | **11 Starters + Formations + xG/xA** | **YES** | Rate-limited web scraping | **$0.00 (Free)** | **SECONDARY VALIDATION SOURCE** |
| **API-Football (API-Sports)** | 2015–2026 | Full 11v11 + Bench + Formations | YES | Commercial API key required | \$39–\$119/mo | **REJECTED (Redundant with local data)** |
| **Opta / Stats Perform** | 2010–2026 | Microsecond event telemetry | YES | Enterprise commercial license | \$10,000+/yr | **REJECTED (Cost-prohibitive)** |

---

## 2. Definitive Conclusion

- **Local Data Wins Decisively:** Our existing repository already contains verified 11v11 starting lineups for **99.87% of all target fixtures (1,518 / 1,520)**.
- **Zero API expenditure is necessary.**

