"""Phase 5: Squad Transition / Regime Change Index Extractor.
Extracts leak-free squad turnover, minutes retention, key-creator departure, and transition uncertainty
for each team across all Premier League seasons (2022-26) using historical FPL player data.

Run from ennovera-pl/ directory:
python scripts/v4_transition_features.py
"""
import os
import sys
import json
import glob
import numpy as np
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize

RAW_FPL_DIR = os.path.join(_ROOT, "data/raw/fpl_full/data")
OUT_DIR = os.path.join(_ROOT, "data/v4_features")
os.makedirs(OUT_DIR, exist_ok=True)

SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]

def get_season_player_stats(season_str):
    """Aggregate total minutes, xG, xA, and total_points per player per team in season_str."""
    path = os.path.join(RAW_FPL_DIR, season_str, "gws/merged_gw.csv")
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path, low_memory=False)
    df["team_name"] = df["team"].map(canonicalize)
    for col in ["minutes", "expected_goals", "expected_assists", "total_points"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            
    stats = {}
    for team, t_df in df.groupby("team_name"):
        p_stats = {}
        for p_name, p_df in t_df.groupby("name"):
            p_stats[p_name] = {
                "minutes": float(p_df["minutes"].sum()),
                "xg_xa": float((p_df["expected_goals"] + p_df["expected_assists"]).sum()) if "expected_goals" in p_df else 0.0,
                "points": float(p_df["total_points"].sum()),
            }
        stats[team] = p_stats
    return stats

def compute_transition_indices():
    season_stats = {s: get_season_player_stats(s) for s in SEASONS}
    
    records = []
    # Compute transition for target seasons 2022-23, 2023-24, 2024-25, 2025-26 using S-1 as prior
    target_seasons = [("2022-23", "2021-22"), ("2023-24", "2022-23"), ("2024-25", "2023-24"), ("2025-26", "2024-25")]
    
    for s_target, s_prior in target_seasons:
        t_stats_target = season_stats[s_target]
        t_stats_prior = season_stats[s_prior]
        
        # Load teams list for target season
        t_csv = os.path.join(RAW_FPL_DIR, s_target, "teams.csv")
        teams_df = pd.read_csv(t_csv)
        teams = [canonicalize(name) for name in teams_df["name"]]
        
        for team in teams:
            is_promoted = team not in t_stats_prior
            
            if is_promoted:
                # Promoted team: maximum historical transition uncertainty
                records.append({
                    "season": s_target,
                    "team": team,
                    "is_promoted": 1.0,
                    "minutes_retention": 0.0,
                    "minutes_turnover": 1.0,
                    "creator_retention": 0.0,
                    "creator_turnover": 1.0,
                    "transition_index": 1.0,
                })
            else:
                p_curr = t_stats_target.get(team, {})
                p_prev = t_stats_prior.get(team, {})
                
                total_prev_mins = sum(p["minutes"] for p in p_prev.values())
                total_prev_xg_xa = sum(p["xg_xa"] for p in p_prev.values())
                
                # Players retained in target season
                retained_players = set(p_curr.keys()) & set(p_prev.keys())
                retained_mins = sum(p_prev[p]["minutes"] for p in retained_players)
                retained_xg_xa = sum(p_prev[p]["xg_xa"] for p in retained_players)
                
                min_ret = retained_mins / max(total_prev_mins, 1.0)
                xg_ret = retained_xg_xa / max(total_prev_xg_xa, 1.0)
                
                min_turnover = 1.0 - min_ret
                xg_turnover = 1.0 - xg_ret
                
                # Composite transition index [0.0 = completely identical, 1.0 = total rebuild]
                comp_trans = 0.5 * min_turnover + 0.5 * xg_turnover
                
                records.append({
                    "season": s_target,
                    "team": team,
                    "is_promoted": 0.0,
                    "minutes_retention": round(min_ret, 4),
                    "minutes_turnover": round(min_turnover, 4),
                    "creator_retention": round(xg_ret, 4),
                    "creator_turnover": round(xg_turnover, 4),
                    "transition_index": round(comp_trans, 4),
                })
                
    df_trans = pd.DataFrame(records)
    out_csv = os.path.join(OUT_DIR, "squad_transition_indices.csv")
    df_trans.to_csv(out_csv, index=False)
    print(f"Saved squad transition indices to {out_csv} ({len(df_trans)} rows)")
    
    # Summary of most turbulent rebuilds vs most stable squads
    print("\nTop 5 Most Stable Teams (Lowest Transition Index):")
    for _, r in df_trans.sort_values("transition_index").head(5).iterrows():
        print(f"  {r['season']} {r['team']:<25} Transition Index: {r['transition_index']:.3f} (Mins Ret: {r['minutes_retention']*100:.1f}%)")
        
    print("\nTop 5 Highest Transition Rebuilds (Non-Promoted):")
    for _, r in df_trans[df_trans['is_promoted'] == 0].sort_values("transition_index", ascending=False).head(5).iterrows():
        print(f"  {r['season']} {r['team']:<25} Transition Index: {r['transition_index']:.3f} (Mins Turnover: {r['minutes_turnover']*100:.1f}%)")
        
    return df_trans

if __name__ == "__main__":
    compute_transition_indices()

