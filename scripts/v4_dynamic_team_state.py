"""Phase 3, 4, 5, 6: Dynamic Team State & Temporal Memory Decay Engine.
Constructs leak-free dynamic attacking and defensive states with exponential memory decay,
opponent-adjustments, historical priors, squad transition weighting, and uncertainty estimation.

Run from ennovera-pl/ directory:
python scripts/v4_dynamic_team_state.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize

RAW_FPL_DIR = os.path.join(_ROOT, "data/raw/fpl_full/data")
DATA_DIR = os.path.join(_ROOT, "data/processed")
V4_DIR = os.path.join(_ROOT, "data/v4_features")
os.makedirs(V4_DIR, exist_ok=True)

# Load transition indices
trans_df = pd.read_csv(os.path.join(V4_DIR, "squad_transition_indices.csv"))
trans_map = {(r["season"], r["team"]): r["transition_index"] for _, r in trans_df.iterrows()}

def build_team_match_history(seasons=["2022-23", "2023-24", "2024-25", "2025-26"]):
    """Extract chronological per-match xG, xGA, goals, Elo for all teams across all seasons."""
    # Load feature dataset containing base Elo and match metadata
    base_df = pd.read_csv(os.path.join(DATA_DIR, "pl_features.csv"))
    base_df = base_df[base_df["season"].isin(seasons)].copy().sort_values(["season", "date"]).reset_index(drop=True)
    
    # Load leak-free FPL per-gameweek team aggregates
    team_gw_metrics = {}
    for s in seasons:
        gw_path = os.path.join(RAW_FPL_DIR, s, "gws/merged_gw.csv")
        if not os.path.exists(gw_path):
            continue
        gdf = pd.read_csv(gw_path, low_memory=False)
        gdf["team_name"] = gdf["team"].map(canonicalize)
        gdf["GW"] = pd.to_numeric(gdf["GW"], errors="coerce").fillna(1).astype(int)
        for col in ["expected_goals", "expected_assists", "expected_goals_conceded", "clean_sheets", "value"]:
            if col in gdf.columns:
                gdf[col] = pd.to_numeric(gdf[col], errors="coerce").fillna(0.0)
                
        for (t, gw), grp in gdf.groupby(["team_name", "GW"]):
            xg = float(grp["expected_goals"].sum()) if "expected_goals" in grp else 1.3
            xa = float(grp["expected_assists"].sum()) if "expected_assists" in grp else 1.0
            xga = float(grp["expected_goals_conceded"].mean()) if "expected_goals_conceded" in grp else 1.3
            team_gw_metrics[(s, t, gw)] = {"xg": xg, "xa": xa, "xga": xga}
            
    # Enrich matches with GW integer and dynamic states
    # Load fixtures to get official GWs
    matches_list = []
    for s in seasons:
        fix_path = os.path.join(RAW_FPL_DIR, s, "fixtures.csv")
        teams_path = os.path.join(RAW_FPL_DIR, s, "teams.csv")
        tdf = pd.read_csv(teams_path)
        id2t = {r["id"]: canonicalize(r["name"]) for _, r in tdf.iterrows()}
        
        fdf = pd.read_csv(fix_path)
        fdf["gw"] = pd.to_numeric(fdf["event"], errors="coerce").fillna(1).astype(int)
        fdf["home"] = fdf["team_h"].map(id2t)
        fdf["away"] = fdf["team_a"].map(id2t)
        
        # Match with base_df
        s_base = base_df[base_df["season"] == s].copy()
        merged_s = pd.merge(s_base, fdf[["gw", "home", "away"]], on=["home", "away"], how="left")
        merged_s["gw"] = merged_s["gw"].fillna(1).astype(int)
        merged_s["season"] = s
        matches_list.append(merged_s)
        
    full_matches = pd.concat(matches_list, ignore_index=True)
    return full_matches, team_gw_metrics

def compute_dynamic_states(half_life=6.0, prior_weight=4.0):
    """
    Computes leak-free dynamic attack/defence states for all matches.
    half_life: half-life in matches for exponential memory decay
    prior_weight: equivalent match weight for long-term historical prior (scaled by 1 - transition)
    """
    matches_df, team_gw_metrics = build_team_match_history()
    decay_lambda = np.log(2.0) / half_life
    
    # Store match-by-match states
    home_att_list, home_def_list, away_att_list, away_def_list = [], [], [], []
    home_unc_list, away_unc_list = [], []
    
    # Chronological tracking per season
    for s, s_matches in matches_df.groupby("season", sort=False):
        # Team match history within this season: list of (gw, xg_for, xga_conceded, opp_team)
        team_history = {t: [] for t in set(s_matches["home"]) | set(s_matches["away"])}
        
        for idx, row in s_matches.iterrows():
            gw = int(row["gw"])
            h_team = row["home"]
            a_team = row["away"]
            
            # Transition indices for both teams
            tau_h = trans_map.get((s, h_team), 0.3)
            tau_a = trans_map.get((s, a_team), 0.3)
            
            # Historical priors derived from pre-match Elo
            elo_h = row["home_elo"]
            elo_a = row["away_elo"]
            
            # Normalized baseline ratings centered at 1.0 (1500 Elo = 1.0)
            prior_att_h = float(elo_h / 1500.0) ** 0.8
            prior_def_h = float(1500.0 / elo_h) ** 0.8
            prior_att_a = float(elo_a / 1500.0) ** 0.8
            prior_def_a = float(1500.0 / elo_a) ** 0.8
            
            # Function to calculate decayed dynamic state from completed matches (GW < target_gw)
            def get_state(team, prior_att, prior_def, tau):
                hist = [m for m in team_history[team] if m["gw"] < gw]
                n_played = len(hist)
                
                # Base prior weight reduced by transition index (high turnover = weak historical prior)
                eff_prior_w = max(0.5, prior_weight * (1.0 - 0.7 * tau))
                
                if n_played == 0:
                    att = prior_att
                    def_ = prior_def
                    # Initial uncertainty high, scaled by transition index
                    unc = 0.30 * (1.0 + 1.2 * tau)
                else:
                    # Exponential decay weights based on match age
                    weights = [np.exp(-decay_lambda * (n_played - 1 - i)) for i in range(n_played)]
                    sum_w = sum(weights)
                    
                    # Decayed observed attack & defence
                    obs_att = sum(weights[i] * hist[i]["xg_for"] for i in range(n_played)) / sum_w
                    obs_def = sum(weights[i] * hist[i]["xga_conc"] for i in range(n_played)) / sum_w
                    
                    # Normalized to league average 1.35
                    obs_att_norm = obs_att / 1.35
                    obs_def_norm = obs_def / 1.35
                    
                    # Blend prior with decayed observations
                    att = (eff_prior_w * prior_att + sum_w * obs_att_norm) / (eff_prior_w + sum_w)
                    def_ = (eff_prior_w * prior_def + sum_w * obs_def_norm) / (eff_prior_w + sum_w)
                    
                    # Uncertainty decays as matches accumulate in season
                    unc = (0.30 * (1.0 + 1.2 * tau)) * np.exp(-0.08 * n_played) + 0.08
                    
                return att, def_, unc
                
            att_h, def_h, unc_h = get_state(h_team, prior_att_h, prior_def_h, tau_h)
            att_a, def_a, unc_a = get_state(a_team, prior_att_a, prior_def_a, tau_a)
            
            home_att_list.append(att_h)
            home_def_list.append(def_h)
            away_att_list.append(att_a)
            away_def_list.append(def_a)
            home_unc_list.append(unc_h)
            away_unc_list.append(unc_a)
            
            # Post-match record update (leak-free: recorded only after match is evaluated)
            gw_h_stat = team_gw_metrics.get((s, h_team, gw), {"xg": 1.35, "xga": 1.35})
            gw_a_stat = team_gw_metrics.get((s, a_team, gw), {"xg": 1.35, "xga": 1.35})
            
            team_history[h_team].append({
                "gw": gw,
                "xg_for": gw_h_stat["xg"],
                "xga_conc": gw_h_stat["xga"],
            })
            team_history[a_team].append({
                "gw": gw,
                "xg_for": gw_a_stat["xg"],
                "xga_conc": gw_a_stat["xga"],
            })
            
    matches_df["v4_home_att"] = home_att_list
    matches_df["v4_home_def"] = home_def_list
    matches_df["v4_away_att"] = away_att_list
    matches_df["v4_away_def"] = away_def_list
    matches_df["v4_home_unc"] = home_unc_list
    matches_df["v4_away_unc"] = away_unc_list
    
    out_csv = os.path.join(V4_DIR, "v4_dynamic_team_states.csv")
    matches_df.to_csv(out_csv, index=False)
    print(f"Generated dynamic team states for {len(matches_df)} matches -> {out_csv}")
    return matches_df

if __name__ == "__main__":
    compute_dynamic_states()

