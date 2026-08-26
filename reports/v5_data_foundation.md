# Ennovera PL Predictor — V5 Data Foundation & Shared FPL Intelligence Architecture

**Status:** Research Specification & Data Architecture Design (No Model Training Executed)  
**Target Next Phase:** V5 Lineup-Conditioned Team State & Unified FPL Engine

---

## 1. The V5 Unified Intelligence Concept

In V1–V4, team strength was modeled purely at the club aggregate level:
$$\text{Club History} \longrightarrow \text{Dynamic Rating} \longrightarrow \text{Match Prediction}$$

In **V5**, the football ontology is restructured from the bottom up so that **Match Prediction** and **Fantasy Premier League (FPL) Player Prediction** share the exact same underlying player/tactical intelligence engine:

```
                  ┌───────────────────────────────────────────────┐
                  │          PLAYER STATE INTELLIGENCE            │
                  │  (Rolling xG/90, xA/90, ICT, Price, Form)     │
                  └───────────────────────┬───────────────────────┘
                                          │
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │           AVAILABILITY & LINEUP ENGINE        │
                  │ (Injury Status, Starting Prob, Exp. Minutes)  │
                  └───────┬───────────────────────────────┬───────┘
                          │                               │
                          ▼                               ▼
       ┌────────────────────────────────────┐   ┌────────────────────────────────────┐
       │   LINEUP-ADJUSTED TEAM STRENGTH    │   │      FPL PLAYER PREDICTOR          │
       │ (Starting XI Attack / Defence Mass)│   │  (xP, Clean Sheet %, Goal/Assist %)│
       └──────────────────┬─────────────────┘   └────────────────────────────────────┘
                          │
                          ▼
       ┌────────────────────────────────────┐
       │     PL MATCH PREDICTOR (1X2/Score) │
       └────────────────────────────────────┘
```

---

## 2. Player State Pre-Kickoff Schema

For every active Premier League player before each gameweek $t$, the system constructs a leak-free feature vector representing information available strictly **prior to kickoff**:

```sql
CREATE TABLE player_prekick_state (
    player_id VARCHAR(64) NOT NULL,
    player_name VARCHAR(128) NOT NULL,
    team VARCHAR(64) NOT NULL,
    position VARCHAR(16) NOT NULL, -- GKP, DEF, MID, FWD
    
    -- Availability & Selection
    injury_status VARCHAR(64),     -- Available, Doubtful (75%/50%/25%), Injured (0%), Suspended
    starting_probability FLOAT,    -- P(starts in Starting XI) in [0, 1]
    expected_minutes FLOAT,        -- E[minutes | available] in [0, 90]
    
    -- Rolling Dynamic Performance (Leak-Free Past Matches Only)
    rolling_xG_per90 FLOAT,        -- Exponentially decayed xG per 90 mins
    rolling_xA_per90 FLOAT,        -- Exponentially decayed xA per 90 mins
    rolling_xGI_per90 FLOAT,       -- Expected goal involvements per 90
    rolling_xGC_per90 FLOAT,       -- Expected goals conceded per 90 (DEF/GKP)
    rolling_ict_index FLOAT,       -- Influence, Creativity, Threat index
    rolling_minutes_share FLOAT,   -- Fraction of team minutes played over last 5 matches
    
    -- Tactical Roles & Valuation
    is_penalty_taker BOOLEAN,
    is_corner_taker BOOLEAN,
    is_direct_freekick_taker BOOLEAN,
    fpl_price FLOAT,               -- Current market price in millions
    fpl_selected_pct FLOAT,        -- Current ownership percentage
    
    -- Attacking & Defensive Player Contribution Ratings
    player_att_rating FLOAT,       -- Individual offensive power rating
    player_def_rating FLOAT,       -- Individual defensive power rating
    
    -- Metadata
    manager_id VARCHAR(64),
    data_cutoff_timestamp TIMESTAMP NOT NULL
);
```

---

## 3. Lineup-Conditioned Team Strength Conversion

Instead of treating a club name as a fixed entity, team attacking and defensive strength are dynamically aggregated from the **Starting XI profile**:

### Attacking Strength Formulation:
$$\tilde{\alpha}_{\text{team}}(t) = \sum_{i \in \text{Squad}} P(\text{Starts}_i) \cdot \left( \frac{\mathbb{E}[\text{Mins}_i]}{90} \right) \cdot \text{player\_att\_rating}_i(t)$$

### Defensive Strength Formulation:
$$\tilde{\beta}_{\text{team}}(t) = \kappa_{\text{GKP}} \cdot \text{def\_rating}_{\text{GKP}} + \sum_{j \in \text{Defenders/MIDs}} P(\text{Starts}_j) \cdot \text{player\_def\_rating}_j(t) + \text{residual\_team\_defence}$$

### Real-World Differentiation Handled Naturally:
1. **Liverpool with elite creators vs without:** When key creators (e.g. Salah, Alexander-Arnold) are absent or doubtful ($P(\text{Starts}) \to 0$), the team attack rating automatically drops proportionally to their individual creation share.
2. **Manchester City under squad/manager turnover:** High squad churn replaces proven high-xG contributors with unrated or newly integrated players, automatically raising team uncertainty $\sigma(t)$.
3. **Arsenal with stable retained XI:** 100% minutes retention maintains tight ratings and low parameter variance.

---

## 4. Manager / Regime State Architecture

Manager and tactical regime transitions are tracked using objective, non-subjective operational metrics:

```sql
CREATE TABLE manager_regime_state (
    manager_name VARCHAR(128) NOT NULL,
    team VARCHAR(64) NOT NULL,
    appointment_date DATE NOT NULL,
    matches_in_charge INT NOT NULL,
    days_since_appointment INT NOT NULL,
    is_interim BOOLEAN NOT NULL,
    
    -- Objective Performance Under Current Regime
    regime_matches_played INT NOT NULL,
    regime_rolling_xG_per_match FLOAT,
    regime_rolling_xGA_per_match FLOAT,
    prior_manager_xG_per_match FLOAT,
    prior_manager_xGA_per_match FLOAT,
    
    -- Tactical & Pressure Context (Measurable Proxies)
    formation_stability_index FLOAT,  -- Fraction of matches using primary formation
    relegation_pressure_flag BOOLEAN, -- Within 3 points of bottom 3 after GW 10
    title_race_pressure_flag BOOLEAN  -- Within 3 points of top after GW 25
);
```

---

## 5. Local Data Source Audit Matrix for V5

An audit of existing local files in `ennovera-pl/` was conducted to establish exact feature feasibility:

| Feature / Data Field | Historical Availability (2022–26) | Live Availability (2026–27) | Local Source / Location | Leak-Free? | Status / Feasibility |
|---|---|---|---|---|---|
| **Player Minutes & Starts** | **YES** (Per-GW in `merged_gw.csv`) | **YES** (FPL API `live`) | `data/raw/fpl_full/data/*/gws/` | YES | **AVAILABLE HISTORICALLY** |
| **Player xG / xA / xGI** | **YES** (Per-GW in `merged_gw.csv`) | **YES** (FPL API `live`) | `data/raw/fpl_full/data/*/gws/` | YES | **AVAILABLE HISTORICALLY** |
| **Player ICT Index** | **YES** (Influence, Creativity, Threat) | **YES** (FPL API) | `data/raw/fpl_full/data/*/gws/` | YES | **AVAILABLE HISTORICALLY** |
| **Player FPL Price & Ownership** | **YES** (Value in `merged_gw.csv`) | **YES** (FPL API `bootstrap-static`) | `data/raw/fpl_full/data/*/gws/` | YES | **AVAILABLE HISTORICALLY** |
| **GK Saves & Clean Sheets** | **YES** (Per-GW in `merged_gw.csv`) | **YES** (FPL API) | `data/raw/fpl_full/data/*/gws/` | YES | **AVAILABLE HISTORICALLY** |
| **Set-Piece / Penalty Takers** | **PARTIAL** (Penalties scored/missed) | **YES** (FPL API `set_piece_notes`) | Historical penalties derivable | YES | **DERIVABLE HISTORICALLY** |
| **Official Lineups (1-hr pre-kick)** | **NO** (Only final `starts` recorded) | **YES** (Premier League / FPL live feed) | Live matchday API feed | YES | **AVAILABLE LIVE ONLY** |
| **Pre-match Injury News & % Chance**| **NO** (Not backfilled per GW) | **YES** (`chance_of_playing_next_round`)| FPL live API `bootstrap-static` | YES | **AVAILABLE LIVE ONLY** |
| **Manager Appointment Dates** | **NO** (Not in raw tabular FPL) | **YES** (Public league records) | Managerial metadata table | YES | **REQUIRES EXTERNAL MAPPING** |
| **Pre-match Bookmaker Odds** | **YES** (Bet365 in `E0_*.csv`) | **YES** (Public odds feeds) | `data/raw/pl_history/E0_*.csv` | YES | **AVAILABLE (MARKET BENCHMARK)** |

---

## 6. Strict Separation of Pure Model vs. Market-Hybrid Prior

To maintain scientific integrity:
1. **Pure Ennovera Model:** Uses strictly football-derived data (Player State, Dynamic Team States, Starting Lineups, Tactical/Managerial States). Zero bookmaker odds are used in feature engineering or model training.
2. **Market-Hybrid Model (Future Research Only):** Investigates Bayesian updating of the Pure Ennovera posterior with market consensus odds. This will remain a completely separate research track and will not be blended into the primary Pure Ennovera architecture without explicit approval.

---

## 7. Recommended Next V5 Research Experiment

When V5 development begins, the recommended first research experiment is:
**"V5.1 — Pre-Kickoff Lineup Creator-Weighting Backtest"**
- Using historical starting XI indicators from `merged_gw.csv`, scale team attack and defence ratings by the presence of each team's top 3 xGI creators.
- Compare out-of-sample Log-Loss against the frozen V4 baseline across the 4 walk-forward seasons.

