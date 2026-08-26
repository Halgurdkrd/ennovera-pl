# ENNOVERA PL + FPL — Production Frontend API Handoff Contract (v2.0)
**Audience:** Claude Code / Claude Chat (Frontend Integration Lead)  
**Status:** **AUTHORITATIVE PRODUCTION SPECIFICATION (VERIFIED & LIVE)**  
**Version:** Ennovera PL v1.0 (`CORE_BASE`) + FPL v3.0 (`FPL-03`)

---

## 1. Hosting Architecture & Base URLs

### **A. Public API Base URL (Frontend / Browser Target)**
- **Public Production Endpoint:** `https://innovera-wc2026-api.hf.space` (or via reverse proxy on VPS `http://72.62.35.32/api/v1/`)
- **Local Development URL:** `http://localhost:8001`

### **B. Internal VPS Deployment Port**
- **Service Name:** `ennovera-pl.service`
- **Internal Port:** `http://127.0.0.1:8001` (Separate from WC2026 on port `8000`)
- **Service Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8001`

### **C. Nginx Reverse Proxy Block (For VPS 72.62.35.32)**
```nginx
# Add to /etc/nginx/sites-available/default (or appropriate server block):
location /api/v1/pl/ {
    proxy_pass http://127.0.0.1:8001/api/v1/pl/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location /api/v1/fpl/ {
    proxy_pass http://127.0.0.1:8001/api/v1/fpl/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location /health {
    proxy_pass http://127.0.0.1:8001/health;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 2. API Endpoints Specification

### 1. Health & Model Integrity Check
- **`GET /health`**
- **Status:** `200 OK`
- **Real Response:**
```json
{
  "status": "ok",
  "pl_model_loaded": true,
  "fpl_model_loaded": true,
  "version": "1.0.0",
  "model_architecture": "Ennovera PL (CORE_BASE) + FPL (FPL-03)"
}
```

---

### 2. Premier League Match Fixtures & Predictions
- **`GET /api/v1/pl/fixtures?gw={gw}&season={season}`**
- **Query Parameters:**
  - `gw` (int, default: `1`, range: `1-38`)
  - `season` (string, default: `"2025-26"`)
- **Real Response (`200 OK`):**
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
    "generated_at": "2026-08-26T18:48:56.120000Z",
    "data_cutoff": "Pre-match lineup confirmation / 1 hour before kickoff"
  }
]
```

---

### 3. FPL Master Gameweek Plan
- **`GET /api/v1/fpl/gameweek/plan?gw={gw}&season={season}`**
- **Query Parameters:**
  - `gw` (int, default: `1`, range: `1-38`)
  - `season` (string, default: `"2025-26"`)
- **Real Response (`200 OK`):**
```json
{
  "season": "2025-26",
  "gameweek": 1,
  "deadline": "2025-08-15T17:30:00Z",
  "model_version": "FPL-03 (Multi-Head xP + Captain Specialist + 8-Chip Manager)",
  "data_cutoff": "Official FPL Gameweek Deadline (90 mins prior to first kickoff)",
  "generated_at": "2026-08-26T18:48:56.135000Z",
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
      "expected_minutes": 90.0,
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
      "expected_minutes": 89.0,
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
      "expected_minutes": 0.0,
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
      "reason": "Transfers out Marcus Rashford for Phil Foden on positive 3-GW fixture swing."
    }
  ],
  "chip_recommendation": {
    "action": "SAVE",
    "chip_name": null,
    "expected_incremental_gain": 0.0,
    "reason": "Holding chip reservation value for future high-leverage gameweek."
  },
  "available_chips": [
    "wildcard_1",
    "free_hit_1",
    "bench_boost_1",
    "triple_captain_1"
  ]
}
```

---

### 4. FPL Recommended Transfers
- **`GET /api/v1/fpl/transfers/recommended?gw={gw}&season={season}`**
- **Real Response (`200 OK`):**
```json
[
  {
    "player_out": "Marcus Rashford",
    "player_in": "Phil Foden",
    "expected_gain": 6.8,
    "free_transfers_used": 1,
    "hit_points": 0,
    "bank_after": 0.5,
    "reason": "Transfers out Marcus Rashford for Phil Foden on positive 3-GW fixture swing."
  }
]
```

---

### 5. FPL Captain Specialist
- **`GET /api/v1/fpl/captain/recommended?gw={gw}&season={season}`**
- **Real Response (`200 OK`):**
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
  "selection_rationale": "Erling Haaland maximizes combined mean xP (8.6) and haul probability (52%) with penalty responsibilities."
}
```

---

### 6. FPL Chip Regulations & Status
- **`GET /api/v1/fpl/chips/status?current_gw={gw}&season={season}`**
- **Real Response (`200 OK`):**
```json
[
  {
    "chip_id": "wildcard_1",
    "name": "Wildcard 1",
    "available": true,
    "used": false,
    "status": "AVAILABLE",
    "target_gw": 8,
    "expected_incremental_value": 34.0,
    "reason": "Optimal window for Wildcard 1 at GW8 (Window: GW1-19)."
  },
  {
    "chip_id": "wildcard_2",
    "name": "Wildcard 2",
    "available": false,
    "used": false,
    "status": "LOCKED",
    "target_gw": null,
    "expected_incremental_value": 0.0,
    "reason": "Optimal window for Wildcard 2 at GW28 (Window: GW20-38)."
  }
]
```

---

## 3. Deployment Instructions for Claude Code on VPS 72.62.35.32

1. **Pull Latest Master/Main in `ennovera-pl`:**
   ```bash
   cd /path/to/ennovera-pl
   git pull origin main
   ```
2. **Install Serving Requirements:**
   ```bash
   pip install fastapi uvicorn pydantic scipy numpy pandas scikit-learn
   ```
3. **Start Systemd Service (`/etc/systemd/system/ennovera-pl.service`):**
   ```ini
   [Unit]
   Description=Ennovera Premier League and FPL Serving Layer
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/path/to/ennovera-pl
   ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
4. **Enable & Start Service:**
   ```bash
   systemctl daemon-reload
   systemctl enable ennovera-pl
   systemctl start ennovera-pl
   ```
5. **Verify Nginx Reverse Proxy Reload:**
   ```bash
   nginx -t && systemctl reload nginx
   ```
