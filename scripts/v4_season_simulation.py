"""Phase 15, 16, 17: Fast Vectorized Season Simulation with Parameter Uncertainty, Backtests & Case Studies.
Runs 10,000-iteration Monte Carlo simulations with fixed vs parameter uncertainty sampling,
backtests champion/relegation probabilities, and inspects Arsenal, Manchester City, and Liverpool case studies.

Run from ennovera-pl/ directory:
python scripts/v4_season_simulation.py
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
from v4_score_model import compute_score_probs_batch

V4_FEATS_PATH = os.path.join(_ROOT, "data/v4_features/v4_dynamic_team_states.csv")
WF_V2_PATH = os.path.join(_ROOT, "data/v3_walkforward/v2_walkforward_predictions.csv")
CONFIG_PATH = os.path.join(_ROOT, "data/experiments/v4_walkforward_evaluation.json")
EXP_DIR = os.path.join(_ROOT, "data/experiments")

df_v4 = pd.read_csv(V4_FEATS_PATH)
df_v2 = pd.read_csv(WF_V2_PATH)
merged = pd.merge(df_v4, df_v2[["season", "home", "away", "v2_prob_home", "v2_prob_draw", "v2_prob_away"]], on=["season", "home", "away"], how="left")

with open(CONFIG_PATH, "r") as f:
    eval_cfg = json.load(f)

cfg = eval_cfg["config"]
mu_league = cfg["mu_league"]
hfa_mult = cfg["hfa_mult"]
rho = cfg["rho_dixon_coles"]
w_score = cfg["blend_weight_score"]

# ---------------------------------------------------------------------------
# Fast Vectorized Monte Carlo Simulation
# ---------------------------------------------------------------------------
def simulate_season(season_df, n_sims=10000, use_param_unc=True):
    teams = sorted(set(season_df["home"]) | set(season_df["away"]))
    team2idx = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    n_fixtures = len(season_df)
    
    h_idx = np.array([team2idx[t] for t in season_df["home"]])
    a_idx = np.array([team2idx[t] for t in season_df["away"]])
    
    # Base expected goals
    lh_base = mu_league * hfa_mult * season_df["v4_home_att"].values * season_df["v4_away_def"].values
    la_base = mu_league * season_df["v4_away_att"].values * season_df["v4_home_def"].values
    
    unc_h = season_df["v4_home_unc"].values
    unc_a = season_df["v4_away_unc"].values
    
    # V2 probabilities for blending
    P_v2 = season_df[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
    P_v2 = np.clip(P_v2, 1e-9, 1); P_v2 = P_v2 / P_v2.sum(axis=1, keepdims=True)
    
    P_score = compute_score_probs_batch(lh_base, la_base, rho=rho, uncertainty_arr=None)
    P_base = w_score * P_score + (1.0 - w_score) * P_v2
    
    rng = np.random.default_rng(13)
    
    if not use_param_unc:
        cum_h = P_base[:, 0]
        cum_d = P_base[:, 0] + P_base[:, 1]
        
        R = rng.random((n_sims, n_fixtures))
        hw = (R < cum_h)
        dr = (R >= cum_h) & (R < cum_d)
        aw = (R >= cum_d)
    else:
        # Vectorized parameter dispersion: (n_sims, n_fixtures)
        noise_h = rng.normal(0, unc_h[None, :], size=(n_sims, n_fixtures))
        noise_a = rng.normal(0, unc_a[None, :], size=(n_sims, n_fixtures))
        shift = 0.08 * (noise_h - noise_a)
        
        p_h_sim = np.clip(P_base[None, :, 0] + shift, 0.02, 0.95)
        p_a_sim = np.clip(P_base[None, :, 2] - shift, 0.02, 0.95)
        p_d_sim = np.clip(1.0 - (p_h_sim + p_a_sim), 0.05, 0.60)
        
        # Renormalize
        tot = p_h_sim + p_d_sim + p_a_sim
        p_h_sim /= tot
        p_d_sim /= tot
        
        cum_h = p_h_sim
        cum_d = p_h_sim + p_d_sim
        
        R = rng.random((n_sims, n_fixtures))
        hw = (R < cum_h)
        dr = (R >= cum_h) & (R < cum_d)
        aw = (R >= cum_d)

    pts = np.zeros((n_sims, n_teams), dtype=np.int32)
    gd = np.zeros((n_sims, n_teams), dtype=np.int32)
    
    for f in range(n_fixtures):
        h = h_idx[f]; a = a_idx[f]
        pts[:, h] += hw[:, f] * 3 + dr[:, f] * 1
        pts[:, a] += aw[:, f] * 3 + dr[:, f] * 1
        gd[:, h] += hw[:, f] * 1 - aw[:, f] * 1
        gd[:, a] += aw[:, f] * 1 - hw[:, f] * 1

    tiebreak = rng.random((n_sims, n_teams))
    scores = pts * 10000.0 + gd * 10.0 + tiebreak
    ranks = np.argsort(-scores, axis=1)
    
    champ_counts = np.bincount(ranks[:, 0], minlength=n_teams)
    top4_counts = np.bincount(ranks[:, :4].ravel(), minlength=n_teams)
    releg_counts = np.bincount(ranks[:, -3:].ravel(), minlength=n_teams)
    
    positions = np.zeros((n_sims, n_teams), dtype=np.int32)
    for s in range(n_sims):
        positions[s, ranks[s]] = np.arange(1, n_teams + 1)
        
    summary = []
    for i, t in enumerate(teams):
        summary.append({
            "team": t,
            "champ_pct": round(champ_counts[i] / n_sims * 100, 2),
            "top4_pct": round(top4_counts[i] / n_sims * 100, 2),
            "releg_pct": round(releg_counts[i] / n_sims * 100, 2),
            "exp_pts": round(float(pts[:, i].mean()), 1),
            "std_pts": round(float(pts[:, i].std()), 1),
            "exp_pos": round(float(positions[:, i].mean()), 1),
        })
    summary.sort(key=lambda x: -x["exp_pts"])
    return summary

# ---------------------------------------------------------------------------
# Run Simulation Comparisons on 2025-26 Holdout Season
# ---------------------------------------------------------------------------
hold_df = merged[merged["season"] == "2025-26"].copy().reset_index(drop=True)
sim_fixed = {r["team"]: r for r in simulate_season(hold_df, n_sims=10000, use_param_unc=False)}
sim_unc = {r["team"]: r for r in simulate_season(hold_df, n_sims=10000, use_param_unc=True)}

print("=" * 80)
print("PHASE 15: MONTE CARLO SEASON SIMULATION (2025-26 HOLDOUT, 10,000 RUNS)")
print("=" * 80)
print(f"{'Team':<25}{'Exp Pts':<10}{'Std Pts (Fixed)':<18}{'Std Pts (Unc)':<16}{'Champ%':<10}{'Top4%':<10}{'Releg%'}")
print("-" * 95)
for t, r_unc in sorted(sim_unc.items(), key=lambda x: -x[1]["exp_pts"]):
    r_fix = sim_fixed[t]
    print(f"{t:<25}{r_unc['exp_pts']:<10.1f}{r_fix['std_pts']:<18.1f}{r_unc['std_pts']:<16.1f}{str(r_unc['champ_pct'])+'%':<10}{str(r_unc['top4_pct'])+'%':<10}{str(r_unc['releg_pct'])+'%'}")

# ---------------------------------------------------------------------------
# Phase 17: Case Studies (Arsenal, Manchester City, Liverpool)
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 17: ARSENAL / MANCHESTER CITY / LIVERPOOL CASE STUDIES")
print("=" * 80)

trans_df = pd.read_csv(os.path.join(_ROOT, "data/v4_features/squad_transition_indices.csv"))
trans_25 = trans_df[trans_df["season"] == "2025-26"].set_index("team")

for team in ["Arsenal", "Manchester City", "Liverpool", "Chelsea", "Tottenham", "Burnley"]:
    t_matches = hold_df[(hold_df["home"] == team) | (hold_df["away"] == team)]
    att_vals = [r["v4_home_att"] if r["home"] == team else r["v4_away_att"] for _, r in t_matches.iterrows()]
    def_vals = [r["v4_home_def"] if r["home"] == team else r["v4_away_def"] for _, r in t_matches.iterrows()]
    unc_vals = [r["v4_home_unc"] if r["home"] == team else r["v4_away_unc"] for _, r in t_matches.iterrows()]
    
    t_row = trans_25.loc[team] if team in trans_25.index else None
    t_idx = t_row["transition_index"] if t_row is not None else 0.5
    
    print(f"\nClub: {team}")
    print(f"  Squad Transition Index (S-1 to S): {t_idx:.3f} (Mins Turnover: {t_row['minutes_turnover']*100:.1f}%)" if t_row is not None else "  Promoted")
    print(f"  Mean Dynamic Attack State: {np.mean(att_vals):.3f} (League Avg: 1.00)")
    print(f"  Mean Dynamic Defence State: {np.mean(def_vals):.3f} (League Avg: 1.00, lower is better)")
    print(f"  Mean Model Uncertainty: {np.mean(unc_vals):.3f}")
    print(f"  Simulated 2025-26 Expected Points: {sim_unc[team]['exp_pts']} +/- {sim_unc[team]['std_pts']} pts")
    print(f"  Champion %: {sim_unc[team]['champ_pct']}%, Top 4 %: {sim_unc[team]['top4_pct']}%, Relegation %: {sim_unc[team]['releg_pct']}%")

out_sim_json = os.path.join(EXP_DIR, "v4_season_simulation.json")
with open(out_sim_json, "w") as f:
    json.dump({
        "fixed_simulation": sim_fixed,
        "uncertainty_simulation": sim_unc,
    }, f, indent=2)
print(f"\nSaved simulation outputs to {out_sim_json}")

