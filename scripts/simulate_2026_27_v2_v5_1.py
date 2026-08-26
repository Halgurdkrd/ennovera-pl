"""Full 2026-27 Pre-GW1 and Post-GW1 Championship Simulation Engine (100,000 Monte Carlo Iterations).
Compares Frozen V2 and Frozen V5.1, decomposes contender title probabilities (Man City vs Arsenal),
and measures historical inertia vs current squad state.

Run from ennovera-pl/ directory:
python scripts/simulate_2026_27_v2_v5_1.py
"""
import os
import sys
import json
import time
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

t0 = time.time()
print("=" * 80)
print("2026-27 PRE-GW1 & POST-GW1 MONTE CARLO CHAMPIONSHIP SIMULATION (100,000 RUNS)")
print("=" * 80)

# ---------------------------------------------------------------------------
# 1. Load Fixtures, Models, and Pre-GW1 States
# ---------------------------------------------------------------------------
FIXTURES_PATH = os.path.join(_ROOT, "data/raw/fpl_full/data/2026-27/fixtures.csv")
TEAMS_PATH = os.path.join(_ROOT, "data/raw/fpl_full/data/2026-27/teams.csv")
V2_MODEL_PATH = os.path.join(_ROOT, "data/models/pl_v2_final.pkl")
V5_MODEL_PATH = os.path.join(_ROOT, "data/models/pl_v5_1_candidate.pkl")
CURRENT_ELO_PATH = os.path.join(_ROOT, "data/processed/current_elo.csv")
PL_FEATURES_PATH = os.path.join(_ROOT, "data/processed/pl_features.csv")
V4_MASTER_PATH = os.path.join(_ROOT, "data/v4_features/v4_dynamic_team_states.csv")
GW1_RESULTS_PATH = os.path.join(EXP_DIR, "2026_27_gw1_official_results.json")

with open(GW1_RESULTS_PATH, "r") as f:
    gw1_results = json.load(f)

# Teams
teams_df = pd.read_csv(TEAMS_PATH)
tid_to_team = {r["id"]: canonicalize(r["name"]) for _, r in teams_df.iterrows()}
all_teams = sorted(list(tid_to_team.values()))
assert len(all_teams) == 20, f"Expected 20 teams, got {len(all_teams)}"

# Fixtures schedule
fix_df = pd.read_csv(FIXTURES_PATH)
schedule = []
for _, r in fix_df.iterrows():
    h = tid_to_team[r["team_h"]]
    a = tid_to_team[r["team_a"]]
    schedule.append({
        "fixture_id": int(r["id"]),
        "event": int(r["event"]),
        "home": h,
        "away": a,
    })
assert len(schedule) == 380, f"Expected 380 fixtures, got {len(schedule)}"

# Models
with open(V2_MODEL_PATH, "rb") as f:
    v2_art = pickle.load(f)
v2_cal = v2_art["calibrator"]
v2_feats = v2_art["features"]

with open(V5_MODEL_PATH, "rb") as f:
    v5_art = pickle.load(f)
v5_clf = v5_art["clf"]
W_V5 = v5_art["blend_weight"]

# Pre-GW1 Elo
cur_elo = pd.read_csv(CURRENT_ELO_PATH)
pre_elo_dict = {canonicalize(r["team"]): float(r["derived_elo"]) for _, r in cur_elo.iterrows()}

PREV_POS = {canonicalize(k): v for k, v in {
    'Arsenal':1,'Man City':2,'Liverpool':3,'Chelsea':4,'Aston Villa':5,'Newcastle':6,'Man Utd':7,'Bournemouth':8,
    'Brighton':9,'Brentford':10,'Crystal Palace':11,"Nott'm Forest":12,'Fulham':13,'Everton':14,'Tottenham':15,
    'Leeds':16,'Ipswich':17,'Sunderland':18,'Coventry City':19,'Hull City':20}.items()}

DEFAULT_GF = 1.3
df_hist = pd.read_csv(PL_FEATURES_PATH)
d_2526 = df_hist[df_hist["season"] == "2025-26"].sort_values("date")
dq = defaultdict(lambda: deque(maxlen=5))
for r in d_2526.itertuples():
    dq[canonicalize(r.home)].append(r.fthg)
    dq[canonicalize(r.away)].append(r.ftag)
pre_form_dict = {t: (sum(v)/len(v) if v else DEFAULT_GF) for t, v in dq.items()}

# Pre-GW1 V4 states
v4_master = pd.read_csv(V4_MASTER_PATH)
v4_2526 = v4_master[v4_master["season"] == "2025-26"]
pre_team_att = {}
pre_team_def = {}
pre_team_unc = {}
for t in all_teams:
    t_matches = v4_2526[(v4_2526["home"].apply(canonicalize) == t) | (v4_2526["away"].apply(canonicalize) == t)].sort_values("gw")
    if len(t_matches) > 0:
        last_m = t_matches.iloc[-1]
        is_h = (canonicalize(last_m["home"]) == t)
        last_att = float(last_m["v4_home_att"] if is_h else last_m["v4_away_att"])
        last_def = float(last_m["v4_home_def"] if is_h else last_m["v4_away_def"])
        last_unc = float(last_m["v4_home_unc"] if is_h else last_m["v4_away_unc"])
        pre_team_att[t] = 0.35 * 1.0 + 0.65 * last_att
        pre_team_def[t] = 0.35 * 1.0 + 0.65 * last_def
        pre_team_unc[t] = min(0.30, last_unc + 0.05)
    else:
        pre_team_att[t] = 0.85; pre_team_def[t] = 1.15; pre_team_unc[t] = 0.35

# Pre-GW1 V5.1 Expected XI features
pre_exp_att = {}
pre_exp_creativity = {}
pre_exp_continuity = {}
for t in all_teams:
    pre_exp_att[t] = round(pre_team_att[t] * 1.45, 4)
    pre_exp_creativity[t] = round(pre_team_att[t] * 1.10, 4)
    pre_exp_continuity[t] = 0.85 if PREV_POS.get(t, 20) <= 15 else 0.60

# ---------------------------------------------------------------------------
# 2. Probability Generator Functions
# ---------------------------------------------------------------------------
def compute_match_probs_v2(home, away, elo_d, form_d):
    he = elo_d.get(home, 1500.0)
    ae = elo_d.get(away, 1500.0)
    elo_diff = he - ae
    hf = form_d.get(home, DEFAULT_GF)
    af = form_d.get(away, DEFAULT_GF)
    hp = PREV_POS.get(home, 18)
    ap = PREV_POS.get(away, 18)
    
    feat_map = {
        'home_elo': he, 'away_elo': ae, 'elo_diff': elo_diff,
        'home_form5_gf': hf, 'away_form5_gf': af,
        'home_prev_position': hp, 'away_prev_position': ap,
    }
    x_vec = np.array([[feat_map[f] for f in v2_feats]])
    probs = v2_cal.predict_proba(x_vec)[0]
    probs = np.clip(probs, 1e-9, 1); probs /= probs.sum()
    return probs

def compute_match_probs_v5(home, away, elo_d, form_d, att_d, def_d, unc_d, exp_att_d, exp_cre_d, exp_cont_d):
    p_v2 = compute_match_probs_v2(home, away, elo_d, form_d)
    
    att_h = att_d[home]; def_h = def_d[home]
    att_a = att_d[away]; def_a = def_d[away]
    unc = (unc_d[home] + unc_d[away]) / 2.0
    
    lh = 1.60 * 1.40 * att_h * def_a
    la = 1.60 * att_a * def_h
    p_score = compute_score_probs_batch(np.array([lh]), np.array([la]), rho=0.0, uncertainty_arr=np.array([unc]))[0]
    p_v4 = 0.0928 * p_score + 0.9072 * p_v2
    p_v4 = np.clip(p_v4, 1e-9, 1); p_v4 /= p_v4.sum()
    
    diff_att = exp_att_d[home] - exp_att_d[away]
    diff_cre = exp_cre_d[home] - exp_cre_d[away]
    h_cont = exp_cont_d[home]; a_cont = exp_cont_d[away]
    
    eps = 1e-6
    logit_h = np.log(p_v4[0] / (p_v4[1] + eps))
    logit_a = np.log(p_v4[2] / (p_v4[1] + eps))
    x_v5 = np.array([[logit_h, logit_a, diff_att, diff_cre, h_cont, a_cont]])
    p_v5_raw = v5_clf.predict_proba(x_v5)[0]
    p_v5 = W_V5 * p_v5_raw + (1.0 - W_V5) * p_v4
    p_v5 = np.clip(p_v5, 1e-9, 1); p_v5 /= p_v5.sum()
    return p_v5

# ---------------------------------------------------------------------------
# 3. Vectorized Monte Carlo Simulation Engine (100,000 Runs)
# ---------------------------------------------------------------------------
N_SIMS = 100000

def run_season_simulations(match_probs_list, initial_points=None, seed=42):
    """Vectorized simulation of remaining fixtures."""
    rng = np.random.default_rng(seed)
    n_matches = len(match_probs_list)
    
    # Pre-extract probabilities
    team_idx_map = {t: i for i, t in enumerate(all_teams)}
    home_indices = np.array([team_idx_map[m["home"]] for m in match_probs_list])
    away_indices = np.array([team_idx_map[m["away"]] for m in match_probs_list])
    probs = np.array([m["probs"] for m in match_probs_list]) # (n_matches, 3)
    
    # Cumulative probability thresholds for inverse transform sampling
    cum_p_h = probs[:, 0]
    cum_p_hd = probs[:, 0] + probs[:, 1]
    
    # Initialize points array: shape (N_SIMS, 20)
    pts_arr = np.zeros((N_SIMS, 20), dtype=np.float32)
    if initial_points:
        for t, pts in initial_points.items():
            pts_arr[:, team_idx_map[t]] = pts
            
    # Simulate fixtures in chunks for high performance
    # Draw random uniform matrix (n_matches, N_SIMS)
    rand_draws = rng.random((n_matches, N_SIMS), dtype=np.float32)
    
    is_home_win = (rand_draws < cum_p_h[:, None])
    is_draw = ((rand_draws >= cum_p_h[:, None]) & (rand_draws < cum_p_hd[:, None]))
    is_away_win = (rand_draws >= cum_p_hd[:, None])
    
    for i in range(n_matches):
        h_idx = home_indices[i]
        a_idx = away_indices[i]
        
        pts_arr[:, h_idx] += is_home_win[i] * 3.0 + is_draw[i] * 1.0
        pts_arr[:, a_idx] += is_away_win[i] * 3.0 + is_draw[i] * 1.0
        
    # Compute rankings per simulation: highest points is rank 0
    # Add small tiebreaker noise to avoid exact discrete rank artifacts
    tiebreak_noise = rng.normal(0, 1e-4, pts_arr.shape).astype(np.float32)
    ranked_indices = np.argsort(-(pts_arr + tiebreak_noise), axis=1)
    
    ranks = np.zeros_like(pts_arr, dtype=np.int32)
    for sim in range(N_SIMS):
        ranks[sim, ranked_indices[sim]] = np.arange(20)
        
    # Aggregate statistics
    results = {}
    mean_pts = pts_arr.mean(axis=0)
    champ_freq = (ranks == 0).mean(axis=0) * 100.0
    top4_freq = (ranks < 4).mean(axis=0) * 100.0
    rel_freq = (ranks >= 17).mean(axis=0) * 100.0
    
    for t in all_teams:
        idx = team_idx_map[t]
        results[t] = {
            "team": t,
            "xPts": round(float(mean_pts[idx]), 2),
            "champ_pct": round(float(champ_freq[idx]), 2),
            "top4_pct": round(float(top4_freq[idx]), 2),
            "relegation_pct": round(float(rel_freq[idx]), 2),
        }
    return results

# ---------------------------------------------------------------------------
# 4. PRE-GW1 Simulation (All 380 matches scheduled)
# ---------------------------------------------------------------------------
print("\n--- Running Pre-GW1 Simulations (100,000 Runs) ---")
pre_probs_v2 = []
pre_probs_v5 = []
for fix in schedule:
    h = fix["home"]; a = fix["away"]
    pv2 = compute_match_probs_v2(h, a, pre_elo_dict, pre_form_dict)
    pv5 = compute_match_probs_v5(h, a, pre_elo_dict, pre_form_dict, pre_team_att, pre_team_def, pre_team_unc, pre_exp_att, pre_exp_creativity, pre_exp_continuity)
    pre_probs_v2.append({"fixture_id": fix["fixture_id"], "home": h, "away": a, "probs": pv2})
    pre_probs_v5.append({"fixture_id": fix["fixture_id"], "home": h, "away": a, "probs": pv5})

sim_pre_v2 = run_season_simulations(pre_probs_v2, initial_points=None, seed=101)
sim_pre_v5 = run_season_simulations(pre_probs_v5, initial_points=None, seed=101)

# ---------------------------------------------------------------------------
# 5. POST-GW1 Simulation (10 completed matches locked, 370 remaining)
# ---------------------------------------------------------------------------
print("\n--- Running Post-GW1 Simulations (100,000 Runs) ---")
# Apply GW1 updates strictly
post_gw1_points = defaultdict(float)
post_elo_dict = dict(pre_elo_dict)
post_form_dict = dict(pre_form_dict)
post_team_att = dict(pre_team_att)
post_team_def = dict(pre_team_def)
post_team_unc = dict(pre_team_unc)
post_exp_att = dict(pre_exp_att)
post_exp_creativity = dict(pre_exp_creativity)
post_exp_continuity = dict(pre_exp_continuity)

for res in gw1_results:
    h = canonicalize(res["home_team"])
    a = canonicalize(res["away_team"])
    hs = res["home_score"]; as_score = res["away_score"]
    ftr = res["ftr"]
    
    # Points
    if ftr == "H":
        post_gw1_points[h] += 3.0
    elif ftr == "A":
        post_gw1_points[a] += 3.0
    else:
        post_gw1_points[h] += 1.0
        post_gw1_points[a] += 1.0
        
    # Standard Elo Update (K=20, HFA=100)
    e_h = 1 / (1 + 10 ** (-((post_elo_dict[h] - post_elo_dict[a]) + 100) / 400))
    s_h = 1.0 if ftr == "H" else (0.5 if ftr == "D" else 0.0)
    post_elo_dict[h] += 20.0 * (s_h - e_h)
    post_elo_dict[a] += 20.0 * ((1.0 - s_h) - (1.0 - e_h))
    
    # Form update
    dq[h].append(hs)
    dq[a].append(as_score)
    post_form_dict[h] = sum(dq[h]) / len(dq[h])
    post_form_dict[a] = sum(dq[a]) / len(dq[a])
    
    # Dynamic attack/defense update (EWMA alpha=0.15)
    post_team_att[h] = 0.85 * post_team_att[h] + 0.15 * max(0.5, hs / 1.5)
    post_team_att[a] = 0.85 * post_team_att[a] + 0.15 * max(0.5, as_score / 1.1)
    post_team_def[h] = 0.85 * post_team_def[h] + 0.15 * max(0.5, as_score / 1.1)
    post_team_def[a] = 0.85 * post_team_def[a] + 0.15 * max(0.5, hs / 1.5)
    
    post_exp_att[h] = round(post_team_att[h] * 1.45, 4)
    post_exp_att[a] = round(post_team_att[a] * 1.45, 4)

# Remaining 370 fixtures (events >= 2)
remaining_schedule = [f for f in schedule if f["event"] >= 2]
assert len(remaining_schedule) == 370, f"Expected 370 remaining fixtures, got {len(remaining_schedule)}"

post_probs_v2 = []
post_probs_v5 = []
for fix in remaining_schedule:
    h = fix["home"]; a = fix["away"]
    pv2 = compute_match_probs_v2(h, a, post_elo_dict, post_form_dict)
    pv5 = compute_match_probs_v5(h, a, post_elo_dict, post_form_dict, post_team_att, post_team_def, post_team_unc, post_exp_att, post_exp_creativity, post_exp_continuity)
    post_probs_v2.append({"fixture_id": fix["fixture_id"], "home": h, "away": a, "probs": pv2})
    post_probs_v5.append({"fixture_id": fix["fixture_id"], "home": h, "away": a, "probs": pv5})

sim_post_v2 = run_season_simulations(post_probs_v2, initial_points=post_gw1_points, seed=101)
sim_post_v5 = run_season_simulations(post_probs_v5, initial_points=post_gw1_points, seed=101)

# ---------------------------------------------------------------------------
# 6. Assemble Tables & Export JSONs
# ---------------------------------------------------------------------------
# Sort by V5.1 Pre-GW1 Champion %
sorted_pre_v5 = sorted(sim_pre_v5.values(), key=lambda x: x["champ_pct"], reverse=True)
sorted_pre_v2 = sorted(sim_pre_v2.values(), key=lambda x: x["champ_pct"], reverse=True)

pre_comparison = []
for r in sorted_pre_v5:
    t = r["team"]
    r_v2 = sim_pre_v2[t]
    pre_comparison.append({
        "team": t,
        "v2_xpts": r_v2["xPts"],
        "v5_xpts": r["xPts"],
        "delta_xpts": round(r["xPts"] - r_v2["xPts"], 2),
        "v2_champ_pct": r_v2["champ_pct"],
        "v5_champ_pct": r["champ_pct"],
        "delta_champ_pct": round(r["champ_pct"] - r_v2["champ_pct"], 2),
        "v2_top4_pct": r_v2["top4_pct"],
        "v5_top4_pct": r["top4_pct"],
        "v2_rel_pct": r_v2["relegation_pct"],
        "v5_rel_pct": r["relegation_pct"],
    })

post_comparison = []
for r in sorted_pre_v5:
    t = r["team"]
    pre_v2_res = sim_pre_v2[t]
    post_v2_res = sim_post_v2[t]
    pre_v5_res = sim_pre_v5[t]
    post_v5_res = sim_post_v5[t]
    post_comparison.append({
        "team": t,
        "v2_pre_champ": pre_v2_res["champ_pct"],
        "v2_post_champ": post_v2_res["champ_pct"],
        "v2_delta_champ": round(post_v2_res["champ_pct"] - pre_v2_res["champ_pct"], 2),
        "v5_pre_champ": pre_v5_res["champ_pct"],
        "v5_post_champ": post_v5_res["champ_pct"],
        "v5_delta_champ": round(post_v5_res["champ_pct"] - pre_v5_res["champ_pct"], 2),
        "v2_post_xpts": post_v2_res["xPts"],
        "v5_post_xpts": post_v5_res["xPts"],
    })

# Save Pre-GW1 and Post-GW1 JSONs
json_pre_path = os.path.join(EXP_DIR, "2026_27_preseason_champion_simulation.json")
with open(json_pre_path, "w") as f:
    json.dump({
        "simulations": N_SIMS,
        "v2_results": sim_pre_v2,
        "v5_results": sim_pre_v5,
        "comparison": pre_comparison,
    }, f, indent=2)
print(f"Saved Pre-GW1 Simulation to {json_pre_path}")

json_post_path = os.path.join(EXP_DIR, "2026_27_post_gw1_champion_simulation.json")
with open(json_post_path, "w") as f:
    json.dump({
        "simulations": N_SIMS,
        "v2_results": sim_post_v2,
        "v5_results": sim_post_v5,
        "comparison": post_comparison,
    }, f, indent=2)
print(f"Saved Post-GW1 Simulation to {json_post_path}")

# Print Pre-GW1 Comparison Table
print("\n" + "=" * 105)
print(f"{'Team':<26}{'V2 xPts':<10}{'V5.1 xPts':<12}{'Delta xPts':<12}{'V2 Champ%':<12}{'V5.1 Champ%':<14}{'Delta Champ%'}")
print("=" * 105)
for r in pre_comparison:
    print(f"{r['team']:<26}{r['v2_xpts']:<10.2f}{r['v5_xpts']:<12.2f}{r['delta_xpts']:<+12.2f}{r['v2_champ_pct']:<12.2f}{r['v5_champ_pct']:<14.2f}{r['delta_champ_pct']:<+12.2f}")

# Print Post-GW1 Comparison Table
print("\n" + "=" * 105)
print(f"{'Team':<26}{'V2 Pre Champ':<14}{'V2 Post Champ':<15}{'V2 Delta':<11}{'V5 Pre Champ':<14}{'V5 Post Champ':<15}{'V5 Delta'}")
print("=" * 105)
for r in post_comparison:
    print(f"{r['team']:<26}{r['v2_pre_champ']:<14.2f}{r['v2_post_champ']:<15.2f}{r['v2_delta_champ']:<+11.2f}{r['v5_pre_champ']:<14.2f}{r['v5_post_champ']:<15.2f}{r['v5_delta_champ']:<+11.2f}")

print(f"\nSimulation suite completed in {time.time()-t0:.2f}s.")

