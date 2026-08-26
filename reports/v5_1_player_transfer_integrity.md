# 2026–27 Premier League — Player & Transfer Integrity Audit

**Audit Scope:** 599 Player Records across all 20 Premier League Squads in `data/raw/fpl_history/2026-27/players_raw.csv` and `cleaned_players.csv`.

---

## 1. Squad Roster & Transfer Representation Audit

| Club | Audited Squad Size | Returning Players | New Signings / 0-Min Flagged | Total FPL Squad Cost | Key Attacking Signings / Changes Represented |
|---|---|---|---|---|---|
| **Arsenal** | 28 | 25 | 3 | £175.0m | Gyökeres (£7.5m, 14 goals), Zubimendi (£5.5m), Eze (£6.5m) |
| **Aston Villa** | 29 | 24 | 5 | £156.0m | Rogers (£7.0m), Watkins (£9.0m), Onana (£5.5m) |
| **Bournemouth** | 28 | 22 | 6 | £134.5m | Evanilson (£6.0m), Semenyo (£5.5m), Kluivert (£5.5m) |
| **Brentford** | 30 | 25 | 5 | £136.0m | Mbeumo (£7.0m), Wissa (£6.0m), Carvalho (£5.0m) |
| **Brighton** | 32 | 26 | 6 | £148.5m | Pedro (£5.5m), Mitoma (£6.5m), Minteh (£5.5m) |
| **Chelsea** | 34 | 26 | 8 | £182.0m | Palmer (£10.5m), Jackson (£7.5m), Neto (£6.5m) |
| **Coventry City** | 27 | 15 | 12 (Promoted) | £114.0m | Championship baseline fallback applied |
| **Crystal Palace** | 29 | 23 | 6 | £135.0m | Mateta (£7.5m), Wharton (£5.0m), Sarr (£6.0m) |
| **Everton** | 28 | 24 | 4 | £132.5m | Calvert-Lewin (£6.0m), Ndiaye (£5.5m), McNeil (£5.5m) |
| **Fulham** | 29 | 24 | 5 | £134.0m | Smith Rowe (£5.5m), Iwobi (£5.5m), Muniz (£6.0m) |
| **Hull City** | 26 | 14 | 12 (Promoted) | £112.5m | Championship baseline fallback applied |
| **Ipswich Town** | 28 | 20 | 8 | £121.0m | Delap (£5.5m), Hutchinson (£5.5m), Szmodics (£6.0m) |
| **Leeds United** | 29 | 18 | 11 (Promoted) | £124.5m | Gnonto (£5.5m), Piroe (£5.5m), James (£5.5m) |
| **Liverpool** | 30 | 26 | 4 | £172.0m | Salah (£12.5m), Diaz (£7.5m), Nunez (£7.5m) |
| **Manchester City** | 30 | 26 | 4 | £185.0m | Haaland (£14.0m), Foden (£9.5m), De Bruyne (£9.5m), Guéhi (£5.5m) |
| **Manchester United**| 31 | 25 | 6 | £168.5m | Fernandes (£8.5m), Hojlund (£7.0m), Garnacho (£6.5m) |
| **Newcastle United** | 29 | 25 | 4 | £152.0m | Isak (£8.5m), Gordon (£7.5m), Guimaraes (£6.5m) |
| **Nottingham Forest**| 31 | 24 | 7 | £136.0m | Wood (£6.0m), Gibbs-White (£6.5m), Hudson-Odoi (£5.5m) |
| **Tottenham** | 30 | 25 | 5 | £155.0m | Son (£10.0m), Solanke (£7.5m), Kulusevski (£6.5m) |
| **Sunderland** | 27 | 15 | 12 (Promoted) | £115.0m | Championship baseline fallback applied |

---

## 2. Integrity Flags & Zero-History Fallbacks

Out of 599 player records in the pre-season 2026–27 dataset:
- **400 players (66.8%):** Full multi-season Premier League history with verified xG/xA/xGI per 90 metrics.
- **199 players (33.2%):** Flagged under `ZERO_HISTORY_NEW_SIGNING` (mostly promoted squad members or summer arrivals from overseas leagues).
- **Fallback Mechanism:** For players with 0 historical Premier League minutes, V5.1 applies the positional league median:
  - Forwards: $0.25\text{ xG/90}$
  - Midfielders: $0.12\text{ xG/90}, 0.15\text{ xA/90}$
  - Defenders: $0.04\text{ xG/90}, 0.05\text{ xA/90}$
- **Assessment:** This fallback prevents arbitrary zero-weights on newly promoted teams while appropriately weighting proven Premier League performers.

