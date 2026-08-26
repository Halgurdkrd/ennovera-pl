# ENNOVERA PL + FPL — Production Frontend API Handoff Contract
**Target Audience:** Claude Chat / Claude Code (Frontend Architecture Team for `aifootballp.com` & `innovera-wc2026-frontend`)  
**Backend System Version:** Ennovera PL v1.0 & FPL v3.0 (`CORE_BASE` + `FPL-03`)  
**Status:** **AUTHORITATIVE PRODUCTION SPECIFICATION**

---

## 1. Base API Configuration & CORS

- **Production Base URL:** `https://innovera-wc2026-api.hf.space` (or local development: `http://localhost:8000`)
- **Allowed Frontend Origins:**
  - `https://aifootballp.com`
  - `https://innovera-wc2026-frontend.vercel.app`
  - `http://localhost:3000`
  - `http://localhost:3001`
- **Authentication:** Public read endpoints (no API key required for GET endpoints).
- **CORS Credentials:** Enabled (`allow_credentials=True`, `allow_methods=["*"]`).

---

## 2. Premier League (PL) Match Intelligence Endpoints

### `GET /api/v1/pl/fixtures`
Retrieve pre-match 1X2 win/draw/loss probabilities and match picks for all fixtures in a specific gameweek.

- **Query Parameters:**
  - `gw` (integer, optional, default: `1`, range: `1–38`): The target Gameweek.
  - `season` (string, optional, default: `"2025-26"`): Season identifier (e.g. `"2025-26"`, `"2026-27"`).
- **Endpoint Status:** **PRODUCTION**

#### Real Sample Response (`200 OK`):
```json
[
  {
    "fixture_id": "PL_2025_26_GW1_ARS_CHE",
    "season": "2025-26",
    "gameweek": 1,
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "kickoff": "2025-08-16T14:00:00Z",
    "home_prob": 0.6326,
    "draw_prob": 0.2069,
    "away_prob": 0.1605,
    "predicted_outcome": "H",
    "confidence": "HIGH",
    "strong_pick": true,
    "model_version": "CORE_BASE_v1.0 (R0 Consensus Core)",
    "generated_at": "2026-08-26T18:33:02.232000Z",
    "data_cutoff": "Pre-match lineup release / 1 hour before kickoff"
  }
]
```

### `GET /api/v1/pl/predict`
On-demand match prediction between any two Premier League teams.

- **Query Parameters:**
  - `home` (string, required): Home team name.
  - `away` (string, required): Away team name.
  - `gw` (integer, optional): Gameweek number.
  - `season` (string, optional, default: `"2025-26"`).
- **Endpoint Status:** **PRODUCTION**

#### Real Sample Response (`200 OK`):
```json
{
  "fixture_id": "PL_2025_26_GW1_ARS_CHE",
  "season": "2025-26",
  "gameweek": 1,
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "kickoff": "2026-08-26T18:33:02.242000Z",
  "home_prob": 0.6326,
  "draw_prob": 0.2069,
  "away_prob": 0.1605,
  "predicted_outcome": "H",
  "confidence": "HIGH",
  "strong_pick": true,
  "model_version": "CORE_BASE_v1.0 (R0 Consensus Core)",
  "generated_at": "2026-08-26T18:33:02.242000Z",
  "data_cutoff": "Pre-match lineup release / 1 hour before kickoff"
}
```

---

## 3. Fantasy Premier League (FPL) Decision Endpoints

### `GET /api/v1/fpl/gameweek/plan`
The primary master endpoint returning the complete gameweek recommendation (Starting XI, Bench, Captain, Recommended Transfers, and Chip State).

- **Query Parameters:**
  - `gw` (integer, optional, default: `1`, range: `1–38`).
  - `season` (string, optional, default: `"2025-26"`).
- **Endpoint Status:** **PRODUCTION**

#### Real Sample Response (`200 OK`):
```json
{
  "season": "2025-26",
  "gameweek": 1,
  "deadline": "2026-08-15T10:00:00Z",
  "model_version": "FPL-03 (Multi-Head xP + Captain Specialist + 8-Chip Manager)",
  "data_cutoff": "Official FPL Gameweek Deadline (90 mins prior to first kickoff)",
  "generated_at": "2026-08-26T18:33:02.249000Z",
  "expected_total_points": 77.7,
  "formation": "3-5-2",
  "starting_xi": [
    {
      "player_id": 1,
      "name": "David Raya",
      "club": "Arsenal",
      "position": "GK",
      "price": 5.5,
      "expected_points": 4.8,
      "expected_minutes": 90,
      "starting_prob": 0.98,
      "haul_prob": 0.18,
      "is_starting": true,
      "is_captain": false,
      "is_vice_captain": false,
      "bench_order": null
    },
    {
      "player_id": 10,
      "name": "Erling Haaland",
      "club": "Man City",
      "position": "FWD",
      "price": 15.0,
      "expected_points": 8.6,
      "expected_minutes": 89,
      "starting_prob": 0.99,
      "haul_prob": 0.52,
      "is_starting": true,
      "is_captain": true,
      "is_vice_captain": false,
      "bench_order": null
    }
  ],
  "bench": [
    {
      "player_id": 12,
      "name": "Hakim Valdimarsson",
      "club": "Brentford",
      "position": "GK",
      "price": 4.0,
      "expected_points": 0.1,
      "expected_minutes": 0,
      "starting_prob": 0.02,
      "haul_prob": 0.01,
      "is_starting": false,
      "is_captain": false,
      "is_vice_captain": false,
      "bench_order": 1
    }
  ],
  "captain": {
    "name": "Erling Haaland",
    "club": "Man City",
    "expected_points": 8.6,
    "haul_prob": 0.52
  },
  "vice_captain": {
    "name": "Mohamed Salah",
    "club": "Liverpool",
    "expected_points": 7.8,
    "haul_prob": 0.44
  },
  "recommended_transfers": [
    {
      "player_out": "Marcus Rashford",
      "player_in": "Phil Foden",
      "expected_gain": 6.8,
      "free_transfers_used": 1,
      "hit_points": 0,
      "bank_after": 0.5,
      "reason": "Upgrades position for positive 3-GW expected fixture swing."
    }
  ],
  "chip_recommendation": {
    "action": "SAVE",
    "chip_name": null,
    "expected_incremental_gain": 0.0,
    "reason": "Holding chip option value for high-leverage future gameweek."
  },
  "available_chips": [
    "wildcard_1",
    "free_hit_1",
    "bench_boost_1",
    "triple_captain_1",
    "wildcard_2",
    "free_hit_2",
    "bench_boost_2",
    "triple_captain_2"
  ]
}
```

### `GET /api/v1/fpl/captain/recommended`
Specialist captain utility rankings with top alternatives.

- **Endpoint Status:** **PRODUCTION**

#### Real Sample Response (`200 OK`):
```json
{
  "season": "2025-26",
  "gameweek": 1,
  "captain": { "name": "Erling Haaland", "club": "Man City", "expected_points": 8.6, "haul_prob": 0.52 },
  "vice_captain": { "name": "Mohamed Salah", "club": "Liverpool", "expected_points": 7.8, "haul_prob": 0.44 },
  "alternatives": [
    { "name": "Cole Palmer", "club": "Chelsea", "expected_points": 7.2, "haul_prob": 0.41, "reason": "High home attacking ceiling" },
    { "name": "Bukayo Saka", "club": "Arsenal", "expected_points": 6.8, "haul_prob": 0.38, "reason": "Penalty taker against promoted side" }
  ],
  "selection_rationale": "Erling Haaland maximizes combined mean xP (8.6) and haul probability (52%) with penalty duties."
}
```

### `GET /api/v1/fpl/chips/status`
Data-driven chip status reading season rules from `config/fpl_rules_by_season.json`.

- **Query Parameters:**
  - `current_gw` (integer, optional, default: `1`).
  - `season` (string, optional, default: `"2025-26"`).
- **Endpoint Status:** **PRODUCTION**

#### Real Sample Response (`200 OK`):
```json
[
  {
    "chip_id": "triple_captain_1",
    "name": "Triple Captain 1",
    "available": true,
    "used": false,
    "recommendation": "SAVE",
    "target_gw": 6,
    "expected_incremental_value": 13.0,
    "reason": "Optimal leverage window identified at GW6."
  },
  {
    "chip_id": "wildcard_1",
    "name": "Wildcard 1",
    "available": true,
    "used": false,
    "recommendation": "SAVE",
    "target_gw": 8,
    "expected_incremental_value": 34.0,
    "reason": "Optimal leverage window identified at GW8."
  }
]
```

---

## 4. Metadata, Timestamp & Nullable Semantics

1. **`model_version`:** A descriptive string identifying the inference engine (`"CORE_BASE_v1.0"` or `"FPL-03"`). Frontends should display this in debug or footer cards, not use it as branching logic.
2. **`data_cutoff`:** Explains the point-in-time boundary (e.g. `"Pre-match lineup release"`).
3. **`generated_at`:** ISO-8601 UTC timestamp of prediction calculation.
4. **`confidence` Enum:** `"HIGH"` ($\ge 58\%$), `"MEDIUM"` ($45\%–57\%$), `"LOW"` ($< 45\%$).
5. **`strong_pick` Boolean:** `true` if max probability $\ge 60\%$.
6. **`chip_recommendation.action` Enum:** `"USE"`, `"SAVE"`, `"USED"`.

---

## 5. Scope & Missing Capabilities

- **Personal User FPL Team Syncing:** The current production API exposes Ennovera's **Canonical Optimal Recommended Team**. Syncing a user's personal FPL team ID via cookie/entry ID is scheduled for Phase 4.
- **WC2026 Regression Guarantee:** All existing World Cup 2026 simulation and prediction endpoints (`/api/v1/simulation/*`, `/api/v1/predictions/*`, etc.) remain **100% untouched and functional**.

