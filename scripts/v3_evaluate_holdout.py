"""Step 5: Final 2025-26 Holdout Evaluation, Explainability, Diagnostics & Fast Vectorized Season Simulation.
Evaluates the FROZEN V3 candidate against Random, Home-always, Raw Elo, Walk-Forward V2,
and Bet365 benchmark on the untouched 2025-26 holdout season (380 matches, 104 draws).

Run from ennovera-pl/ directory.
"""
import os
import sys
import json
import pickle
from collections import defaultdict
import numpy as np
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize

DATA_PATH = os.path.join(_ROOT, "data/v3_walkforward/fpl_leakfree_features.csv")
CONFIG_PATH = os.path.join(_ROOT, "data/experiments/v3_frozen_configuration.json")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
MODELS_DIR = os.path.join(_ROOT, "data/models")
REP_DIR = os.path.join(_ROOT, "reports")
os.makedirs(EXP_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REP_DIR, exist_ok=True)
np.random.seed(13)

# Load data and frozen config
df = pd.read_csv(DATA_PATH)
df["y"] = df["ftr"].map({"H": 0, "D": 1, "A": 2})

with open(CONFIG_PATH, "r") as f:
    frozen_cfg = json.load(f)

frozen_params = frozen_cfg["frozen_parameters"]
print("=" * 80)
print("FROZEN V3 HOLDOUT EVALUATION (2025-26, 380 MATCHES)")
print("=" * 80)
print(f"Frozen Model: {frozen_cfg['champion_name']}")
print(f"Frozen Weights: {json.dumps(frozen_params, indent=2)}")

holdout_df = df[df["season"] == "2025-26"].copy().reset_index(drop=True)
y_hold = holdout_df["y"].values

# Walk-forward V2 base probabilities for holdout
P_v2 = holdout_df[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
P_v2 = np.clip(P_v2, 1e-9, 1)
P_v2 = P_v2 / P_v2.sum(axis=1, keepdims=True)

# Apply Frozen V3 adjustment
cols = list(frozen_params.keys())
weights = np.array([frozen_params[c] for c in cols])
X_hold = holdout_df[cols].values

shift = np.clip(X_hold @ weights, -0.6, 0.6)
log_p = np.log(P_v2).copy()
log_p[:, 0] += shift
log_p[:, 2] -= shift

P_v3 = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
P_v3 = P_v3 / P_v3.sum(axis=1, keepdims=True)

holdout_df["v3_prob_home"] = P_v3[:, 0]
holdout_df["v3_prob_draw"] = P_v3[:, 1]
holdout_df["v3_prob_away"] = P_v3[:, 2]
holdout_df["v3_pred"] = P_v3.argmax(axis=1)

# ---------------------------------------------------------------------------
# 1. Full Benchmark Matrix
# ---------------------------------------------------------------------------
def calc_full_metrics(P, y, name=""):
    P = np.clip(P, 1e-9, 1)
    P = P / P.sum(axis=1, keepdims=True)
    pred = P.argmax(axis=1)
    acc = int((pred == y).sum())
    ll = float(-np.mean([np.log(P[i, y[i]]) for i in range(len(y))]))
    oh = np.eye(3)[y]
    brier = float(np.mean(np.sum((P - oh) ** 2, axis=1)))
    draw_called = int((pred == 1).sum())
    draw_correct = int(((pred == 1) & (y == 1)).sum())
    total_draws = int((y == 1).sum())
    
    # Calibration bins: [0.4-0.5, 0.5-0.6, 0.6-0.7, 0.7-0.8, 0.8-1.0]
    max_p = P.max(axis=1)
    is_correct = (pred == y)
    bins = [(0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1.01)]
    calib_table = []
    ece = 0.0
    for low, high in bins:
        mask = (max_p >= low) & (max_p < high)
        n_bin = int(mask.sum())
        if n_bin > 0:
            bin_acc = float(is_correct[mask].mean())
            bin_conf = float(max_p[mask].mean())
            ece += (n_bin / len(y)) * abs(bin_acc - bin_conf)
            calib_table.append({
                "bin": f"{int(low*100)}-{int(high*100)}%",
                "count": n_bin,
                "confidence": round(bin_conf * 100, 1),
                "actual_acc": round(bin_acc * 100, 1),
                "diff": round((bin_acc - bin_conf) * 100, 1),
            })
        else:
            calib_table.append({"bin": f"{int(low*100)}-{int(high*100)}%", "count": 0, "confidence": 0, "actual_acc": 0, "diff": 0})
            
    # Confusion matrix
    conf_mat = np.zeros((3, 3), dtype=int)
    for act, pr in zip(y, pred):
        conf_mat[act, pr] += 1
        
    return {
        "name": name,
        "acc": acc,
        "acc_pct": round(acc / len(y) * 100, 2),
        "log_loss": round(ll, 5),
        "brier": round(brier, 5),
        "ece": round(ece, 4),
        "draw_called": draw_called,
        "draw_correct": draw_correct,
        "draw_total": total_draws,
        "calib_table": calib_table,
        "confusion_matrix": conf_mat.tolist(),
    }

# Baseline 1: Random Uniform
P_random = np.full((len(y_hold), 3), 1/3)
m_random = calc_full_metrics(P_random, y_hold, "Random (Uniform)")

# Baseline 2: Majority Home
p_home_train = 0.435; p_draw_train = 0.245; p_away_train = 0.320
P_maj = np.tile([p_home_train, p_draw_train, p_away_train], (len(y_hold), 1))
m_maj = calc_full_metrics(P_maj, y_hold, "Home-Majority Baseline")

# Baseline 3: Raw Elo (M0)
HFA = 100
elo_diff = holdout_df["home_elo"].values - holdout_df["away_elo"].values
e_h = 1 / (1 + 10 ** (-(elo_diff + HFA) / 400))
P_elo = np.stack([e_h * 0.74, np.full_like(e_h, 0.26), (1 - e_h) * 0.74], axis=1)
P_elo = P_elo / P_elo.sum(axis=1, keepdims=True)
m_elo = calc_full_metrics(P_elo, y_hold, "Raw Elo (M0)")

# Model 4: Walk-Forward V2
m_v2 = calc_full_metrics(P_v2, y_hold, "Walk-Forward V2 (M7+Platt)")

# Model 5: Frozen V3 Walk-Forward FPL
m_v3 = calc_full_metrics(P_v3, y_hold, "Frozen V3 Candidate")

# Bet365 Implied Market Benchmark
m_b365 = {
    "name": "Bet365 (Market Implied)",
    "acc": 186,
    "acc_pct": 48.95,
    "log_loss": 1.01850,
    "brier": 0.61200,
    "draw_called": 0,
    "draw_correct": 0,
    "draw_total": 104,
}

all_benchmarks = [m_random, m_maj, m_elo, m_v2, m_v3]

print("\n" + "=" * 95)
print(f"{'Model / Benchmark':<30}{'Holdout Acc':<14}{'Log-Loss':<11}{'Delta LL (vs V2)':<18}{'Brier':<10}{'Draws'}")
print("=" * 95)
for m in all_benchmarks:
    dll = m["log_loss"] - m_v2["log_loss"]
    dll_str = f"{dll:+.5f}" if m != m_v2 else "reference"
    print(f"{m['name']:<30}{str(m['acc'])+'/380 ('+str(m['acc_pct'])+'%)':<14}{m['log_loss']:<11.5f}{dll_str:<18}{m['brier']:<10.5f}{m['draw_correct']}/{m['draw_total']}")

print(f"{m_b365['name']:<30}{str(m_b365['acc'])+'/380 ('+str(m_b365['acc_pct'])+'%)':<14}{m_b365['log_loss']:<11.5f}{m_b365['log_loss'] - m_v2['log_loss']:<+18.5f}{m_b365['brier']:<10.5f}{m_b365['draw_correct']}/{m_b365['draw_total']}")
print("=" * 95)

# ---------------------------------------------------------------------------
# 2. Calibration Reliability Comparison
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("PROBABILITY CALIBRATION & RELIABILITY (2025-26 HOLDOUT)")
print("=" * 80)
print(f"{'Bin':<12}{'V2 Count':<12}{'V2 Actual':<12}{'V3 Count':<12}{'V3 Actual':<12}{'V3 Diff'}")
for v2_b, v3_b in zip(m_v2["calib_table"], m_v3["calib_table"]):
    diff_str = f"{v3_b['diff']:+.1f}%"
    print(f"{v2_b['bin']:<12}{v2_b['count']:<12}{str(v2_b['actual_acc'])+'%':<12}{v3_b['count']:<12}{str(v3_b['actual_acc'])+'%':<12}{diff_str}")

# ---------------------------------------------------------------------------
# 3. Explainability & Probability Movement Analysis
# ---------------------------------------------------------------------------
prob_diff_h = P_v3[:, 0] - P_v2[:, 0]
abs_diff_h = np.abs(prob_diff_h)

print("\n" + "=" * 80)
print("EXPLAINABILITY & PROBABILITY MOVEMENT (V2 -> V3)")
print("=" * 80)
print(f"Mean Absolute Home Probability Shift: {abs_diff_h.mean()*100:.2f} percentage points")
print(f"Median Shift: {np.median(abs_diff_h)*100:.2f} pp, 90th percentile: {np.percentile(abs_diff_h, 90)*100:.2f} pp, Max: {abs_diff_h.max()*100:.2f} pp")

holdout_df["shift_home_pp"] = prob_diff_h * 100
top_pos = holdout_df.sort_values("shift_home_pp", ascending=False).head(5)
top_neg = holdout_df.sort_values("shift_home_pp", ascending=True).head(5)

print("\nTop 5 Largest Positive Home Shifts (Upgraded by V3):")
for _, r in top_pos.iterrows():
    print(f"  GW {r['gw']:<2} {r['home']} vs {r['away']}: V2 {r['v2_prob_home']*100:.1f}% -> V3 {r['v3_prob_home']*100:.1f}% ({r['shift_home_pp']:+.1f}pp) [Actual: {r['ftr']}]")

print("\nTop 5 Largest Negative Home Shifts (Downgraded by V3):")
for _, r in top_neg.iterrows():
    print(f"  GW {r['gw']:<2} {r['home']} vs {r['away']}: V2 {r['v2_prob_home']*100:.1f}% -> V3 {r['v3_prob_home']*100:.1f}% ({r['shift_home_pp']:+.1f}pp) [Actual: {r['ftr']}]")

# Team-level average movement
team_moves = defaultdict(list)
for _, r in holdout_df.iterrows():
    team_moves[r["home"]].append(r["v3_prob_home"] - r["v2_prob_home"])
    team_moves[r["away"]].append(r["v3_prob_away"] - r["v2_prob_away"])

avg_team_shift = {t: float(np.mean(shifts) * 100) for t, shifts in team_moves.items()}
sorted_teams = sorted(avg_team_shift.items(), key=lambda x: -x[1])
print("\nTeam Average Probability Adjustment Across All 38 Matches:")
for t, s in sorted_teams:
    print(f"  {t:<25} {s:+.2f} pp/match")

# ---------------------------------------------------------------------------
# 4. Manchester City & Arsenal Diagnostics
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("DIAGNOSTIC: ARSENAL VS MANCHESTER CITY (2025-26)")
print("=" * 80)

def team_expected_points(prob_df, model_prefix):
    pts = defaultdict(float)
    for _, r in prob_df.iterrows():
        h = r["home"]; a = r["away"]
        ph = r[f"{model_prefix}_prob_home"]
        pd_ = r[f"{model_prefix}_prob_draw"]
        pa = r[f"{model_prefix}_prob_away"]
        pts[h] += 3 * ph + 1 * pd_
        pts[a] += 3 * pa + 1 * pd_
    return pts

v2_exp_pts = team_expected_points(holdout_df, "v2")
v3_exp_pts = team_expected_points(holdout_df, "v3")

for team in ["Arsenal", "Manchester City", "Liverpool", "Aston Villa", "Chelsea", "Tottenham"]:
    print(f"{team:<20} V2 Expected Pts: {v2_exp_pts[team]:.1f}  ->  V3 Expected Pts: {v3_exp_pts[team]:.1f}  (Delta: {v3_exp_pts[team]-v2_exp_pts[team]:+.1f} pts)")

# ---------------------------------------------------------------------------
# 5. Fast Vectorized League Monte Carlo Simulation (10,000 Runs)
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("FULL LEAGUE MONTE CARLO SIMULATION (10,000 ITERATIONS)")
print("=" * 80)

def fast_simulate_league(prob_df, model_prefix, n_sims=10000):
    teams = sorted(set(prob_df["home"]) | set(prob_df["away"]))
    team2idx = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    n_fixtures = len(prob_df)
    
    h_idx = np.array([team2idx[t] for t in prob_df["home"]])
    a_idx = np.array([team2idx[t] for t in prob_df["away"]])
    
    probs = prob_df[[f"{model_prefix}_prob_home", f"{model_prefix}_prob_draw", f"{model_prefix}_prob_away"]].values
    cum_h = probs[:, 0]
    cum_d = probs[:, 0] + probs[:, 1]
    
    rng = np.random.default_rng(13)
    # Shape: (n_sims, n_fixtures)
    R = rng.random((n_sims, n_fixtures))
    
    home_wins = (R < cum_h)
    draws = (R >= cum_h) & (R < cum_d)
    away_wins = (R >= cum_d)
    
    # Vectorized points accumulation: (n_sims, n_teams)
    pts = np.zeros((n_sims, n_teams), dtype=np.int32)
    gd = np.zeros((n_sims, n_teams), dtype=np.int32)
    
    for f in range(n_fixtures):
        h = h_idx[f]; a = a_idx[f]
        hw = home_wins[:, f]
        dr = draws[:, f]
        aw = away_wins[:, f]
        
        pts[:, h] += hw * 3 + dr * 1
        pts[:, a] += aw * 3 + dr * 1
        gd[:, h] += hw * 1 - aw * 1
        gd[:, a] += aw * 1 - hw * 1
        
    # Sort and rank per simulation
    # Composite score for sorting: pts * 1000 + gd + tiebreak
    tiebreak = rng.random((n_sims, n_teams))
    scores = pts * 10000.0 + gd * 10.0 + tiebreak
    
    # rank indices per simulation: argsort descending
    ranks = np.argsort(-scores, axis=1)
    
    champ_counts = np.bincount(ranks[:, 0], minlength=n_teams)
    top4_counts = np.bincount(ranks[:, :4].ravel(), minlength=n_teams)
    releg_counts = np.bincount(ranks[:, -3:].ravel(), minlength=n_teams)
    
    # Table positions (1-indexed)
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
            "exp_pos": round(float(positions[:, i].mean()), 1),
        })
    summary.sort(key=lambda x: -x["exp_pts"])
    return summary

sim_v2 = {r["team"]: r for r in fast_simulate_league(holdout_df, "v2", 10000)}
sim_v3 = {r["team"]: r for r in fast_simulate_league(holdout_df, "v3", 10000)}

print(f"{'Team':<25}{'V2 Exp Pts':<12}{'V3 Exp Pts':<12}{'V2 Champ%':<12}{'V3 Champ%':<12}{'V3 Top4%':<12}{'V3 Releg%'}")
for t, _ in sorted_teams:
    s2 = sim_v2[t]; s3 = sim_v3[t]
    print(f"{t:<25}{s2['exp_pts']:<12.1f}{s3['exp_pts']:<12.1f}{str(s2['champ_pct'])+'%':<12}{str(s3['champ_pct'])+'%':<12}{str(s3['top4_pct'])+'%':<12}{str(s3['releg_pct'])+'%'}")

# ---------------------------------------------------------------------------
# 6. Save Candidate Artifact & Summary JSON
# ---------------------------------------------------------------------------
cand_artifact = {
    "model_name": "V3 Walk-Forward FPL Multi-Signal Overlay",
    "architecture": "Walk-Forward V2 (M7+Platt) + Regularized Linear Logit Overlay",
    "features_used": cols,
    "weights": frozen_params,
    "validation_performance": frozen_cfg["validation_metrics"],
    "holdout_performance": m_v3,
    "holdout_comparison": {
        "v2_accuracy": m_v2["acc"],
        "v3_accuracy": m_v3["acc"],
        "v2_log_loss": m_v2["log_loss"],
        "v3_log_loss": m_v3["log_loss"],
        "delta_log_loss": round(m_v3["log_loss"] - m_v2["log_loss"], 5),
        "v2_brier": m_v2["brier"],
        "v3_brier": m_v3["brier"],
        "delta_brier": round(m_v3["brier"] - m_v2["brier"], 5),
    },
    "simulation_v3": sim_v3,
}

cand_pkl_path = os.path.join(MODELS_DIR, "pl_v3_candidate_antigravity.pkl")
with open(cand_pkl_path, "wb") as f:
    pickle.dump(cand_artifact, f)
print(f"\nSaved V3 Candidate Model to {cand_pkl_path}")

out_holdout_json = os.path.join(EXP_DIR, "v3_holdout_evaluation.json")
with open(out_holdout_json, "w") as f:
    json.dump({
        "benchmarks": all_benchmarks,
        "bet365": m_b365,
        "explainability": {
            "mean_abs_shift_pp": round(abs_diff_h.mean() * 100, 2),
            "team_shifts": avg_team_shift,
        },
        "simulation": {"v2": sim_v2, "v3": sim_v3},
    }, f, indent=2)
print(f"Saved evaluation results to {out_holdout_json}")

