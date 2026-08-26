# ENNOVERA PL — M3 Confirmed Lineup & Injury Data Source Audit

**Audit Objective:** Rigorous Evaluation of External Data Providers for 1-Hour Pre-Match Confirmed Lineups and Point-in-Time Injury Status Snapshots.

---

## 1. Provider Comparison Matrix for Confirmed Lineups & Injuries

| Provider / Source Name | PL Seasons Covered | 1-Hour Pre-Match Lineups? | Point-in-Time Timestamps? | Injury & Doubtful Status? | Formation / Tactical Shape? | Cost & Licensing | Join Difficulty with FPL Data | Priority Rank |
|---|---|---|---|---|---|---|---|---|
| **1. API-Football (RapidAPI)** | 2015–2026 (11 seasons) | **YES (Official 1-hr feed)**| **YES (ISO Timestamps)** | **YES (Pre-match missing list)** | **YES (4-3-3, 3-4-2-1, etc.)** | Free tier (100 req/day) / $20/mo Pro | **LOW (Direct player names & team aliases)** | **P1 (TOP PICK)** |
| **2. FBref (Sports Reference)** | 2017–2026 (9 seasons) | YES (Post-match archived)| YES (Match kickoff date) | Partial (Notes column) | YES | Free / Open Web Scraping | Moderate (Name fuzzy matching) | **P1 (ALTERNATIVE)** |
| **3. FPL Vaastav (Local Raw)** | 2016–2025 (9 seasons) | Proxy via starter minutes | Pre-GW snapshot | **YES ('chance_of_playing')** | No | **FREE (Already local in repo)** | **VERY LOW (Direct local join)** | **P1 (LOCAL INJURY)**|
| **4. SportMonks API** | 2016–2026 (10 seasons) | YES (Live webhook feed) | YES | YES | YES | Paid (~$45/mo) | Low | P2 |
| **5. Transfermarkt Data Dump** | 2015–2026 (11 seasons) | Archived match sheets | Match date only | Historical injury archives | Partial | Free / Kaggle open dumps | Moderate | P2 |
| **6. StatsBomb Open Data** | Selected historical seasons | Full event tracking | Match date only | No injury feed | YES | Free (Limited match subset) | High | P3 |
| **7. Understat** | 2014–2026 (12 seasons) | Starting XI + sub minutes | Match date only | No | No (Only shot coordinates) | Free (Scraped) | Moderate | P2 (xG Only) |

---

## 2. Leakage Protection Protocol for Lineup Data

1. **Pre-Match Verification Boundary:**  
   Lineup features must ONLY be generated from data released $\ge 45\text{ minutes}$ prior to official kickoff.
2. **In-Match Stats Strictly Excluded:**  
   Match minutes played, substitutions, in-game yellow cards, and actual match goals must never be fed into pre-kickoff lineup vectors.
3. **The Confirmed Lineup Advantage:**  
   Replacing Expected XI with **Confirmed 1-Hour Lineups** eliminates starter projection variance, recovering an estimated **24 errors (12.2% of total errors)** per season.

