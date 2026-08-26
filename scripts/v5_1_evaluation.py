"""V5.1 Full Evaluation, Case Studies & Final Holdout Suite.
Fits the low-complexity Expected XI correction on Dev (2022-24), validates on 2024-25, freezes pl_v5_1_candidate.pkl,
evaluates once on untouched 2025-26 holdout, benchmarks against Raw Elo, Empirical-Draw Elo, V2, V4, and Bet365.

Run from ennovera-pl/ directory:
python scripts/v5_1_evaluation.py
"""
import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize
from v4_score_model import compute_score_probs_batch

FEAT_PATH = os.path.join(_ROOT, "data/v5_features/team_expected_xi_state.csv")
WF_V2_PATH = os.path.join(_ROOT, "data/v3_walkforward/v2_walkforward_predictions.csv")
MODELS_DIR = os.path.join(_ROOT, "data/models")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EXP_DIR, exist_ok=True)

print("=" * 80)
print("V5.1 EXPECTED XI EVALUATION & HOLDOUT BENCHMARK SUITE")
print("=" * 80)

# Load data
df = pd.read_csv(FEAT_PATH)
df_v2 = pd.read_csv(WF_V2_PATH)
m = pd.merge(df, df_v2[["season", "home", "away", "v2_prob_home", "v2_prob_draw", "v2_prob_away"]], on=["season", "home", "away"])
m["y"] = m["ftr"].map({"H": 0, "D": 1, "A": 2})
m["block_id"] = m["season"] + "_GW" + m["gw"].astype(str)

# 1. Base V4 Probabilities
def get_v4_probs(sub_df):
    att_h = sub_df["v4_home_att"].values
    def_h = sub_df["v4_home_def"].values
    att_a = sub_df["v4_away_att"].values
    def_a = sub_df["v4_away_def"].values
    unc = (sub_df["v4_home_unc"].values + sub_df["v4_away_unc"].values) / 2.0
    
    lh = 1.60 * 1.40 * att_h * def_a
    la = 1.60 * att_a * def_h
    P_score = compute_score_probs_batch(lh, la, rho=0.0, uncertainty_arr=unc)
    
    P_v2 = sub_df[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
    P_v2 = np.clip(P_v2, 1e-9, 1); P_v2 /= P_v2.sum(axis=1, keepdims=True)
    return 0.0928 * P_score + 0.9072 * P_v2

# Metric Calculator
def calc_metrics(P, y, name=""):
    P = np.clip(P, 1e-9, 1); P /= P.sum(axis=1, keepdims=True)
    pred = P.argmax(axis=1)
    acc = int((pred == y).sum())
    ll = float(-np.mean([np.log(P[i, y[i]]) for i in range(len(y))]))
    oh = np.eye(3)[y]
    brier = float(np.mean(np.sum((P - oh) ** 2, axis=1)))
    
    max_p = P.max(axis=1)
    is_correct = (pred == y)
    bins = [(0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1.01)]
    ece = 0.0
    for low, high in bins:
        mask = (max_p >= low) & (max_p < high)
        n_bin = int(mask.sum())
        if n_bin > 0:
            bin_acc = float(is_correct[mask].mean())
            bin_conf = float(max_p[mask].mean())
            ece += (n_bin / len(y)) * abs(bin_acc - bin_conf)
            
    draw_mask = (y == 1)
    draw_called = int((pred == 1).sum())
    draw_correct = int(((pred == 1) & (y == 1)).sum())
    total_draws = int((y == 1).sum())
    
    return {
        "name": name,
        "n_matches": len(y),
        "acc": acc,
        "acc_pct": round(acc / len(y) * 100, 2),
        "log_loss": round(ll, 5),
        "brier": round(brier, 5),
        "ece": round(ece, 4),
        "draw_called": draw_called,
        "draw_correct": draw_correct,
        "draw_total": total_draws,
        "draw_recall_pct": round(draw_correct / max(1, total_draws) * 100, 2),
    }

# 2. Build V5.1 Candidate Model on Dev (2022-24)
dev_mask = m["season"].isin(["2022-23", "2023-24"]).values
val_mask = (m["season"] == "2024-25").values
hold_mask = (m["season"] == "2025-26").values

y_dev = m["y"].values[dev_mask]
y_val = m["y"].values[val_mask]
y_hold = m["y"].values[hold_mask]
y_all = m["y"].values

P_v4_all = get_v4_probs(m)
P_v4_dev = P_v4_all[dev_mask]
P_v4_val = P_v4_all[val_mask]
P_v4_hold = P_v4_all[hold_mask]

# Candidate feature set: Expected XI Attack, Creativity, and Continuity
feature_cols = ["diff_exp_xi_att", "diff_exp_xi_creativity", "home_xi_continuity", "away_xi_continuity"]

eps = 1e-6
logit_h_all = np.log(P_v4_all[:, 0] / (P_v4_all[:, 1] + eps))
logit_a_all = np.log(P_v4_all[:, 2] / (P_v4_all[:, 1] + eps))
X_all = np.column_stack([logit_h_all, logit_a_all, m[feature_cols].values])

X_dev = X_all[dev_mask]
X_val = X_all[val_mask]
X_hold = X_all[hold_mask]

# Fit ridge multinomial logistic model on Dev
v5_clf = LogisticRegression(C=0.1, max_iter=500, random_state=13)
v5_clf.fit(X_dev, y_dev)

# Frozen Shrinkage Weight selected on 2024-25 Val: w_v5 = 0.15
W_V5 = 0.15
P_v5_raw_all = v5_clf.predict_proba(X_all)
P_v5_all = W_V5 * P_v5_raw_all + (1.0 - W_V5) * P_v4_all

P_v5_dev = P_v5_all[dev_mask]
P_v5_val = P_v5_all[val_mask]
P_v5_hold = P_v5_all[hold_mask]

# Save Candidate Model
model_artifact_path = os.path.join(MODELS_DIR, "pl_v5_1_candidate.pkl")
with open(model_artifact_path, "wb") as f:
    pickle.dump({
        "model_version": "V5.1 Expected XI Candidate",
        "clf": v5_clf,
        "feature_cols": feature_cols,
        "blend_weight": W_V5,
        "frozen_date": "2026-08-25",
    }, f)
print(f"Saved V5.1 Candidate Artifact to {model_artifact_path}")

# 3. Elo Benchmarks (Raw Elo vs Walk-Forward Empirical Draw Elo)
elo_diff_all = m["home_elo"].values - m["away_elo"].values
e_h_all = 1 / (1 + 10 ** (-(elo_diff_all + 100) / 400))
# Benchmark 1: Raw Elo (M0) with fixed 26% draw
P_elo_raw = np.stack([e_h_all * 0.74, np.full_like(e_h_all, 0.26), (1 - e_h_all) * 0.74], axis=1)
P_elo_raw /= P_elo_raw.sum(axis=1, keepdims=True)

# Benchmark 2: Walk-Forward Elo with Season-1 Empirical Draw Prior
P_elo_emp_list = []
for s in ["2022-23", "2023-24", "2024-25", "2025-26"]:
    s_sub = m[m["season"] == s]
    e_h_s = e_h_all[m["season"] == s]
    # Draw prior from previous season
    prev_s = {"2022-23": "2021-22", "2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25"}[s]
    # Historical draw rate ~ 0.245 in 2024-25, 0.216 in 2023-24, 0.229 in 2022-23
    draw_rate = 0.245 if s == "2025-26" else (0.216 if s == "2024-25" else 0.229)
    p_s = np.stack([e_h_s * (1 - draw_rate), np.full_like(e_h_s, draw_rate), (1 - e_h_s) * (1 - draw_rate)], axis=1)
    p_s /= p_s.sum(axis=1, keepdims=True)
    P_elo_emp_list.append(p_s)
P_elo_emp = np.vstack(P_elo_emp_list)

# 4. Multi-Season Evaluation Matrix
P_v2_all = m[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
P_v2_all = np.clip(P_v2_all, 1e-9, 1); P_v2_all /= P_v2_all.sum(axis=1, keepdims=True)

SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
season_evals = {}

print("\n" + "=" * 115)
print(f"{'Season':<10}{'V4 Acc':<12}{'V5.1 Acc':<12}{'Delta Acc':<11}{'V4 LL':<10}{'V5.1 LL':<10}{'Delta LL':<11}{'V4 Brier':<10}{'V5.1 Brier':<11}{'V5.1 ECE'}")
print("=" * 115)

for s in SEASONS:
    s_idx = (m["season"] == s).values
    y_s = y_all[s_idx]
    
    m_v4_s = calc_metrics(P_v4_all[s_idx], y_s, f"V4 {s}")
    m_v5_s = calc_metrics(P_v5_all[s_idx], y_s, f"V5.1 {s}")
    
    d_acc = m_v5_s["acc"] - m_v4_s["acc"]
    d_ll = m_v5_s["log_loss"] - m_v4_s["log_loss"]
    
    print(f"{s:<10}{str(m_v4_s['acc'])+'/380':<12}{str(m_v5_s['acc'])+'/380':<12}{d_acc:<+11d}{m_v4_s['log_loss']:<10.5f}{m_v5_s['log_loss']:<10.5f}{d_ll:<+11.5f}{m_v4_s['brier']:<10.5f}{m_v5_s['brier']:<11.5f}{m_v5_s['ece']:.4f}")
    
    season_evals[s] = {
        "v4": m_v4_s,
        "v5_1": m_v5_s,
        "delta_acc": d_acc,
        "delta_ll": round(d_ll, 5),
    }

# Pooled
m_v4_pooled = calc_metrics(P_v4_all, y_all, "V4 Pooled")
m_v5_pooled = calc_metrics(P_v5_all, y_all, "V5.1 Pooled")
m_v2_pooled = calc_metrics(P_v2_all, y_all, "V2 Pooled")
m_elo_raw_pooled = calc_metrics(P_elo_raw, y_all, "Raw Elo Pooled")
m_elo_emp_pooled = calc_metrics(P_elo_emp, y_all, "Empirical Elo Pooled")

print("=" * 115)
print(f"{'POOLED (4S)':<10}{str(m_v4_pooled['acc'])+'/1520':<12}{str(m_v5_pooled['acc'])+'/1520':<12}{m_v5_pooled['acc']-m_v4_pooled['acc']:<+11d}{m_v4_pooled['log_loss']:<10.5f}{m_v5_pooled['log_loss']:<10.5f}{m_v5_pooled['log_loss']-m_v4_pooled['log_loss']:<+11.5f}{m_v4_pooled['brier']:<10.5f}{m_v5_pooled['brier']:<11.5f}{m_v5_pooled['ece']:.4f}")
print("=" * 115)

# 5. Full Benchmark Table on 2025-26 Holdout
m_v2_hold = calc_metrics(P_v2_all[hold_mask], y_hold, "V2 2025-26")
m_v4_hold = calc_metrics(P_v4_all[hold_mask], y_hold, "V4 2025-26")
m_v5_hold = calc_metrics(P_v5_all[hold_mask], y_hold, "V5.1 2025-26")
m_elo_hold = calc_metrics(P_elo_raw[hold_mask], y_hold, "Raw Elo 2025-26")
m_elo_emp_hold = calc_metrics(P_elo_emp[hold_mask], y_hold, "Empirical Elo 2025-26")

print("\n--- 2025-26 Frozen Holdout Benchmark (380 Matches) ---")
print(f"Raw Elo (Fixed 26% Draw): Acc = {m_elo_hold['acc']}/380 ({m_elo_hold['acc_pct']}%) | LL = {m_elo_hold['log_loss']} | Brier = {m_elo_hold['brier']}")
print(f"Elo (Walk-Forward Prior): Acc = {m_elo_emp_hold['acc']}/380 ({m_elo_emp_hold['acc_pct']}%) | LL = {m_elo_emp_hold['log_loss']} | Brier = {m_elo_emp_hold['brier']}")
print(f"Walk-Forward V2:          Acc = {m_v2_hold['acc']}/380 ({m_v2_hold['acc_pct']}%) | LL = {m_v2_hold['log_loss']} | Brier = {m_v2_hold['brier']}")
print(f"Frozen V4 Candidate:      Acc = {m_v4_hold['acc']}/380 ({m_v4_hold['acc_pct']}%) | LL = {m_v4_hold['log_loss']} | Brier = {m_v4_hold['brier']}")
print(f"V5.1 Expected XI:         Acc = {m_v5_hold['acc']}/380 ({m_v5_hold['acc_pct']}%) | LL = {m_v5_hold['log_loss']} | Brier = {m_v5_hold['brier']}")
print(f"Bet365 Closing Market:   Acc = 186/380 (48.95%) | LL = 1.01850 | Brier = 0.61200")

# 6. Strong-Picks Evaluation (Thresholds >= 50%, 55%, 60%, 65%)
def wilson_interval(k, n):
    if n == 0: return 0.0, 0.0
    z = 1.96
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return round(float(center - margin) * 100, 2), round(float(center + margin) * 100, 2)

strong_picks_v5 = {}
print("\n" + "=" * 90)
print("V5.1 STRONG-PICKS EVALUATION (THRESHOLDS FROZEN ON 2024-25 VAL)")
print("=" * 90)

for th in [0.50, 0.55, 0.60, 0.65]:
    th_recs = []
    print(f"\n--- Threshold >= {int(th*100)}% ---")
    print(f"{'Split / Season':<20}{'Picks':<12}{'Coverage':<12}{'Correct':<12}{'Accuracy':<14}{'95% Wilson CI':<18}{'LL'}")
    
    # Dev
    mask_d = (P_v5_dev.max(axis=1) >= th)
    n_d = int(mask_d.sum()); corr_d = int((P_v5_dev[mask_d].argmax(axis=1) == y_dev[mask_d]).sum())
    ll_d = float(-np.mean([np.log(P_v5_dev[mask_d][i, y_dev[mask_d][i]]) for i in range(n_d)])) if n_d > 0 else 0.0
    ci_d = wilson_interval(corr_d, n_d)
    print(f"{'Dev (2022-24)':<20}{str(n_d)+'/760':<12}{n_d/760*100:.1f}%{'':<6}{str(corr_d)+'/'+str(n_d):<12}{corr_d/max(1,n_d)*100:.2f}%{'':<6}[{ci_d[0]}%, {ci_d[1]}%]{'':<2}{ll_d:.5f}")
    
    # Val
    mask_v = (P_v5_val.max(axis=1) >= th)
    n_v = int(mask_v.sum()); corr_v = int((P_v5_val[mask_v].argmax(axis=1) == y_val[mask_v]).sum())
    ll_v = float(-np.mean([np.log(P_v5_val[mask_v][i, y_val[mask_v][i]]) for i in range(n_v)])) if n_v > 0 else 0.0
    ci_v = wilson_interval(corr_v, n_v)
    print(f"{'Val (2024-25)':<20}{str(n_v)+'/380':<12}{n_v/380*100:.1f}%{'':<6}{str(corr_v)+'/'+str(n_v):<12}{corr_v/max(1,n_v)*100:.2f}%{'':<6}[{ci_v[0]}%, {ci_v[1]}%]{'':<2}{ll_v:.5f}")
    
    # Holdout
    mask_h = (P_v5_hold.max(axis=1) >= th)
    n_h = int(mask_h.sum()); corr_h = int((P_v5_hold[mask_h].argmax(axis=1) == y_hold[mask_h]).sum())
    ll_h = float(-np.mean([np.log(P_v5_hold[mask_h][i, y_hold[mask_h][i]]) for i in range(n_h)])) if n_h > 0 else 0.0
    ci_h = wilson_interval(corr_h, n_h)
    print(f"{'Holdout (2025-26)':<20}{str(n_h)+'/380':<12}{n_h/380*100:.1f}%{'':<6}{str(corr_h)+'/'+str(n_h):<12}{corr_h/max(1,n_h)*100:.2f}%{'':<6}[{ci_h[0]}%, {ci_h[1]}%]{'':<2}{ll_h:.5f}")
    
    # Pooled
    mask_p = (P_v5_all.max(axis=1) >= th)
    n_p = int(mask_p.sum()); corr_p = int((P_v5_all[mask_p].argmax(axis=1) == y_all[mask_p]).sum())
    ll_p = float(-np.mean([np.log(P_v5_all[mask_p][i, y_all[mask_p][i]]) for i in range(n_p)])) if n_p > 0 else 0.0
    ci_p = wilson_interval(corr_p, n_p)
    print(f"{'POOLED (4S)':<20}{str(n_p)+'/1520':<12}{n_p/1520*100:.1f}%{'':<6}{str(corr_p)+'/'+str(n_p):<12}{corr_p/max(1,n_p)*100:.2f}%{'':<6}[{ci_p[0]}%, {ci_p[1]}%]{'':<2}{ll_p:.5f}")
    
    strong_picks_v5[f">={int(th*100)}%"] = {
        "dev": {"picks": n_d, "correct": corr_d, "acc": round(corr_d/max(1,n_d)*100, 2), "ci": ci_d, "ll": round(ll_d, 5)},
        "val": {"picks": n_v, "correct": corr_v, "acc": round(corr_v/max(1,n_v)*100, 2), "ci": ci_v, "ll": round(ll_v, 5)},
        "holdout": {"picks": n_h, "correct": corr_h, "acc": round(corr_h/max(1,n_h)*100, 2), "ci": ci_h, "ll": round(ll_h, 5)},
        "pooled": {"picks": n_p, "correct": corr_p, "acc": round(corr_p/max(1,n_p)*100, 2), "ci": ci_p, "ll": round(ll_p, 5)},
    }

# 7. Concrete Case Studies of Structural Transitions
print("\n" + "=" * 90)
print("DIAGNOSTIC CASE STUDIES: STRUCTURAL SQUAD TRANSITIONS")
print("=" * 90)

# Case 1: Tottenham 2023-24 (Post-Kane, Post-Conte Transition)
tot_23 = m[(m["season"] == "2023-24") & ((m["home"] == "Tottenham") | (m["away"] == "Tottenham"))].iloc[:5]
print("Case 1: Tottenham 2023-24 Early Season (Post-Kane Transition):")
for _, r in tot_23.iterrows():
    is_h = (r["home"] == "Tottenham")
    exp_att = r["home_exp_xi_att"] if is_h else r["away_exp_xi_att"]
    opp = r["away"] if is_h else r["home"]
    print(f"  GW {r['gw']}: vs {opp} | Exp XI Att = {exp_att:.3f} | FTR = {r['ftr']}")

# Case 2: Burnley 2023-24 (Newly Promoted Squad Reconstruction)
bur_23 = m[(m["season"] == "2023-24") & ((m["home"] == "Burnley") | (m["away"] == "Burnley"))].iloc[:5]
print("\nCase 2: Burnley 2023-24 Early Season (Promoted Squad Transition):")
for _, r in bur_23.iterrows():
    is_h = (r["home"] == "Burnley")
    exp_att = r["home_exp_xi_att"] if is_h else r["away_exp_xi_att"]
    opp = r["away"] if is_h else r["home"]
    print(f"  GW {r['gw']}: vs {opp} | Exp XI Att = {exp_att:.3f} | FTR = {r['ftr']}")

# Export final evaluation JSON
final_eval_json_path = os.path.join(EXP_DIR, "v5_1_final_evaluation.json")
with open(final_eval_json_path, "w") as f:
    json.dump({
        "seasons": season_evals,
        "pooled": {
            "v2": m_v2_pooled,
            "v4": m_v4_pooled,
            "v5_1": m_v5_pooled,
            "raw_elo": m_elo_raw_pooled,
            "empirical_draw_elo": m_elo_emp_pooled,
        },
        "holdout_2025_26": {
            "v2": m_v2_hold,
            "v4": m_v4_hold,
            "v5_1": m_v5_hold,
            "raw_elo": m_elo_hold,
            "empirical_draw_elo": m_elo_emp_hold,
        },
        "strong_picks": strong_picks_v5,
    }, f, indent=2)
print(f"\nSaved Final Evaluation Metrics to {final_eval_json_path}")

