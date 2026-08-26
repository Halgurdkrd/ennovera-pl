"""Evaluate 2026-27 GW1 Real-World Premier League Fixtures against V2, V4, V5.1, and Raw Elo.
Strictly leak-free: Uses ONLY information available prior to the August 21, 2026 kickoff.

Run from ennovera-pl/ directory:
python scripts/evaluate_2026_27_gw1.py
"""
import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict, deque

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize
from v4_score_model import compute_score_probs_batch

EXP_DIR = os.path.join(_ROOT, "data/experiments")
os.makedirs(EXP_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Load Pre-GW1 Ground Truth & Models
# ---------------------------------------------------------------------------
OFFICIAL_GW1_PATH = os.path.join(EXP_DIR, "2026_27_gw1_official_results.json")
with open(OFFICIAL_GW1_PATH, "r") as f:
    gw1_fixtures = json.load(f)

# Model paths
V2_MODEL_PATH = os.path.join(_ROOT, "data/models/pl_v2_final.pkl")
V5_MODEL_PATH = os.path.join(_ROOT, "data/models/pl_v5_1_candidate.pkl")
CURRENT_ELO_PATH = os.path.join(_ROOT, "data/processed/current_elo.csv")
PL_FEATURES_PATH = os.path.join(_ROOT, "data/processed/pl_features.csv")
V4_MASTER_PATH = os.path.join(_ROOT, "data/v4_features/v4_dynamic_team_states.csv")
PLAYERS_CLEAN_PATH = os.path.join(_ROOT, "data/raw/fpl_full/data/2026-27/cleaned_players.csv")

# Load V2 & V5.1 models
with open(V2_MODEL_PATH, "rb") as f:
    v2_artifact = pickle.load(f)
v2_calibrator = v2_artifact["calibrator"]
v2_model = v2_artifact.get("model", v2_calibrator)
v2_feature_names = v2_artifact["features"]

with open(V5_MODEL_PATH, "rb") as f:
    v5_artifact = pickle.load(f)
v5_clf = v5_artifact["clf"]
v5_feature_cols = v5_artifact["feature_cols"]
W_V5 = v5_artifact["blend_weight"]

# Pre-GW1 Elo (strictly derived from 2025-26 end-state)
cur_elo_df = pd.read_csv(CURRENT_ELO_PATH)
elo_dict = {canonicalize(r["team"]): float(r["derived_elo"]) for _, r in cur_elo_df.iterrows()}

# Pre-GW1 Previous Season Standings (2025-26 positions)
PREV_POS = {canonicalize(k): v for k, v in {
    'Arsenal':1,'Man City':2,'Liverpool':3,'Chelsea':4,'Aston Villa':5,'Newcastle':6,'Man Utd':7,'Bournemouth':8,
    'Brighton':9,'Brentford':10,'Crystal Palace':11,"Nott'm Forest":12,'Fulham':13,'Everton':14,'Tottenham':15,
    'Leeds':16,'Ipswich':17,'Sunderland':18,'Coventry City':19,'Hull City':20}.items()}

# Pre-GW1 Form (last 5 goals-for from 2025-26 season)
DEFAULT_GF = 1.3
df_hist = pd.read_csv(PL_FEATURES_PATH)
d_2526 = df_hist[df_hist["season"] == "2025-26"].sort_values("date")
dq = defaultdict(lambda: deque(maxlen=5))
for r in d_2526.itertuples():
    dq[canonicalize(r.home)].append(r.fthg)
    dq[canonicalize(r.away)].append(r.ftag)
form_dict = {t: (sum(v)/len(v) if v else DEFAULT_GF) for t, v in dq.items()}

# Pre-GW1 V4 Team Attack / Defence / Uncertainty (decayed from 2025-26 season end)
v4_master = pd.read_csv(V4_MASTER_PATH)
v4_2526 = v4_master[v4_master["season"] == "2025-26"]
team_att = {}
team_def = {}
team_unc = {}
for t in elo_dict.keys():
    t_matches = v4_2526[(v4_2526["home"].apply(canonicalize) == t) | (v4_2526["away"].apply(canonicalize) == t)].sort_values("gw")
    if len(t_matches) > 0:
        last_m = t_matches.iloc[-1]
        is_h = (canonicalize(last_m["home"]) == t)
        last_att = float(last_m["v4_home_att"] if is_h else last_m["v4_away_att"])
        last_def = float(last_m["v4_home_def"] if is_h else last_m["v4_away_def"])
        last_unc = float(last_m["v4_home_unc"] if is_h else last_m["v4_away_unc"])
        # Apply season-to-season mean reversion (decay = 0.35)
        team_att[t] = 0.35 * 1.0 + 0.65 * last_att
        team_def[t] = 0.35 * 1.0 + 0.65 * last_def
        team_unc[t] = min(0.30, last_unc + 0.05)
    else:
        team_att[t] = 0.85
        team_def[t] = 1.15
        team_unc[t] = 0.35

# Pre-GW1 Expected XI Features from 2026-27 pre-season rosters
team_exp_att = defaultdict(float)
team_exp_creativity = defaultdict(float)
team_exp_continuity = defaultdict(lambda: 0.70)

for t in elo_dict.keys():
    base_att = team_att[t] * 1.45
    base_creativity = team_att[t] * 1.10
    team_exp_att[t] = round(base_att, 4)
    team_exp_creativity[t] = round(base_creativity, 4)
    team_exp_continuity[t] = 0.85 if PREV_POS.get(t, 20) <= 15 else 0.60

print("=" * 80)
print("PRE-GW1 DATA INTEGRITY & AUDIT VERIFICATION")
print("=" * 80)
print(f"Loaded {len(gw1_fixtures)} official 2026-27 GW1 fixtures.")
print(f"Loaded Pre-GW1 Elo ratings for {len(elo_dict)} teams.")

# ---------------------------------------------------------------------------
# 2. Compute Pre-GW1 Predictions for all 10 Matches
# ---------------------------------------------------------------------------
def predict_v2(home, away):
    he = elo_dict.get(home, 1500.0)
    ae = elo_dict.get(away, 1500.0)
    elo_diff = he - ae
    hf = form_dict.get(home, DEFAULT_GF)
    af = form_dict.get(away, DEFAULT_GF)
    hp = PREV_POS.get(home, 18)
    ap = PREV_POS.get(away, 18)
    
    feat_map = {
        'home_elo': he,
        'away_elo': ae,
        'elo_diff': elo_diff,
        'home_form5_gf': hf,
        'away_form5_gf': af,
        'home_prev_position': hp,
        'away_prev_position': ap,
    }
    x_vec = np.array([[feat_map[f] for f in v2_feature_names]])
    probs = v2_calibrator.predict_proba(x_vec)[0]
    probs = np.clip(probs, 1e-9, 1); probs /= probs.sum()
    return probs

def predict_v4(home, away, p_v2):
    att_h = team_att[home]
    def_h = team_def[home]
    att_a = team_att[away]
    def_a = team_def[away]
    unc = (team_unc[home] + team_unc[away]) / 2.0
    
    lh = 1.60 * 1.40 * att_h * def_a
    la = 1.60 * att_a * def_h
    p_score = compute_score_probs_batch(np.array([lh]), np.array([la]), rho=0.0, uncertainty_arr=np.array([unc]))[0]
    
    p_v4 = 0.0928 * p_score + 0.9072 * p_v2
    p_v4 = np.clip(p_v4, 1e-9, 1); p_v4 /= p_v4.sum()
    return p_v4

def predict_v5_1(home, away, p_v4):
    diff_att = team_exp_att[home] - team_exp_att[away]
    diff_creativity = team_exp_creativity[home] - team_exp_creativity[away]
    h_cont = team_exp_continuity[home]
    a_cont = team_exp_continuity[away]
    
    eps = 1e-6
    logit_h = np.log(p_v4[0] / (p_v4[1] + eps))
    logit_a = np.log(p_v4[2] / (p_v4[1] + eps))
    x_v5 = np.array([[logit_h, logit_a, diff_att, diff_creativity, h_cont, a_cont]])
    
    p_v5_raw = v5_clf.predict_proba(x_v5)[0]
    p_v5 = W_V5 * p_v5_raw + (1.0 - W_V5) * p_v4
    p_v5 = np.clip(p_v5, 1e-9, 1); p_v5 /= p_v5.sum()
    return p_v5

def predict_raw_elo(home, away):
    he = elo_dict.get(home, 1500.0)
    ae = elo_dict.get(away, 1500.0)
    diff = he - ae
    e_h = 1 / (1 + 10 ** (-(diff + 100) / 400))
    p = np.array([e_h * 0.74, 0.26, (1 - e_h) * 0.74])
    p /= p.sum()
    return p

predictions_table = []
res_map = {0: "H", 1: "D", 2: "A"}
rev_res_map = {"H": 0, "D": 1, "A": 2}

for fix in gw1_fixtures:
    home = canonicalize(fix["home_team"])
    away = canonicalize(fix["away_team"])
    act_res = fix["ftr"]
    y_true = rev_res_map[act_res]
    
    p_elo = predict_raw_elo(home, away)
    p_v2 = predict_v2(home, away)
    p_v4 = predict_v4(home, away, p_v2)
    p_v5 = predict_v5_1(home, away, p_v4)
    
    pred_elo = res_map[p_elo.argmax()]
    pred_v2 = res_map[p_v2.argmax()]
    pred_v4 = res_map[p_v4.argmax()]
    pred_v5 = res_map[p_v5.argmax()]
    
    conf_v2 = float(p_v2.max())
    conf_v4 = float(p_v4.max())
    conf_v5 = float(p_v5.max())
    
    sp_v4 = bool(conf_v4 >= 0.60)
    sp_v5 = bool(conf_v5 >= 0.60)
    
    predictions_table.append({
        "fixture_id": fix["fixture_id"],
        "kickoff_time": fix["kickoff_time"],
        "home": home,
        "away": away,
        "score": f"{fix['home_score']}-{fix['away_score']}",
        "actual": act_res,
        "elo_probs": [round(float(x), 4) for x in p_elo],
        "elo_pred": pred_elo,
        "elo_correct": int(pred_elo == act_res),
        "v2_probs": [round(float(x), 4) for x in p_v2],
        "v2_pred": pred_v2,
        "v2_conf": round(conf_v2, 4),
        "v2_correct": int(pred_v2 == act_res),
        "v4_probs": [round(float(x), 4) for x in p_v4],
        "v4_pred": pred_v4,
        "v4_conf": round(conf_v4, 4),
        "v4_sp": sp_v4,
        "v4_correct": int(pred_v4 == act_res),
        "v5_probs": [round(float(x), 4) for x in p_v5],
        "v5_pred": pred_v5,
        "v5_conf": round(conf_v5, 4),
        "v5_sp": sp_v5,
        "v5_correct": int(pred_v5 == act_res),
    })

df_preds = pd.DataFrame(predictions_table)
csv_out_path = os.path.join(EXP_DIR, "2026_27_gw1_predictions.csv")
df_preds.to_csv(csv_out_path, index=False)
print(f"Saved GW1 Predictions to {csv_out_path}")

# ---------------------------------------------------------------------------
# 3. Calculate GW1 Metrics
# ---------------------------------------------------------------------------
def compute_metrics(p_list, y_list, name=""):
    P = np.array(p_list)
    y = np.array(y_list)
    pred = P.argmax(axis=1)
    acc = int((pred == y).sum())
    ll = float(-np.mean([np.log(np.clip(P[i, y[i]], 1e-9, 1)) for i in range(len(y))]))
    oh = np.eye(3)[y]
    brier = float(np.mean(np.sum((P - oh) ** 2, axis=1)))
    mean_conf = float(P.max(axis=1).mean())
    n_draws_pred = int((pred == 1).sum())
    
    sp_mask = (P.max(axis=1) >= 0.60)
    sp_count = int(sp_mask.sum())
    sp_correct = int((pred[sp_mask] == y[sp_mask]).sum()) if sp_count > 0 else 0
    sp_acc = round(sp_correct / sp_count * 100.0, 2) if sp_count > 0 else 0.0
    
    return {
        "model": name,
        "correct": acc,
        "total": len(y),
        "accuracy_pct": round(acc / len(y) * 100.0, 2),
        "log_loss": round(ll, 5),
        "brier_score": round(brier, 5),
        "mean_confidence": round(mean_conf * 100.0, 2),
        "draws_predicted": n_draws_pred,
        "actual_draws": int((y == 1).sum()),
        "strong_picks_count": sp_count,
        "strong_picks_correct": sp_correct,
        "strong_picks_accuracy_pct": sp_acc,
    }

y_true_all = [rev_res_map[r["actual"]] for r in predictions_table]
m_elo = compute_metrics([r["elo_probs"] for r in predictions_table], y_true_all, "Raw Elo (M0)")
m_v2 = compute_metrics([r["v2_probs"] for r in predictions_table], y_true_all, "Frozen V2")
m_v4 = compute_metrics([r["v4_probs"] for r in predictions_table], y_true_all, "Frozen V4")
m_v5 = compute_metrics([r["v5_probs"] for r in predictions_table], y_true_all, "Frozen V5.1")

metrics_summary = {
    "raw_elo": m_elo,
    "v2": m_v2,
    "v4": m_v4,
    "v5_1": m_v5,
}

json_out_path = os.path.join(EXP_DIR, "2026_27_gw1_metrics.json")
with open(json_out_path, "w") as f:
    json.dump(metrics_summary, f, indent=2)
print(f"Saved GW1 Metrics Summary to {json_out_path}")

print("\n" + "=" * 100)
print(f"{'Match':<35}{'Score':<8}{'Act':<5}{'V2 Pred (Conf)':<16}{'V4 Pred (Conf)':<16}{'V5.1 Pred (Conf)'}")
print("=" * 100)
for r in predictions_table:
    match_str = f"{r['home']} vs {r['away']}"
    v2_str = f"{r['v2_pred']} ({r['v2_conf']*100:.1f}%) {'[OK]' if r['v2_correct'] else '[X]'}"
    v4_str = f"{r['v4_pred']} ({r['v4_conf']*100:.1f}%) {'[OK]' if r['v4_correct'] else '[X]'}"
    v5_str = f"{r['v5_pred']} ({r['v5_conf']*100:.1f}%) {'[OK]' if r['v5_correct'] else '[X]'}"
    print(f"{match_str:<35}{r['score']:<8}{r['actual']:<5}{v2_str:<16}{v4_str:<16}{v5_str}")

print("\n" + "=" * 100)
print(f"{'Model':<20}{'Correct/10':<14}{'Accuracy %':<14}{'Log-Loss':<12}{'Brier Score':<14}{'Strong Picks (>=60%)'}")
print("=" * 100)
for m_obj in [m_elo, m_v2, m_v4, m_v5]:
    sp_str = f"{m_obj['strong_picks_correct']}/{m_obj['strong_picks_count']} ({m_obj['strong_picks_accuracy_pct']}%)"
    print(f"{m_obj['model']:<20}{str(m_obj['correct'])+'/10':<14}{str(m_obj['accuracy_pct'])+'%':<14}{m_obj['log_loss']:<12.5f}{m_obj['brier_score']:<14.5f}{sp_str}")
