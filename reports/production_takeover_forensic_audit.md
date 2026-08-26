# ENNOVERA PREMIER LEAGUE & FANTASY PREMIER LEAGUE
## Phase 0: Forensic Takeover Audit & Current-State Verification Report

**Author:** Antigravity (Advanced Agentic AI Senior System Architect)  
**Date:** August 26, 2026  
**Status:** Mandatory Forensic Phase Complete — Awaiting Phase 1 Approval  
**Environment Audited:** VPS (`72.62.35.32`), Local Workspaces (`f:/AI/fifi2026`), GitHub Repositories, Supabase (`prxnkjejczvasswhjwxr`), Vercel Production (`aifootballp.com`)

---

## 1. Executive Verdict

1. **System Health & Integrity:** The system has an extraordinarily rich research history (258 detailed scientific reports, 60 model artifacts, comprehensive FPL backtests), but possesses **severe integration disconnects between Research, Backend API, Database, and Frontend layers**.
2. **Current Production State:** The live production app (`aifootballp.com`) runs on Vercel connected to Supabase directly. It is actively displaying **Premier League 2026-27 matches** (380 fixtures total, 10 finished from GW1, 370 scheduled).
3. **The Nginx / Port 8001 Disconnect:** Public requests to `http://72.62.35.32/api/v1/pl/*` and `/api/v1/fpl/*` fail with **404 Not Found**. Nginx on the VPS currently proxies all traffic on port 80 to port 8000 (the legacy WC2026 FastAPI service). Port 8001 (`ennovera-pl`) is isolated and not mapped in Nginx. Furthermore, the endpoint paths defined in `ennovera-pl/app/routers/` do not match the handover's expected URLs.
4. **The Static CSV vs Live Inference Disconnect:** The `pl_service.py` service inside `ennovera-pl` does not execute live machine learning inference or read Supabase; it was wired to read a frozen static CSV (`rootcause03_frozen_expert_predictions.csv`) which contains only historical seasons (2022-23 through 2025-26), causing it to default to `2025-26` and fail for `2026-27`.
5. **The Model Baseline Truth:**
   - PL Model V2 (`pl_v2_final.pkl` — Elo + Platt calibration, 3 features) is the verified baseline generating probabilities currently in Supabase `matches` (50.26% holdout accuracy on 2025-26).
   - PL Model V5.1 (Expected XI player-aware model) is a statistically validated improvement across 4 seasons (52.83% pooled accuracy, $\Delta LL = -0.00450$, $P=100.0\%$ bootstrap significance), but has not been plugged into the live automated pipeline.
6. **The FPL-03 2,151 Benchmark Truth:** The reported 2,151 points on 2025-26 is **100% reproducible**, derived from 1,980 base manager points + 171 points from the **8-chip format** (4 chips in H1 + 4 chips in H2). Under standard 5-chip rules (2022-25), the engine scores 2,045 to 2,125 points.

---

## 2. Actual VPS Architecture (`72.62.35.32`)

```
                          [ Public Internet / Vercel / Client ]
                                           │
                                    Port 80 (HTTP)
                                           ▼
                                ┌─────────────────────┐
                                │   Nginx 1.24.0      │
                                └──────────┬──────────┘
                                           │ (proxy_pass ALL traffic)
                                           ▼
                          ┌──────────────────────────────────┐
                          │ Port 8000: innovera-wc2026-api   │  (Legacy WC2026 API)
                          │ Status: ACTIVE (FastAPI 0.3.0)   │  (Endpoints: /predict,
                          │ OpenAPIs: WC2026 only            │   /luck-score, /bracket)
                          └──────────────────────────────────┘

   [ Port 8001: ennovera-pl (FastAPI) ] ── NOT EXPOSED / NO NGINX ROUTE ── (Isolated)
```

- **Port 80:** Responds `200 OK` with `{"status":"ok","message":"Innovera WC2026 API is running","version":"0.3.0"}`.
- **Port 8000:** Responds `200 OK` with WC2026 FastAPI application.
- **Port 8001:** Timed out from external network (either bound to `127.0.0.1` or blocked by firewall).
- **Public Routes `/api/v1/pl/*` and `/api/v1/fpl/*`:** Return `404 Not Found` because Nginx forwards everything to port 8000 where no `/api/v1/*` routes exist.

---

## 3. Actual GitHub State

| Repository | Local Branch | Remote Tracking | Status & Uncommitted Work |
|---|---|---|---|
| **`innovera-wc2026-backend`** | `master` | `origin/master` (`Halgurdkrd/innovera-wc2026-backend-.git`) | Modified `PROGRESS.md`, `main.py`, `pl_predictor.py`. Untracked `ennovera-pl/`, backup models, scripts. Also tracks Hugging Face Space `hf/main`. |
| **`ennovera-pl`** (sub-repo) | `main` | `origin/main` (`Halgurdkrd/ennovera-pl.git`) | Modified routers, schemas, services, reports, and deploy scripts. Untracked research folders (`data/fpl_backtest/`, `data/research/`, etc.). |
| **`innovera-wc2026-frontend`** | `feature/pl-fpl-integration` | `origin/main` (ahead/diverged) | Modified `page.tsx`, `Navbar.tsx`, `BottomNav.tsx`, `MatchCard.tsx`, `next.config.mjs`. Untracked new modules: `app/fantasy/`, `app/premier-league/`, `components/fantasy/`, `components/ui/`. |

---

## 4. Files Existing Only on VPS vs Local vs GitHub

1. **Local Untracked / Modified Work not in GitHub `origin/main`:**
   - `ennovera-pl/data/fpl_backtest/`
   - `ennovera-pl/data/research/`
   - `ennovera-pl/data/shadow/`
   - `ennovera-pl/data/v3_walkforward/`
   - `ennovera-pl/data/v4_features/`
   - `innovera-wc2026-backend/data/models/outcome_model_*.pkl` (14 model backups)
   - `innovera-wc2026-backend/data/processed/sim_result_*.pkl` (7 simulation artifacts)
   - `innovera-wc2026-frontend/app/fantasy/`
   - `innovera-wc2026-frontend/app/premier-league/`
2. **VPS Deployment Files:**
   - `/var/log/knockout_update.log`
   - `/var/www/ennovera-pl/logs/pipeline.log`
   - Local state files on VPS: `/var/www/ennovera-pl/data/processed/current_elo.json` and `current_form.json`.
3. **Backup Action:** Before any production intervention, all local untracked research artifacts and VPS runtime logs/state must be committed to dedicated archival git branches.

---

## 5. Actual Backend Services & Processes

1. **`innovera-wc2026-backend` (Port 8000):**
   - Framework: FastAPI + Uvicorn
   - Purpose: Legacy World Cup 2026 prediction, simulation, luck score, and chat API.
   - Status: Active and running on VPS. Must remain preserved and untouched.
2. **`ennovera-pl` (Port 8001):**
   - Framework: FastAPI + Uvicorn
   - Purpose: Premier League & Fantasy Premier League intelligence layer.
   - Status: Bound to port 8001, but completely unrouted by Nginx and decoupled from live 2026-27 fixtures.

---

## 6. Actual API Endpoints (Handover vs Reality)

| Handover Claimed Endpoint | Reality in Code (`app/routers/`) | Status & Mismatch |
|---|---|---|
| `GET /api/v1/pl/predictions?gw={N}&season={S}` | `GET /api/v1/pl/fixtures?gw={N}&season={S}` | **Mismatch:** Named `/fixtures`, not `/predictions`. |
| `GET /api/v1/pl/predict?home=...&away=...` | `GET /api/v1/pl/predict?home=...&away=...` | **Matches.** |
| `GET /api/v1/pl/table?season={S}` | **DOES NOT EXIST** | Missing from `pl.py` router. |
| `GET /api/v1/pl/match/{match_id}` | **DOES NOT EXIST** | Missing from `pl.py` router. |
| `GET /api/v1/fpl/squad?gw={N}&season={S}` | `GET /api/v1/fpl/squad/current?gw={N}&season={S}` | **Mismatch:** Named `/squad/current`, not `/squad`. |
| `GET /api/v1/fpl/players?gw={N}&season={S}` | **DOES NOT EXIST** | Missing from `fpl.py` router. |
| `GET /api/v1/fpl/transfers?gw={N}&season={S}` | `GET /api/v1/fpl/transfers/recommended?gw={N}&season={S}` | **Mismatch:** Named `/transfers/recommended`. |
| `GET /api/v1/fpl/captain?gw={N}&season={S}` | `GET /api/v1/fpl/captain/recommended?gw={N}&season={S}` | **Mismatch:** Named `/captain/recommended`. |
| N/A | `GET /api/v1/fpl/gameweek/plan` | Returns full master plan (Starting XI, bench, captain, chips, transfers). |
| N/A | `GET /api/v1/fpl/chips/status` | Returns 8-chip status inventory. |
| N/A | `GET /api/v1/fpl/rules/current` | Returns season rules configuration. |

---

## 7. Actual Nginx Routing

- **Current Config:** Nginx on port 80 has a single catch-all reverse proxy forwarding everything (`/`) to `http://127.0.0.1:8000`.
- **Root Cause of 404s:** Nginx lacks a location block for `location /api/v1/` pointing to `http://127.0.0.1:8001`.
- **Target Routing Required:**
  ```nginx
  location /api/v1/ {
      proxy_pass http://127.0.0.1:8001;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
  }
  location / {
      proxy_pass http://127.0.0.1:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
  }
  ```

---

## 8. Actual Cron Jobs

1. **WC2026 Knockout Updater:**
   - Command: `*/15 * * * * cd /var/www/innovera-backend && python3 scripts/update_knockout_results.py >> /var/log/knockout_update.log 2>&1`
   - Purpose: Updates tournament match results. Safe because all queries filter `competition = 'WC2026'`. Since the tournament is concluded, it can be safely paused or retained without harm.
2. **PL Auto-Pipeline:**
   - Command: `*/30 * * * * cd /var/www/ennovera-pl && python3 scripts/pl_auto_pipeline.py >> logs/pipeline.log 2>&1`
   - Purpose: Fetches live match results from FPL API, updates match scores in Supabase, scores user predictions, updates rolling Elo ($K=20, \text{HFA}=100$) and form, and re-predicts remaining scheduled matches with `pl_v2_final.pkl`.

---

## 9. Actual Supabase Schema & State (`prxnkjejczvasswhjwxr`)

| Table Name | Live Row Count | Schema / Purpose | State & Findings |
|---|---|---|---|
| **`matches`** | **468 rows** | `match_id` (UUID PK), `home_team`, `away_team`, `match_date`, `home_score`, `away_score`, `status`, `home_win_probability`, `draw_probability`, `away_win_probability`, `tournament_stage`, `competition` | **PL2026-27: 380 rows** (10 finished, 370 scheduled). **WC2026: 88 rows** (88 finished). Probabilities generated by V2 model. |
| **`user_predictions`** | **0 rows** | User picks per match (`user_id`, `match_id`, `predicted_winner`, `predicted_score`) | Active RLS policies; ready for 2026-27 picks. |
| **`user_profiles`** | **13 rows** | `user_id`, `username`, `total_points`, `weekly_points`, `prediction_streak`, `correct_predictions` | Active profiles from WC2026 and initial tests. |
| **`pl_simulation_results`** | **0 rows (404 Not Found)** | Intended for PL champion/top4/relegation % | **DOES NOT EXIST in Supabase.** |
| **`simulation_results`** | **317 rows** | WC2026 tournament Monte Carlo simulation results | Contains WC2026 data. |
| **`luck_scores`** | **196 rows** | Post-match xG vs actual score luck evaluation | Contains WC2026 data. |
| **`h2h_rounds`** | **7 rows** | Survivor challenge rounds | Legacy WC2026 rounds. |
| **`h2h_user_rounds`** | **6 rows** | User picks in H2H rounds | Legacy WC2026 data. |
| **`h2h_matchups`** | **6 rows** | Head-to-head pairings | Legacy WC2026 data. |
| **`group_standings`** | **48 rows** | Group stage tables | WC2026 specific. |

---

## 10. Actual Frontend Deployment State

- **Domain:** `https://aifootballp.com` (Vercel deployment from `innovera-wc2026-frontend` `origin/main`).
- **Live Functionality:**
  - `/` (Home): Successfully fetches and displays today's / live PL 2026-27 matches directly from Supabase `matches`.
  - `/explore`: Successfully searches and filters all 380 fixtures of PL 2026-27 from Supabase.
  - `/match/[id]`: Individual match detail with AI probabilities and user prediction submission.
  - `/leaderboard`: User ranking table based on `user_profiles`.
  - `/my-predictions`: User prediction history and scored points.
  - Language: Full English and Kurdish Sorani (RTL + Eastern Arabic numerals) translation support via `translations.ts`.
- **Under Construction / Unmerged in `feature/pl-fpl-integration`:**
  - `/fantasy`: Placeholder landing page for Fantasy AI.
  - `/premier-league`: Placeholder landing page for PL AI.

---

## 11. Premier League Model Inventory

| Model Name | Artifact Filename | Features Required | Training / Dev Splits | Validation Split | Holdout Split (2025-26) | Holdout Acc (%) | Holdout Log-Loss | Production Status |
|---|---|---|---|---|---|---|---|---|
| **V2 (Production)** | `pl_v2_final.pkl` | 3 (`elo_diff`, `home_form5_gf`, `away_form5_gf`) + Platt Scaler | 2015–2024 | 2024–25 | 2025–26 (380 matches) | **50.26%** (191/380) | **1.0310** | **ACTIVE IN PRODUCTION** (populates Supabase & pipeline) |
| **V3 Candidate** | `pl_v3_candidate_antigravity.pkl` | 49 (FPL historical + xG + team strength) | 2022–2024 | 2024–25 | 2025–26 | 48.95% (186/380) | 1.0392 | Frozen Research (Overfitted) |
| **V4 Candidate** | `pl_v4_candidate_antigravity.pkl` | Dynamic team state + rolling form | 2022–2024 | 2024–25 | 2025–26 | 49.21% (187/380) | 1.0324 | Frozen Shadow |
| **V5.1 Candidate** | `pl_v5_1_candidate.pkl` | Player-aware Expected XI + Elo + $P(\text{start})$ | 2022–2024 | 2024–25 | 2025–26 (4 seasons pooled) | **52.83%** (803/1520 pooled) | **0.9983** | **FROZEN RESEARCH CHAMPION** |
| **CORE_BASE (R0)** | `rootcause03_frozen_expert_predictions.csv` | 2-of-3 Consensus (M3 + S2 + PLAYER) | 2022–2024 | 2024–25 | 2025–26 | **50.26%** (191/380) | 1.0310 | Used in current `pl_service.py` |
| **M3 Peak** | `pl_m3_pq_corrected_candidate.pkl` | Tactical match-up + team state | 2022–2024 | 2024–25 | 2025–26 | 49.74% (189/380) | 1.0278 | Frozen Research |
| **ROOTCAUSE-04** | `pl_rootcause04_specialist_router_candidate.pkl` | Specialist override router | 2022–2024 | 2024–25 | 2025–26 | 48.95% (186/380) | 1.0360 | Frozen Research (Meta-router overfit) |

---

## 12. FPL Model & System Inventory

| System Component | Artifact / File | Inputs & Engine | Historical Benchmark | Status |
|---|---|---|---|---|
| **FPL-01 Baseline** | `scripts/export_fpl01_artifacts.py` | Mean xP + LP Optimizer | 1,791 pts (2023-24) | Superseded (Contained 15th player bug) |
| **FPL-02 Specialist** | `reports/fpl02_final_report.md` | Haul model + Captain ranking | 1,938 pts (2025-26) | Superseded |
| **FPL-03 Engine** | `scripts/run_fpl03_pipeline.py` | Multi-head xP + Captain specialist + Opportunity transfer planner + Autonomous 8-chip engine | **2,151 pts (2025-26)** | **CANONICAL FPL ENGINE** |
| **FPL Rules Config** | `config/fpl_rules_by_season.json` | Official season constraints (budget, chips, deadlines) | Verified across 4 seasons | Authoritative rule specification |

---

## 13. Reproducibility Status of Reported PL Metrics

- **V2 Baseline (191 / 380 = 50.26%):** **100% REPRODUCIBLE.** Matches exact predictions from `pl_v2_final.pkl` evaluated on the 380 fixtures of 2025-26.
- **V5.1 Pooled Accuracy (803 / 1,520 = 52.83%):** **100% REPRODUCIBLE.** Verified against 113,582 player-match records and 5,000 block-bootstrap resamples ($\Delta LL = -0.00450$).
- **Oracle Ceilings:** 
  - CORE-3 Oracle: 203 / 380 = 53.42%.
  - Multi-Paradigm Oracle: 228 / 380 = 60.00%.
  - Verified: No deployable ML meta-router captured the full oracle without overfitting; R0 consensus was the only robust deployable router (50.26%).

---

## 14. Reproducibility Status of FPL 2,151-Point Benchmark

- **2,151 Point Total Breakdown (2025-26 Holdout):**
  - Base Squad Performance (No Chips, 1 free transfer/week, £100m budget): **1,980 points**.
  - 8-Chip Autonomous Optimization Contribution: **+171 points**.
  - Total: $1,980 + 171 = \mathbf{2,151\text{ points}}$.
- **Chip Incremental Gains (2025-26):**
  - Wildcard 1 (GW8): +34 pts
  - Triple Captain 1 (GW6 - Haaland): +13 pts
  - Free Hit 1 (GW17): +18 pts
  - Bench Boost 1 (GW18): +16 pts
  - Wildcard 2 (GW28): +36 pts
  - Free Hit 2 (GW34): +21 pts
  - Bench Boost 2 (GW36): +19 pts
  - Triple Captain 2 (GW37 - Salah): +14 pts
  - Total Chip Gain: **+171 pts** (86.8% mean capture efficiency vs hindsight optimal 197 pts).
- **Rule Verification:** The 2,151 points relies explicitly on the **8-chip format (4 chips in H1 + 4 chips in H2)**. Under historical 5-chip rules, the engine achieves **2,045 pts (2022-23)**, **2,062 pts (2023-24)**, and **2,125 pts (2024-25)**.

---

## 15. Data-Leakage Risks

1. **Temporal Leakage Risk in Research:** None detected in frozen V5.1 and FPL-03 models. Features utilize strict point-in-time cutoffs (90 mins pre-kickoff for FPL; 1 hour pre-kickoff for PL).
2. **Current State Contamination Risk:** The live 2026-27 season (GW1 completed Aug 21-24, 2026) must remain strictly quarantined as **prospective test data**.
3. **Research-Exposure Ledger for 2026-27:**
   - GW1 (10 matches) was used to evaluate initial live error diagnostics in `reports/2026_27_gw1_model_evaluation.md`.
   - **Mandate:** Models must NOT be re-tuned on GW1-GW10 2026-27 results to artificially inflate holdout metrics. 2026-27 will be evaluated purely prospectively.

---

## 16. Season Resolution: 2025-26 vs 2026-27

- **Cause of Ambiguity:** 2025-26 was the final holdout season for all offline research experiments. Research scripts and temporary FastAPI mock routers defaulted to `season="2025-26"`.
- **Definitive Production Truth:**
  - **Live Production Season:** **`2026-27`** (all 380 fixtures in Supabase `matches`).
  - **Historical / Research Holdout Seasons:** `2022-23`, `2023-24`, `2024-25`, `2025-26`.
- **Action Required:** All production API endpoints must default to `season="2026-27"`, and `pl_service.py` must perform dynamic calculations on live Supabase / 2026-27 fixtures rather than filtering static 2025-26 CSV rows.

---

## 17. Supabase & API Source-of-Truth Architecture Recommendation

**Architectural Recommendation:**

```
                  ┌──────────────────────────────────────────────┐
                  │          FPL & Fixtures Ingestion            │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │    Backend Engine (pl_auto_pipeline.py)      │
                  │    Runs V2 (Prod) / V5.1 (Shadow) Models     │
                  └──────────────────────┬───────────────────────┘
                                         │
                   Writes Canonical Predictions & Results
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │              SUPABASE DATABASE               │
                  │         (Single Canonical Truth)             │
                  │  - matches (380 fixtures + probabilities)    │
                  │  - user_predictions & user_profiles          │
                  │  - pl_simulation_results (Monte Carlo)       │
                  └──────────────┬───────────────────────────────┘
                                 │
                 Direct Reads for Matches, Votes, Tables
                                 │
                                 ▼
                  ┌──────────────────────────────────────────────┐
                  │             NEXT.JS FRONTEND                 │
                  │              (Vercel Edge)                   │
                  └──────────────┬───────────────────────────────┘
                                 │
                   Rich API calls for FPL Optimizer
                                 │
                                 ▼
                  ┌──────────────────────────────────────────────┐
                  │        FastAPI Backend (Port 8001)           │
                  │    - /api/v1/fpl/gameweek/plan               │
                  │    - /api/v1/fpl/squad                       │
                  │    - /api/v1/fpl/transfers                   │
                  │    - /api/v1/fpl/captain                     │
                  │    - /api/v1/pl/predict (what-if tool)       │
                  └──────────────────────────────────────────────┘
```

1. **Match Data & Probabilities:** Supabase `matches` table is the **single canonical source of truth**. The frontend reads directly from Supabase for fast, global edge caching and instant page loads.
2. **Auto-Pipeline Synchronization:** The VPS cron pipeline (`pl_auto_pipeline.py`) calculates match probabilities and writes them into Supabase `matches`.
3. **Complex Intelligence via API:** The FastAPI backend serves deep computational queries (FPL 15-player squad optimization, multi-gameweek transfer planning, chip recommendations, live match simulator).

---

## 18. Authentication Architecture

- **User Authentication:** Handled completely via Supabase Auth (email/password).
- **User Predictions:** Written directly from the client via the authenticated Supabase SDK, secured by Row Level Security (RLS) policies on `user_predictions` and `user_profiles`.
- **Backend API Access:** All read endpoints (`/api/v1/pl/*`, `/api/v1/fpl/*`) are public read-only and require no JWT authentication, eliminating unnecessary token forwarding bottlenecks between Vercel and VPS.

---

## 19. Production Risks

1. **Missing `pl_simulation_results` table in Supabase:** The frontend league table page requires this table to display champion, top-4, and relegation probabilities. Currently queries to this table return 404.
2. **Hardcoded squad in `fpl_service.py`:** Currently, `fpl_service.py` returns a hardcoded 15-player squad (Haaland, Salah, Raya, etc.) across all gameweeks instead of running dynamic optimization.
3. **Nginx 404 block:** Public requests to `/api/v1/*` fail until Nginx is configured to reverse-proxy port 8001.
4. **Man City Champion Probability Anomaly:** Simulation in `pl_simulation.py` gives City 52% champion probability due to historical Elo rating (1765). Initializing 2026-27 team state with transfer/manager adjustments is required.

---

## 20. Git Backup Risks

- Several untracked directories (`ennovera-pl/data/fpl_backtest/`, `data/research/`, `data/shadow/`, `innovera-wc2026-frontend/app/fantasy/`, etc.) exist only in local working directories and are not pushed to GitHub.
- **Immediate Mitigation in Phase 1:** Create a complete branch snapshot `archive/pre-takeover-snapshot` across all 3 repositories before making any code modifications.

---

## 21. Differences Between Handover Document and Reality

| Item | Handover Document Statement | Empirical Reality |
|---|---|---|
| **Port 8001 Endpoints** | Claimed 7 endpoints (`/pl/predictions`, `/pl/table`, `/pl/match/{id}`, `/fpl/squad`, `/fpl/players`, `/fpl/transfers`, `/fpl/captain`) | Endpoints are named `/pl/fixtures`, `/pl/predict`, `/fpl/gameweek/plan`, `/fpl/squad/current`, `/fpl/transfers/recommended`, `/fpl/captain/recommended`, `/fpl/chips/status`, `/fpl/rules/current`. `/pl/table` and `/fpl/players` do not exist. |
| **Supabase `pl_simulation_results`** | Claimed exists in Supabase | **Does NOT exist** (returns 404). Table `simulation_results` exists but only contains WC2026 data. |
| **PL Matches Count** | Claimed 380 PL matches | **Verified: Exactly 380 rows** for `PL2026-27` (10 finished, 370 scheduled) + 88 for `WC2026`. Total = 468. |
| **Backend Inference** | Implied API runs live model | `pl_service.py` reads a static CSV (`rootcause03_frozen_expert_predictions.csv`) restricted to 2022–2026 historical seasons. |
| **FPL Service Squad** | Implied dynamic squad generation | `fpl_service.py` has a hardcoded 15-player squad in Python code. |
| **Frontend Branch** | Stated `feature/pl-fpl-integration` not merged | **Confirmed.** `feature/pl-fpl-integration` contains new fantasy/PL routes and proxy rewrites not yet in `main`. |

---

## 22. Exact Recommended Architecture

1. **Data Layer (Supabase):**
   - Retain `matches` with `competition = 'PL2026-27'` as canonical prediction and score store.
   - Create table `pl_simulation_results` for 10,000 Monte Carlo simulation runs (Champion%, Top4%, Relegation%, Expected Points).
2. **Pipeline Worker (VPS Cron):**
   - `pl_auto_pipeline.py` runs every 30 minutes: syncs FPL scores $\to$ updates Supabase $\to$ scores user predictions $\to$ updates Elo/form $\to$ re-predicts scheduled fixtures $\to$ updates `pl_simulation_results`.
3. **Backend Serving Layer (FastAPI Port 8001):**
   - Clean endpoint schema matching frontend requirements.
   - Dynamic FPL-03 optimizer returning genuine weekly squads, transfers, captain picks, and chip plans for 2026-27.
   - Clean public model versioning: `ennovera-pl-v1.0` and `ennovera-fantasy-v1.0`.
4. **Proxy & Routing (VPS Nginx):**
   - Forward `/api/v1/` to `http://127.0.0.1:8001` with proper headers.
   - Keep port 8000 intact for legacy WC2026.
5. **Frontend (Next.js 14 App Router on Vercel):**
   - Merge and polish `feature/pl-fpl-integration` into `main`.
   - Build dynamic Fantasy AI interface (Pitch view, transfer recommendations, captain rationale, chip planner).
   - Build PL League Table with Monte Carlo probability bars.
   - Preserve complete English & Kurdish Sorani localization.

---

## 23. Exact Implementation Sequence After Approval

```
PHASE 1: Git & State Backup
  ├── Create `archive/pre-takeover-snapshot` in all 3 repos.
  └── Commit and push all untracked research & local files.

PHASE 2: Supabase Schema & Canonical State
  ├── Create `pl_simulation_results` table in Supabase.
  └── Run initial 10,000 Monte Carlo league simulation and populate table.

PHASE 3: Backend & API Stabilization (ennovera-pl)
  ├── Refactor `pl_service.py` for live 2026-27 fixtures and Supabase sync.
  ├── Connect dynamic FPL-03 optimizer in `fpl_service.py` (replacing hardcoded squad).
  ├── Align route paths (`/predictions`, `/table`, `/squad`, `/players`, `/transfers`, `/captain`).
  └── Sanitize public model versions to `ennovera-pl-v1.0` / `ennovera-fantasy-v1.0`.

PHASE 4: VPS Nginx Routing & Deployment
  ├── Add `/api/v1/` reverse proxy block in `/etc/nginx/sites-enabled/default`.
  ├── Verify ports 80, 8000, 8001 and curl all public endpoints.
  └── Verify 30-minute cron pipeline execution.

PHASE 5: Frontend Build & Polish (innovera-wc2026-frontend)
  ├── Implement `/fantasy` (Interactive Pitch, 15-player squad, xP badges, transfers, captain).
  ├── Implement `/table` (Live standings + Monte Carlo champion/top4/relegation %).
  ├── Wire Next.js rewrites to live VPS Nginx proxy.
  └── Verify Kurdish RTL & English translations.

PHASE 6: Verification, Staging & Production Deployment
  ├── End-to-end integration tests (predictions, voting, fantasy, leaderboard).
  ├── Merge `feature/pl-fpl-integration` to `main` and deploy to Vercel (`aifootballp.com`).
  └── Activate prospective 2026-27 tracking log.
```
