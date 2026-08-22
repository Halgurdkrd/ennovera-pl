# Ennovera PL Predictor — Phase 1 Data Collection Report

**Season target:** 2026-27 Premier League + Fantasy
**Generated:** Phase 1 (data collection). Environment note: run from a sandbox with
partial network egress — 3 of 4 external sources reachable (Club Elo blocked).

---

## 1. Data source status

| Source | Status | Detail |
|---|---|---|
| **football-data.co.uk** (PL history) | ✅ Downloaded | 10 seasons `E0_2016-17…2025-26.csv`, **380 rows each** (complete), 62–132 cols |
| **Club Elo** (clubelo.com) | ❌ **BLOCKED** | http + https + custom User-Agent all time out (HTTP 000) from this sandbox. **0 files.** |
| **FPL API** — bootstrap-static | ✅ Downloaded | `bootstrap_static.json` (1.58 MB): 600 players, 20 teams, 38 GWs, **xG present**, season **2026-27** (first deadline 2026-08-21) |
| **FPL API** — fixtures | ✅ Downloaded | `fixtures.json`: 380 fixtures, first kickoff **2026-08-21T19:00Z** |
| **FPL history** (vaastav) | ◐ Sampled | 11 seasons available (2016-17 → 2026-27). Downloaded 2026-27 metadata (`teams.csv`, `cleaned_players.csv`, `players_raw.csv`). **Full clone deferred** (~500 MB — too large to commit; run the clone locally). |

### football-data per-season summary
| Season | Rows | Cols | Teams | Missing% |
|---|---|---|---|---|
| 2016-17 | 380 | 65 | 20 | 0.0% |
| 2017-18 | 380 | 65 | 20 | 0.0% |
| 2018-19 | 380 | 62 | 20 | 0.0% |
| 2019-20 | 380 | 106 | 20 | 0.0% |
| 2020-21 | 380 | 106 | 20 | 0.0% |
| 2021-22 | 380 | 106 | 20 | 0.0% |
| 2022-23 | 380 | 106 | 20 | 0.0% |
| 2023-24 | 380 | 106 | 20 | 2.9% |
| 2024-25 | 380 | 120 | 20 | 3.2% |
| 2025-26 | 380 | 132 | 20 | 7.9% |

Column count grows over time as football-data added closing-odds and xG fields. **Core
columns are complete in every season**: `Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, HS,
AS, HST, AST` (+ HF/AF/HC/AC/HY/AY/HR/AR). The rising "Missing%" is entirely in
*optional* betting-market columns (many bookmaker columns are sparse in recent files),
not the match results/stats.

---

## 2. Team-name consistency (⚠️ 3-way mismatch — harmonization required)

The same club is spelled differently across sources. A canonical mapping is a
prerequisite before joining football-data ↔ FPL ↔ Elo.

| Canonical | football-data | FPL API | Assumed list |
|---|---|---|---|
| Manchester United | `Man United` | `Man Utd` | Man Utd |
| Tottenham | `Tottenham` | `Spurs` | Tottenham |
| Leeds United | `Leeds` | `Leeds` | Leeds United |
| Nottingham Forest | `Nott'm Forest` | `Nott'm Forest` | Nottm Forest |
| Manchester City | `Man City` | `Man City` | Man City |
| Wolverhampton | `Wolves` | *(not in 2026-27)* | Wolves |

**Action:** build a `TEAM_ALIASES` map (like the WC2026 project's) keyed to one canonical
spelling per club, covering all three source spellings.

---

## 3. Missing-data summary

- **football-data**: match results + shot/card stats complete across all 10 seasons.
  Sparse optional betting columns push the whole-file missing% to ≤7.9% (2025-26) — not a
  concern for modeling on core features.
- **Club Elo**: **100% missing** — clubelo.com is unreachable from this environment. This
  is the single biggest gap (see §6).
- **FPL 2026-27 `strength`**: `NaN` pre-season, but `strength_overall_home` /
  `strength_overall_away` (2–5 scale) **are** populated for all 20 teams.

---

## 4. Promoted-team data gaps (Sunderland, Coventry City, Hull City)

| Team | PL history CSVs | Club Elo | FPL API 2026-27 |
|---|---|---|---|
| **Sunderland** | ✅ yes (as `Sunderland`, last PL 2016-17) | ❌ blocked | ✅ yes (`Sunderland`) |
| **Hull City** | ✅ yes (as **`Hull`**, 2016-17) | ❌ blocked | ✅ yes (`Hull City`) |
| **Coventry City** | ❌ **none** (no PL season in the 10-yr window) | ❌ blocked | ✅ yes (`Coventry City`) |

**Cold-start risk:** Coventry City has **no top-flight match history** in the dataset and
(currently) no Elo — it will need a proxy (Championship form, FPL `strength_overall`, or a
promoted-team baseline). Sunderland/Hull have stale history (last PL ~9 seasons ago) — heavy
recency-weighting or Elo (once sourced) needed.

---

## 5. FPL API field availability

- **600 players**, **20 teams**, **38 gameweeks**. **xG data present.**
- Player fields include: `web_name, team, now_cost, total_points, expected_goals,
  expected_assists, expected_goal_involvements, expected_goals_conceded, minutes, bps,
  ict_index, influence, creativity, threat, selected_by_percent, form, points_per_game`.
- **FPL history `merged_gw.csv`** (per player × gameweek) is rich for FPL modeling:
  `name, position, team, xP, assists, bonus, bps, clean_sheets, creativity, expected_assists,
  expected_goal_involvements, expected_goals, expected_goals_conceded, goals_scored,
  ict_index, influence, kickoff_time, minutes, opponent_team, saves, selected, starts,
  team_a_score, team_h_score, …` — plus manager (`mng_*`) points for the 2025-26+ manager rules.

---

## 6. ⚠️ Team-list discrepancy vs the assumed 20

The **official FPL 2026-27 list** differs from the assumed list by exactly one swap:

- **FPL includes `Ipswich Town`** — the assumed list omitted it.
- **Assumed list includes `Wolves`** — FPL does **not** have Wolves in 2026-27.

**Official FPL 2026-27 (20):** Arsenal, Aston Villa, Bournemouth, Brentford, Brighton,
Chelsea, Coventry City, Crystal Palace, Everton, Fulham, Hull City, **Ipswich Town**, Leeds,
Liverpool, Man City, Man Utd, Newcastle, Nott'm Forest, Spurs, Sunderland.

**Resolve before modeling:** confirm whether Wolves or Ipswich is correct for 2026-27 (trust
the FPL API — but note it can carry a placeholder squad pre-season). This also affects which
Elo/history rows matter.

---

## 7. Recommended next steps

1. **Close the Club Elo gap.** clubelo.com is blocked here — fetch it from a machine with
   egress (all 25 teams incl. relegated), or substitute: (a) FiveThirtyEight SPI archive,
   (b) derive a home-grown Elo from the 10 seasons of football-data results (the WC2026
   project already does exactly this for internationals — reuse that pipeline).
2. **Build the canonical `TEAM_ALIASES` map** (football-data ↔ FPL ↔ Elo, §2).
3. **Resolve the Ipswich-vs-Wolves question** (§6) against the confirmed 2026-27 league.
4. **Coventry cold-start plan** (§4): Championship-form proxy or promoted-team baseline.
5. **Full FPL-history pull:** `git clone --depth 1 https://github.com/vaastav/Fantasy-Premier-League.git`
   for the per-GW player data (11 seasons) — kept out of this repo due to size.
6. **Fixtures→features:** join `fixtures.json` (380 2026-27 matches) with team strength +
   Elo to build the match-difficulty features.

---

### Files collected (this phase)
```
ennovera-pl/data/raw/pl_history/E0_2016-17.csv … E0_2025-26.csv   (10 files, ~1.5 MB)
ennovera-pl/data/raw/fpl/bootstrap_static.json                    (1.58 MB)
ennovera-pl/data/raw/fpl/fixtures.json                            (120 KB)
ennovera-pl/data/raw/fpl_history/2026-27/{teams,cleaned_players,players_raw}.csv
ennovera-pl/data/raw/elo/                                          (EMPTY — clubelo blocked)
```
