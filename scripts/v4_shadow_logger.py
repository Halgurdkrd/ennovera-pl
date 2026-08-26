"""V4 Shadow Mode Prediction Logger.
Records immutable pre-kickoff predictions for V2 and V4 models during live seasons (e.g. 2026-27).
Ensures predictions cannot be altered post-kickoff and preserves timestamped snapshots.

Run from ennovera-pl/ directory:
python scripts/v4_shadow_logger.py
"""
import os
import sys
import json
import datetime
import pandas as pd
import numpy as np

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

SHADOW_DIR = os.path.join(_ROOT, "data/shadow")
os.makedirs(SHADOW_DIR, exist_ok=True)

PRED_FILE = os.path.join(SHADOW_DIR, "v4_shadow_predictions.csv")
RESULT_FILE = os.path.join(SHADOW_DIR, "v4_shadow_results.csv")

PRED_COLUMNS = [
    "fixture_id", "season", "gameweek", "kickoff_time", "home_team", "away_team",
    "v2_prob_home", "v2_prob_draw", "v2_prob_away", "v2_top_pred", "v2_conf",
    "v4_prob_home", "v4_prob_draw", "v4_prob_away", "v4_top_pred", "v4_conf",
    "v4_strong_pick_50", "v4_strong_pick_55", "v4_strong_pick_60", "v4_strong_pick_65",
    "prediction_timestamp", "data_cutoff_timestamp"
]

RESULT_COLUMNS = [
    "fixture_id", "season", "gameweek", "home_team", "away_team",
    "actual_result", "home_goals", "away_goals",
    "v2_correct", "v4_correct",
    "v2_match_logloss", "v4_match_logloss",
    "v2_match_brier", "v4_match_brier",
    "result_logged_timestamp"
]

def init_shadow_tables():
    """Initializes empty shadow prediction and results CSVs if they do not already exist."""
    if not os.path.exists(PRED_FILE):
        pd.DataFrame(columns=PRED_COLUMNS).to_csv(PRED_FILE, index=False)
        print(f"Initialized shadow predictions table at {PRED_FILE}")
    if not os.path.exists(RESULT_FILE):
        pd.DataFrame(columns=RESULT_COLUMNS).to_csv(RESULT_FILE, index=False)
        print(f"Initialized shadow results table at {RESULT_FILE}")

def log_fixture_prediction(fixture_id, season, gw, kickoff_iso, home, away,
                           p_v2, p_v4, data_cutoff_iso=None):
    """
    Logs an immutable pre-kickoff prediction snapshot for a fixture.
    p_v2: [p_home, p_draw, p_away]
    p_v4: [p_home, p_draw, p_away]
    """
    init_shadow_tables()
    df_pred = pd.read_csv(PRED_FILE)
    
    # Check if fixture prediction already exists
    if fixture_id in df_pred["fixture_id"].values:
        print(f"WARNING: Fixture {fixture_id} ({home} vs {away}) already logged. Snapshot is immutable.")
        return
        
    p_v2 = np.asarray(p_v2, dtype=float); p_v2 /= p_v2.sum()
    p_v4 = np.asarray(p_v4, dtype=float); p_v4 /= p_v4.sum()
    
    pred_v2_idx = int(p_v2.argmax())
    pred_v4_idx = int(p_v4.argmax())
    conf_v2 = float(p_v2.max())
    conf_v4 = float(p_v4.max())
    
    classes = ["H", "D", "A"]
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cutoff = data_cutoff_iso or now_iso
    
    record = {
        "fixture_id": str(fixture_id),
        "season": str(season),
        "gameweek": int(gw),
        "kickoff_time": str(kickoff_iso),
        "home_team": home,
        "away_team": away,
        "v2_prob_home": round(float(p_v2[0]), 4),
        "v2_prob_draw": round(float(p_v2[1]), 4),
        "v2_prob_away": round(float(p_v2[2]), 4),
        "v2_top_pred": classes[pred_v2_idx],
        "v2_conf": round(conf_v2, 4),
        "v4_prob_home": round(float(p_v4[0]), 4),
        "v4_prob_draw": round(float(p_v4[1]), 4),
        "v4_prob_away": round(float(p_v4[2]), 4),
        "v4_top_pred": classes[pred_v4_idx],
        "v4_conf": round(conf_v4, 4),
        "v4_strong_pick_50": int(conf_v4 >= 0.50),
        "v4_strong_pick_55": int(conf_v4 >= 0.55),
        "v4_strong_pick_60": int(conf_v4 >= 0.60),
        "v4_strong_pick_65": int(conf_v4 >= 0.65),
        "prediction_timestamp": now_iso,
        "data_cutoff_timestamp": cutoff,
    }
    
    df_pred = pd.concat([df_pred, pd.DataFrame([record])], ignore_index=True)
    df_pred.to_csv(PRED_FILE, index=False)
    print(f"Logged shadow prediction for GW {gw}: {home} vs {away} (V2: {record['v2_top_pred']} {conf_v2*100:.1f}%, V4: {record['v4_top_pred']} {conf_v4*100:.1f}%)")

def log_fixture_result(fixture_id, actual_result, home_goals=None, away_goals=None):
    """
    Logs actual outcome for a previously logged fixture and computes instant loss metrics.
    actual_result: 'H', 'D', or 'A'
    """
    init_shadow_tables()
    df_pred = pd.read_csv(PRED_FILE)
    df_res = pd.read_csv(RESULT_FILE)
    
    match_pred = df_pred[df_pred["fixture_id"] == str(fixture_id)]
    if len(match_pred) == 0:
        raise ValueError(f"No pre-kickoff prediction found for fixture_id {fixture_id}")
        
    row = match_pred.iloc[0]
    p_v2 = np.array([row["v2_prob_home"], row["v2_prob_draw"], row["v2_prob_away"]])
    p_v4 = np.array([row["v4_prob_home"], row["v4_prob_draw"], row["v4_prob_away"]])
    
    act_idx = {"H": 0, "D": 1, "A": 2}[actual_result]
    oh = np.eye(3)[act_idx]
    
    ll_v2 = -float(np.log(max(1e-9, p_v2[act_idx])))
    ll_v4 = -float(np.log(max(1e-9, p_v4[act_idx])))
    br_v2 = float(np.sum((p_v2 - oh) ** 2))
    br_v4 = float(np.sum((p_v4 - oh) ** 2))
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    record = {
        "fixture_id": str(fixture_id),
        "season": str(row["season"]),
        "gameweek": int(row["gameweek"]),
        "home_team": row["home_team"],
        "away_team": row["away_team"],
        "actual_result": actual_result,
        "home_goals": int(home_goals) if home_goals is not None else -1,
        "away_goals": int(away_goals) if away_goals is not None else -1,
        "v2_correct": int(row["v2_top_pred"] == actual_result),
        "v4_correct": int(row["v4_top_pred"] == actual_result),
        "v2_match_logloss": round(ll_v2, 5),
        "v4_match_logloss": round(ll_v4, 5),
        "v2_match_brier": round(br_v2, 5),
        "v4_match_brier": round(br_v4, 5),
        "result_logged_timestamp": now_iso,
    }
    
    # Update or append
    if str(fixture_id) in df_res["fixture_id"].astype(str).values:
        df_res = df_res[df_res["fixture_id"] != str(fixture_id)]
    df_res = pd.concat([df_res, pd.DataFrame([record])], ignore_index=True)
    df_res.to_csv(RESULT_FILE, index=False)
    print(f"Logged result for {row['home_team']} vs {row['away_team']}: Result={actual_result} (V2 LL={ll_v2:.3f}, V4 LL={ll_v4:.3f})")

if __name__ == "__main__":
    init_shadow_tables()

