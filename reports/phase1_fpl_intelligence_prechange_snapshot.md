# ENNOVERA FOOTBALL INTELLIGENCE PROGRAM — PHASE 1
## Pre-Change System Snapshot & Baseline Configuration

**Timestamp:** 2026-08-27T15:10:00+03:00  
**Branch:** `feature/fpl-intelligence-phase1`  
**Base Commit:** `ba9101d2bd2076f2d13e08a48837f24b5535338d`  
**Working Tree State:** Clean / Dedicated Research Feature Branch  
**Frozen GW2 Production Plan SHA256:** `a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e` (VERIFIED IMMUTABLE)

---

### 1. Production Service Paths & Architecture

- **Live FPL Service:** `app/services/fpl_service.py`
- **Live Ingestor Layer:** `app/services/fpl_ingestor.py`
- **Live Linear Programming Optimizer:** `app/services/fpl_optimizer.py`
- **Temporal Governance Module:** `app/services/temporal_governance.py`
- **Live Shadow xP Module:** `app/services/fpl_xp_model.py`
- **Production API Route:** `app/api/v1/fantasy.py` (FastAPI on port 8001)
- **Production Frontend Routes:** `frontend/src/app/fantasy/page.tsx` & Next.js route handlers `app/api/fpl/*/route.ts`
- **Frozen Prospective Snapshot:** `data/live_snapshots/2026-27/GW02/`

---

### 2. Established Baselines to Freeze

1. **Historical FPL-03 2025-26 Benchmark:** 2,151 pts (1,980 base + 171 chips)
2. **Current Live Heuristic:** base_pts = 0.70 * form + 0.30 * (total_points/38)
3. **Corrected Shadow Shrinkage Prototype:** Projected 64.8 pts | Captain: Haaland (7.4) | Vice: Palmer (6.5) | Chip: None (SAVE)
4. **Official Prospective Record:** Formally begins at GW2. Frozen GW2 plan is permanently immutable.
