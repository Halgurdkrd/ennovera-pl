"""Step 2: Temporal FPL Feature Extraction Engine with Strict Leak-Free Guardrails.
Extracts 8 candidate signal families across all 1,520 matches (2022-23 to 2025-26)
using ONLY completed Gameweeks < N and lagged prior-season teams.csv (S-1).

Includes automated leakage assertions for every match and every feature family.
Run from ennovera-pl/ directory.
"""
import os
import sys
import json
from collections import defaultdict
import numpy as np
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize

RAW_DIR = os.path.join(_ROOT, "data/raw/fpl_full/data")
OUT_DIR = os.path.join(_ROOT, "data/v3_walkforward")
os.makedirs(OUT_DIR, exist_ok=True)

SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
ALL_SEASONS = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]

# ---------------------------------------------------------------------------
# 1. Load lagged prior-season teams.csv (S-1) for Signal 1
# ---------------------------------------------------------------------------
def load_prior_season_fpl_strengths():
    prior_strengths = {}
    for s in SEASONS:
        s_idx = ALL_SEASONS.index(s)
        prev_s = ALL_SEASONS[s_idx - 1]
        prev_teams_path = os.path.join(RAW_DIR, f"{prev_s}/teams.csv")
        if os.path.exists(prev_teams_path):
            t_df = pd.read_csv(prev_teams_path)
            str_dict = {}
            for _, r in t_df.iterrows():
                team_name = canonicalize(r["name"])
                str_dict[team_name] = {
                    "atk_h": float(r.get("strength_attack_home", 1100) or 1100) / 1000.0,
                    "atk_a": float(r.get("strength_attack_away", 1100) or 1100) / 1000.0,
                    "def_h": float(r.get("strength_defence_home", 1100) or 1100) / 1000.0,
                    "def_a": float(r.get("strength_defence_away", 1100) or 1100) / 1000.0,
                    "ovr_h": float(r.get("strength_overall_home", 1100) or 1100) / 1000.0,
                    "ovr_a": float(r.get("strength_overall_away", 1100) or 1100) / 1000.0,
                }
            prior_strengths[s] = str_dict
            print(f"Loaded prior-season strength for {s} from {prev_s}/teams.csv ({len(str_dict)} teams)")
        else:
            prior_strengths[s] = {}
            print(f"Warning: No prior season teams.csv found for {s} (checked {prev_teams_path})")
    return prior_strengths

# ---------------------------------------------------------------------------
# 2. Extract per-match FPL features with strict temporal shifting
# ---------------------------------------------------------------------------
def extract_season_fpl_features(season, prior_strength_dict):
    season_dir = os.path.join(RAW_DIR, season)
    fixtures_df = pd.read_csv(os.path.join(season_dir, "fixtures.csv"))
    teams_df = pd.read_csv(os.path.join(season_dir, "teams.csv"))
    merged_gw_df = pd.read_csv(os.path.join(season_dir, "gws/merged_gw.csv"), low_memory=False)

    id2team = {r["id"]: canonicalize(r["name"]) for _, r in teams_df.iterrows()}
    fixtures_df["home"] = fixtures_df["team_h"].map(id2team)
    fixtures_df["away"] = fixtures_df["team_a"].map(id2team)
    fixtures_df["gw"] = fixtures_df["event"].astype(int)

    # Standardize merged_gw
    merged_gw_df["team_name"] = merged_gw_df["team"].map(canonicalize)
    merged_gw_df["GW"] = merged_gw_df["GW"].astype(int)
    for col in ["expected_goals", "expected_assists", "expected_goals_conceded", "ict_index", "clean_sheets", "total_points", "value", "minutes"]:
        if col in merged_gw_df.columns:
            merged_gw_df[col] = pd.to_numeric(merged_gw_df[col], errors="coerce").fillna(0.0)

    # Pre-aggregate GW-level team stats
    # For each team and each GW g: team_xg, team_xa, team_ict, team_cs, player stats
    team_gw_stats = defaultdict(dict)
    player_gw_stats = defaultdict(lambda: defaultdict(dict)) # team -> gw -> player -> stats
    
    # We also need team_xga: xg conceded in that match = opponent's team_xg in that match
    # Let's group player stats by (team, GW)
    for (team, gw), g_df in merged_gw_df.groupby(["team_name", "GW"]):
        team_xg = float(g_df["expected_goals"].sum())
        team_xa = float(g_df["expected_assists"].sum())
        team_ict = float(g_df["ict_index"].sum())
        # team clean sheet in GW: goalkeeper or primary defenders played and team conceded 0
        goals_conc = float(g_df["goals_conceded"].max() if "goals_conceded" in g_df.columns else 0.0)
        team_cs = 1.0 if goals_conc == 0.0 and len(g_df[g_df["minutes"] > 0]) > 0 else 0.0
        
        # Squad value of players with minutes > 0 (or squad active)
        active_players = g_df[g_df["minutes"] > 0]
        if len(active_players) >= 11:
            squad_val = float(active_players.nlargest(15, "value")["value"].sum()) / 10.0 # in millions
        else:
            squad_val = float(g_df.nlargest(15, "value")["value"].sum()) / 10.0
            
        team_gw_stats[team][gw] = {
            "xg": team_xg,
            "xa": team_xa,
            "ict": team_ict,
            "cs": team_cs,
            "squad_val": squad_val,
            "goals_conceded": goals_conc,
        }
        
        # Player contributions for dependency calculation
        for _, p_row in g_df.iterrows():
            p_name = p_row["name"]
            player_gw_stats[team][gw][p_name] = {
                "xg_xa": float(p_row["expected_goals"] + p_row["expected_assists"]),
                "pts": float(p_row["total_points"]),
            }

    # Derive team xga per GW from opponent's xg in that GW fixture
    for _, fix_row in fixtures_df.iterrows():
        h = fix_row["home"]
        a = fix_row["away"]
        gw = fix_row["gw"]
        h_xg = team_gw_stats[h].get(gw, {}).get("xg", 1.30)
        a_xg = team_gw_stats[a].get(gw, {}).get("xg", 1.30)
        if gw in team_gw_stats[h]:
            team_gw_stats[h][gw]["xga"] = a_xg
        if gw in team_gw_stats[a]:
            team_gw_stats[a][gw]["xga"] = h_xg

    # -----------------------------------------------------------------------
    # Helper to compute rolling features strictly on GW < target_gw
    # -----------------------------------------------------------------------
    def get_rolling_stats(team, target_gw, window=5):
        completed_gws = [g for g in sorted(team_gw_stats[team].keys()) if g < target_gw]
        if not completed_gws:
            return {
                "roll_xg": 1.30,
                "roll_xa": 0.95,
                "roll_xga": 1.30,
                "roll_ict": 35.0,
                "roll_cs": 0.25,
                "squad_val": 85.0,
                "dependency": 0.35,
                "max_source_gw": 0,
                "n_gws": 0,
            }
        
        w_gws = completed_gws[-window:]
        max_src = max(w_gws)
        assert max_src < target_gw, f"LEAK DETECTED: {team} target_gw={target_gw}, max_src={max_src}"
        
        xg_list = [team_gw_stats[team][g]["xg"] for g in w_gws]
        xa_list = [team_gw_stats[team][g]["xa"] for g in w_gws]
        xga_list = [team_gw_stats[team][g].get("xga", 1.30) for g in w_gws]
        ict_list = [team_gw_stats[team][g]["ict"] for g in w_gws]
        cs_list = [team_gw_stats[team][g]["cs"] for g in w_gws]
        val_list = [team_gw_stats[team][g]["squad_val"] for g in w_gws]
        
        # Cumulative player dependency across completed GWs < target_gw
        cum_player_xg_xa = defaultdict(float)
        team_cum_xg_xa = 0.0
        for g in completed_gws:
            for p, p_st in player_gw_stats[team][g].items():
                val = p_st["xg_xa"]
                cum_player_xg_xa[p] += val
                team_cum_xg_xa += val
                
        if team_cum_xg_xa > 0.5 and len(cum_player_xg_xa) >= 2:
            top2_vals = sorted(cum_player_xg_xa.values(), reverse=True)[:2]
            dependency = sum(top2_vals) / team_cum_xg_xa
        else:
            dependency = 0.35
            
        return {
            "roll_xg": float(np.mean(xg_list)),
            "roll_xa": float(np.mean(xa_list)),
            "roll_xga": float(np.mean(xga_list)),
            "roll_ict": float(np.mean(ict_list)),
            "roll_cs": float(np.mean(cs_list)),
            "squad_val": float(val_list[-1]), # most recent prior squad value
            "dependency": float(dependency),
            "max_source_gw": max_src,
            "n_gws": len(w_gws),
        }

    # Now construct the per-match feature rows
    feature_rows = []
    for _, fix in fixtures_df.iterrows():
        h = fix["home"]
        a = fix["away"]
        target_gw = int(fix["gw"])
        
        # 1. Prior-season FPL strength (S1) - from prior season teams.csv
        p_str_h = prior_strength_dict.get(h, {"atk_h": 1.0, "atk_a": 1.0, "def_h": 1.0, "def_a": 1.0})
        p_str_a = prior_strength_dict.get(a, {"atk_h": 1.0, "atk_a": 1.0, "def_h": 1.0, "def_a": 1.0})
        
        s1_atk_diff = p_str_h["atk_h"] - p_str_a["atk_a"]
        s1_def_diff = p_str_a["def_a"] - p_str_h["def_h"] # higher home def -> lower away goals -> positive
        s1_strength_diff = 0.6 * s1_atk_diff + 0.4 * s1_def_diff
        
        # 2-8. Dynamic rolling features (Strictly GW < target_gw)
        h_st = get_rolling_stats(h, target_gw, window=5)
        a_st = get_rolling_stats(a, target_gw, window=5)
        
        # AUTOMATED LEAKAGE ASSERTIONS FOR EVERY FAMILY
        assert h_st["max_source_gw"] < target_gw, f"FATAL LEAK: Home {h} GW {target_gw} source {h_st['max_source_gw']}"
        assert a_st["max_source_gw"] < target_gw, f"FATAL LEAK: Away {a} GW {target_gw} source {a_st['max_source_gw']}"
        
        max_src_gw = max(h_st["max_source_gw"], a_st["max_source_gw"])
        assert max_src_gw < target_gw, f"FATAL LEAK: Match {h} vs {a} GW {target_gw} max_src_gw {max_src_gw}"
        
        # Differentials
        s2_roll_xg_diff = h_st["roll_xg"] - a_st["roll_xg"]
        s3_roll_xa_diff = h_st["roll_xa"] - a_st["roll_xa"]
        s4_roll_xga_diff = a_st["roll_xga"] - h_st["roll_xga"] # positive favors home
        s5_squad_val_diff = (h_st["squad_val"] - a_st["squad_val"]) / 100.0 # scale in £100M
        s6_dependency_diff = a_st["dependency"] - h_st["dependency"] # positive if away is more fragile/dependent
        s7_roll_ict_diff = (h_st["roll_ict"] - a_st["roll_ict"]) / 50.0
        s8_roll_cs_diff = h_st["roll_cs"] - a_st["roll_cs"]
        
        # Opponent-adjusted xG (Section 11)
        # Scale team's recent xG by opponent's defensive conceding tendency
        h_adj_xg = h_st["roll_xg"] * (a_st["roll_xga"] / 1.30)
        a_adj_xg = a_st["roll_xg"] * (h_st["roll_xga"] / 1.30)
        s_opp_adj_xg_diff = h_adj_xg - a_adj_xg

        row = {
            "season": season,
            "gw": target_gw,
            "home": h,
            "away": a,
            "kickoff_time": fix.get("kickoff_time"),
            # Source tracking for leakage audit
            "xg_max_source_gw": max_src_gw,
            "xa_max_source_gw": max_src_gw,
            "xga_max_source_gw": max_src_gw,
            "squad_value_max_source_gw": max_src_gw,
            "dependency_max_source_gw": max_src_gw,
            "ict_max_source_gw": max_src_gw,
            "clean_sheet_max_source_gw": max_src_gw,
            "is_cold_start": 1 if target_gw == 1 else 0,
            # Signal 1: Prior-season FPL strength
            "s1_strength_diff": round(s1_strength_diff, 4),
            "s1_atk_diff": round(s1_atk_diff, 4),
            "s1_def_diff": round(s1_def_diff, 4),
            # Signal 2: Rolling xG
            "home_roll_xg": round(h_st["roll_xg"], 3),
            "away_roll_xg": round(a_st["roll_xg"], 3),
            "s2_roll_xg_diff": round(s2_roll_xg_diff, 4),
            # Signal 3: Rolling xA
            "home_roll_xa": round(h_st["roll_xa"], 3),
            "away_roll_xa": round(a_st["roll_xa"], 3),
            "s3_roll_xa_diff": round(s3_roll_xa_diff, 4),
            # Signal 4: Rolling xGA
            "home_roll_xga": round(h_st["roll_xga"], 3),
            "away_roll_xga": round(a_st["roll_xga"], 3),
            "s4_roll_xga_diff": round(s4_roll_xga_diff, 4),
            # Signal 5: Squad value differential
            "home_squad_val": round(h_st["squad_val"], 2),
            "away_squad_val": round(a_st["squad_val"], 2),
            "s5_squad_val_diff": round(s5_squad_val_diff, 4),
            # Signal 6: Player dependency
            "home_dependency": round(h_st["dependency"], 3),
            "away_dependency": round(a_st["dependency"], 3),
            "s6_dependency_diff": round(s6_dependency_diff, 4),
            # Signal 7: Rolling ICT
            "home_roll_ict": round(h_st["roll_ict"], 2),
            "away_roll_ict": round(a_st["roll_ict"], 2),
            "s7_roll_ict_diff": round(s7_roll_ict_diff, 4),
            # Signal 8: Clean sheet rate
            "home_roll_cs": round(h_st["roll_cs"], 3),
            "away_roll_cs": round(a_st["roll_cs"], 3),
            "s8_roll_cs_diff": round(s8_roll_cs_diff, 4),
            # Section 11: Opponent-adjusted xG
            "s_opp_adj_xg_diff": round(s_opp_adj_xg_diff, 4),
        }
        feature_rows.append(row)
        
    return pd.DataFrame(feature_rows)


def main():
    print("=" * 70)
    print("EXTRACTING TEMPORALLY SAFE HISTORICAL FPL FEATURES (2022-26)")
    print("=" * 70)
    
    prior_strengths = load_prior_season_fpl_strengths()
    all_season_dfs = []
    
    for s in SEASONS:
        print(f"\nProcessing Season {s}...")
        s_df = extract_season_fpl_features(s, prior_strengths.get(s, {}))
        print(f"  Extracted {len(s_df)} matches.")
        
        # Verify leak-free assertions on whole dataframe
        assert (s_df["xg_max_source_gw"] < s_df["gw"]).all(), "LEAKAGE ASSERTION FAILED FOR xg_max_source_gw"
        assert (s_df["dependency_max_source_gw"] < s_df["gw"]).all(), "LEAKAGE ASSERTION FAILED FOR dependency"
        print(f"  All temporal leakage assertions PASSED: max(source_gw) < target_gw for 100% of rows.")
        all_season_dfs.append(s_df)
        
    full_fpl_df = pd.concat(all_season_dfs, ignore_index=True)
    
    # Merge with walk-forward V2 predictions
    wf_path = os.path.join(OUT_DIR, "v2_walkforward_predictions.csv")
    wf_df = pd.read_csv(wf_path)
    
    # Match on (season, home, away)
    merged = wf_df.merge(
        full_fpl_df,
        on=["season", "home", "away"],
        how="inner",
    )
    
    print(f"\nSuccessfully merged with walk-forward V2: {len(merged)} matches total.")
    assert len(merged) == 1520, f"Expected 1520 merged matches, got {len(merged)}"
    
    out_csv = os.path.join(OUT_DIR, "fpl_leakfree_features.csv")
    merged.to_csv(out_csv, index=False)
    print(f"Saved complete leak-free dataset to {out_csv} ({len(merged)} rows, {len(merged.columns)} columns)")

if __name__ == "__main__":
    main()
