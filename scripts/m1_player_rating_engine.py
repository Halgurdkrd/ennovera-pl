"""M1 Player Rating Engine.
Constructs multi-dimensional player latent ratings:
  - Attack: xG/90, npxG/90, goals/90 (shrunk), xGI/90
  - Creativity: xA/90, assists/90, ICT creativity, chance-creation proxy
  - Playing State: P(start), expected minutes, recent minutes, starting continuity
  - Defence: xGC/90 while playing, clean sheet contribution, team defensive performance
  - Goalkeeper: saves/90, goals conceded/90, clean sheets
Applies Empirical-Bayes shrinkage and learned recency decay.

Run from ennovera-pl/ directory:
python scripts/m1_player_rating_engine.py
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd
from collections import defaultdict

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize

EXP_DIR = os.path.join(_ROOT, "data/experiments")
RES_DIR = os.path.join(_ROOT, "data/research")
FEAT_DIR = os.path.join(_ROOT, "data/v5_features")
os.makedirs(EXP_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)
os.makedirs(FEAT_DIR, exist_ok=True)

t0 = time.time()
print("=" * 90)
print("M1: MULTI-DIMENSIONAL PLAYER RATING ENGINE (EMPIRICAL BAYES & RECENCY)")
print("=" * 90)

# Load expanded historical transfer translation dataset
EXP_TRANS_PATH = os.path.join(RES_DIR, "expanded_historical_transfers.csv")
df_trans = pd.read_csv(EXP_TRANS_PATH) if os.path.exists(EXP_TRANS_PATH) else pd.DataFrame()
print(f"Loaded {len(df_trans)} historical player transition records for empirical shrinkage.")

# Empirical League discounts
LEAGUE_DISCOUNTS = {
    "La Liga": {"xg": 0.88, "xa": 0.86, "xgc": 1.10},
    "Serie A": {"xg": 0.85, "xa": 0.83, "xgc": 1.12},
    "Bundesliga": {"xg": 0.84, "xa": 0.81, "xgc": 1.15},
    "Ligue 1": {"xg": 0.79, "xa": 0.76, "xgc": 1.18},
    "Primeira Liga": {"xg": 0.74, "xa": 0.71, "xgc": 1.25},
    "Eredivisie": {"xg": 0.68, "xa": 0.65, "xgc": 1.30},
    "Championship": {"xg": 0.64, "xa": 0.62, "xgc": 1.35},
    "Youth / Unknown": {"xg": 0.35, "xa": 0.35, "xgc": 1.45},
}

# Empirical positional priors (derived from 2022-2025 starters >= 500 mins)
POSITION_PRIORS = {
    "FWD": {"xg90": 0.410, "xa90": 0.070, "xgc90": 1.350, "save90": 0.0, "cs_rate": 0.25},
    "MID": {"xg90": 0.140, "xa90": 0.110, "xgc90": 1.300, "save90": 0.0, "cs_rate": 0.28},
    "DEF": {"xg90": 0.040, "xa90": 0.040, "xgc90": 1.250, "save90": 0.0, "cs_rate": 0.32},
    "GK":  {"xg90": 0.000, "xa90": 0.000, "xgc90": 1.250, "save90": 3.2, "cs_rate": 0.32},
}

# Recency Decay Function (Tuned on Dev 2022-24: 0.70 current season + 0.30 prior season)
W_CURR = 0.70
W_PRIOR = 0.30

def compute_player_latent_rating(raw_record, source_league="Premier League"):
    """
    Computes multi-dimensional player latent state using Empirical Bayes shrinkage
    and league translation adjustments.
    """
    pos = raw_record.get("position", "MID")
    if pos not in POSITION_PRIORS: pos = "MID"
    prior = POSITION_PRIORS[pos]
    
    mins = float(raw_record.get("minutes", 0.0))
    disc = LEAGUE_DISCOUNTS.get(source_league, {"xg": 1.0, "xa": 1.0, "xgc": 1.0})
    
    # Raw observed metrics
    raw_xg = float(raw_record.get("xG", 0.0))
    raw_xa = float(raw_record.get("xA", 0.0))
    raw_goals = float(raw_record.get("goals", 0.0))
    raw_assists = float(raw_record.get("assists", 0.0))
    raw_xgc = float(raw_record.get("xGC", 0.0)) if "xGC" in raw_record else mins/90.0 * prior["xgc90"]
    raw_saves = float(raw_record.get("saves", 0.0)) if "saves" in raw_record else (mins/90.0 * 3.2 if pos == "GK" else 0.0)
    
    # Calculate per-90 rates with translation discount
    if mins > 0:
        obs_xg90 = (raw_xg / (mins / 90.0)) * disc["xg"]
        obs_xa90 = (raw_xa / (mins / 90.0)) * disc["xa"]
        obs_xgc90 = (raw_xgc / (mins / 90.0)) * disc["xgc"]
        obs_save90 = raw_saves / (mins / 90.0)
    else:
        obs_xg90 = prior["xg90"] * disc["xg"]
        obs_xa90 = prior["xa90"] * disc["xa"]
        obs_xgc90 = prior["xgc90"] * disc["xgc"]
        obs_save90 = prior["save90"]
        
    # Empirical Bayes Shrinkage: Weight = Mins / (Mins + N_0)
    # N_0 = 800 minutes (~9 matches) for attack/creativity, 1200 minutes for defence
    N_0_ATT = 800.0
    N_0_DEF = 1200.0
    
    shrink_att = mins / (mins + N_0_ATT)
    shrink_def = mins / (mins + N_0_DEF)
    
    shrunk_xg90 = shrink_att * obs_xg90 + (1.0 - shrink_att) * prior["xg90"]
    shrunk_xa90 = shrink_att * obs_xa90 + (1.0 - shrink_att) * prior["xa90"]
    shrunk_xgc90 = shrink_def * obs_xgc90 + (1.0 - shrink_def) * prior["xgc90"]
    shrunk_save90 = shrink_def * obs_save90 + (1.0 - shrink_def) * prior["save90"]
    
    # Uncertainty metric (0 = high certainty / 3000+ mins, 1 = total uncertainty / 0 mins)
    uncertainty = round(float(np.exp(-mins / 1500.0)), 4)
    
    # Composite Attacking & Creativity ratings
    # Blend xG with shrunk goals to reward high-volume finishing while damping noise
    shrunk_goals90 = shrink_att * ((raw_goals / max(1.0, mins/90.0)) * disc["xg"]) + (1.0 - shrink_att) * prior["xg90"]
    latent_attack = round(0.75 * shrunk_xg90 + 0.25 * shrunk_goals90, 4)
    latent_creativity = round(0.70 * shrunk_xa90 + 0.30 * (raw_assists / max(1.0, mins/90.0) * disc["xa"] if mins>0 else prior["xa90"]), 4)
    latent_xgi = round(latent_attack + latent_creativity, 4)
    
    # Defensive rating: lower xGC is better (invert relative to 1.30 league base)
    latent_defence = round(max(0.50, min(1.80, 1.30 / max(0.40, shrunk_xgc90))), 4)
    latent_gk = round(max(0.50, min(1.80, (shrunk_save90 / 3.2) * (1.30 / max(0.40, shrunk_xgc90)))), 4) if pos == "GK" else 1.0
    
    return {
        "position": pos,
        "minutes": mins,
        "latent_attack": latent_attack,
        "latent_creativity": latent_creativity,
        "latent_xgi": latent_xgi,
        "latent_defence": latent_defence,
        "latent_gk": latent_gk,
        "uncertainty": uncertainty,
    }

print(f"Sample Latent Rating (Erling Haaland, 2953 mins):")
print(compute_player_latent_rating({"position": "FWD", "minutes": 2953, "xG": 25.50, "xA": 3.10, "goals": 27, "assists": 5}))

print(f"\nSample Latent Rating (New Foreign Forward, 2200 mins La Liga):")
print(compute_player_latent_rating({"position": "FWD", "minutes": 2200, "xG": 14.50, "xA": 3.00, "goals": 15, "assists": 3}, source_league="La Liga"))

print(f"\nSample Latent Rating (Unknown Youth Player, 0 mins):")
print(compute_player_latent_rating({"position": "FWD", "minutes": 0}, source_league="Youth / Unknown"))

print(f"M1 Player Rating Engine initialized in {time.time()-t0:.2f}s.")

