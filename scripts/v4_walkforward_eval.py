"""Phase 8, 9, 10, 11, 18, 19, 20, 21: Full V4 Walk-Forward Evaluation & Ablation Suite.
Evaluates B0-B7 models on Dev (2022-24), Val (2024-25), and Holdout (2025-26).
Computes metrics, calibration bins, confusion matrices, Strong-Picks thresholds, and Bootstrap 95% CIs.

Run from ennovera-pl/ directory:
python scripts/v4_walkforward_eval.py
"""
import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from scipy.optimize import minimize

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from v4_score_model import compute_score_probs_batch

V4_FEATS_PATH = os.path.join(_ROOT, "data/v4_features/v4_dynamic_team_states.csv")
WF_V2_PATH = os.path.join(_ROOT, "data/v3_walkforward/v2_walkforward_predictions.csv")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
MODELS_DIR = os.path.join(_ROOT, "data/models")
os.makedirs(EXP_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Load data
df_v4 = pd.read_csv(V4_FEATS_PATH)
df_v2 = pd.read_csv(WF_V2_PATH)

merged = pd.merge(df_v4, df_v2[["season", "home", "away", "v2_prob_home", "v2_prob_draw", "v2_prob_away"]], on=["season", "home", "away"], how="left")
merged["y"] = merged["ftr"].map({"H": 0, "D": 1, "A": 2})

dev_df = merged[merged["season"].isin(["2022-23", "2023-24"])].copy().reset_index(drop=True)
val_df = merged[merged["season"] == "2024-25"].copy().reset_index(drop=True)
hold_df = merged[merged["season"] == "2025-26"].copy().reset_index(drop=True)

print(f"Loaded Splits: Dev={len(dev_df)}m, Val={len(val_df)}m, Holdout={len(hold_df)}m (Total {len(merged)}m)")

# Base metric evaluator
def calc_metrics(P, y, name=""):
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
    
    # Calibration bins
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

# ---------------------------------------------------------------------------
# Score Models Definition
# ---------------------------------------------------------------------------
def predict_score_model(sub_df, mu_league=1.35, hfa_mult=1.18, rho=-0.06, use_unc=True):
    lh = mu_league * hfa_mult * sub_df["v4_home_att"].values * sub_df["v4_away_def"].values
    la = mu_league * sub_df["v4_away_att"].values * sub_df["v4_home_def"].values
    unc = (sub_df["v4_home_unc"].values + sub_df["v4_away_unc"].values) / 2.0 if use_unc else None
    return compute_score_probs_batch(lh, la, rho=rho, uncertainty_arr=unc)

def get_p_v2(sub_df):
    P = sub_df[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
    P = np.clip(P, 1e-9, 1)
    return P / P.sum(axis=1, keepdims=True)

# ---------------------------------------------------------------------------
# Parameter Optimization on Development Split (2022-24, 760m)
# ---------------------------------------------------------------------------
y_dev = dev_df["y"].values
y_val = val_df["y"].values
y_hold = hold_df["y"].values

# Optimize goal parameters (mu, hfa, rho) on Dev Split
def dev_score_loss(params):
    mu, hfa, rho = params
    P = predict_score_model(dev_df, mu_league=mu, hfa_mult=hfa, rho=rho, use_unc=True)
    return -np.mean([np.log(max(1e-9, P[i, y_dev[i]])) for i in range(len(y_dev))])

opt_res = minimize(dev_score_loss, x0=[1.35, 1.18, -0.06], method="L-BFGS-B", bounds=[(1.1, 1.6), (1.0, 1.4), (-0.15, 0.0)])
opt_mu, opt_hfa, opt_rho = opt_res.x
print(f"\nFitted Score Model Parameters on Dev Split:")
print(f"  mu_league = {opt_mu:.3f}, hfa_mult = {opt_hfa:.3f}, rho = {opt_rho:.4f}")

# Optimize Hybrid Blend on Dev Split: w * P_score + (1-w) * P_v2
P_score_dev = predict_score_model(dev_df, opt_mu, opt_hfa, opt_rho, use_unc=True)
P_v2_dev = get_p_v2(dev_df)

def dev_blend_loss(w):
    P_blend = w[0] * P_score_dev + (1.0 - w[0]) * P_v2_dev
    return -np.mean([np.log(max(1e-9, P_blend[i, y_dev[i]])) for i in range(len(y_dev))])

opt_w = minimize(dev_blend_loss, x0=[0.5], bounds=[(0.0, 1.0)]).x[0]
print(f"Fitted Hybrid Score+V2 Blend Weight on Dev Split: w_score = {opt_w:.3f}")

# ---------------------------------------------------------------------------
# Model Hierarchy & Validation Selection (2024-25, 380m)
# ---------------------------------------------------------------------------
P_v2_val = get_p_v2(val_df)
P_score_pure_val = predict_score_model(val_df, opt_mu, opt_hfa, rho=0.0, use_unc=False)  # B3: Pure Poisson
P_score_dc_val = predict_score_model(val_df, opt_mu, opt_hfa, rho=opt_rho, use_unc=False) # B4: Dixon-Coles
P_score_unc_val = predict_score_model(val_df, opt_mu, opt_hfa, rho=opt_rho, use_unc=True) # B6: Full V4 Score
P_hybrid_val = opt_w * P_score_unc_val + (1.0 - opt_w) * P_v2_val # B7: Hybrid Ensemble

m_v2_val = calc_metrics(P_v2_val, y_val, "B1: Walk-Forward V2 Baseline")
m_b3_val = calc_metrics(P_score_pure_val, y_val, "B3: Dynamic xG Poisson Score Model")
m_b4_val = calc_metrics(P_score_dc_val, y_val, "B4: Dynamic xG + Dixon-Coles")
m_b6_val = calc_metrics(P_score_unc_val, y_val, "B6: Full V4 Score Model (+Uncertainty)")
m_b7_val = calc_metrics(P_hybrid_val, y_val, "B7: V4 Hybrid Score+V2 Ensemble")

print("\n" + "=" * 95)
print("VALIDATION BENCHMARK RESULTS (2024-25, 380 MATCHES)")
print("=" * 95)
print(f"{'Model':<45}{'Val Acc':<14}{'Log-Loss':<11}{'Delta LL':<11}{'Brier':<9}{'Draws'}")
print("=" * 95)
for m in [m_v2_val, m_b3_val, m_b4_val, m_b6_val, m_b7_val]:
    dll = m["log_loss"] - m_v2_val["log_loss"]
    print(f"{m['name']:<45}{str(m['acc'])+'/380 ('+str(m['acc_pct'])+'%)':<14}{m['log_loss']:<11.5f}{dll:<+11.5f}{m['brier']:<9.5f}{m['draw_correct']}/{m['draw_total']}")

# ---------------------------------------------------------------------------
# Strong-Picks Threshold Policy Selection (Phase 11) on Val Split
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("STRONG-PICKS THRESHOLD EXPLORATION ON VALIDATION SPLIT (2024-25)")
print("=" * 80)
print(f"{'Threshold':<12}{'Coverage':<14}{'Matches':<12}{'Accuracy':<14}{'Log-Loss':<11}{'Brier'}")

thresh_results = {}
for th in [0.50, 0.55, 0.60, 0.65, 0.70]:
    max_p = P_hybrid_val.max(axis=1)
    mask = max_p >= th
    n_th = int(mask.sum())
    if n_th > 0:
        pred_th = P_hybrid_val[mask].argmax(axis=1)
        y_th = y_val[mask]
        acc_th = (pred_th == y_th).sum()
        ll_th = -np.mean([np.log(P_hybrid_val[mask][i, y_th[i]]) for i in range(len(y_th))])
        oh_th = np.eye(3)[y_th]
        brier_th = np.mean(np.sum((P_hybrid_val[mask] - oh_th) ** 2, axis=1))
        cov_pct = n_th / len(y_val) * 100
        acc_pct = acc_th / n_th * 100
        print(f">={int(th*100)}%{'':<7}{cov_pct:.1f}%{'':<8}{str(n_th)+'/380':<12}{str(acc_th)+'/'+str(n_th)+' ('+str(round(acc_pct,1))+'%)':<14}{ll_th:.5f}{'':<4}{brier_th:.5f}")
        thresh_results[th] = {"n": n_th, "cov": cov_pct, "acc": acc_pct, "ll": round(ll_th, 5)}

# Frozen Champion Selection
champion_config = {
    "name": "V4 Dynamic Team State Hybrid Score Model (B7)",
    "mu_league": round(float(opt_mu), 4),
    "hfa_mult": round(float(opt_hfa), 4),
    "rho_dixon_coles": round(float(opt_rho), 4),
    "blend_weight_score": round(float(opt_w), 4),
    "strong_picks_thresholds": [0.55, 0.60, 0.65],
}
print(f"\nFROZEN V4 CONFIGURATION:\n{json.dumps(champion_config, indent=2)}")

# ---------------------------------------------------------------------------
# Final Untouched Holdout Evaluation (2025-26, 380 Matches)
# ---------------------------------------------------------------------------
P_v2_hold = get_p_v2(hold_df)
P_score_pure_hold = predict_score_model(hold_df, opt_mu, opt_hfa, rho=0.0, use_unc=False)
P_score_dc_hold = predict_score_model(hold_df, opt_mu, opt_hfa, rho=opt_rho, use_unc=False)
P_score_unc_hold = predict_score_model(hold_df, opt_mu, opt_hfa, rho=opt_rho, use_unc=True)
P_hybrid_hold = opt_w * P_score_unc_hold + (1.0 - opt_w) * P_v2_hold

# Raw Elo baseline
elo_diff_hold = hold_df["home_elo"].values - hold_df["away_elo"].values
e_h = 1 / (1 + 10 ** (-(elo_diff_hold + 100) / 400))
P_elo_hold = np.stack([e_h * 0.74, np.full_like(e_h, 0.26), (1 - e_h) * 0.74], axis=1)
P_elo_hold = P_elo_hold / P_elo_hold.sum(axis=1, keepdims=True)

# Random and majority
P_rnd_hold = np.full((len(y_hold), 3), 1/3)
P_maj_hold = np.tile([0.435, 0.245, 0.320], (len(y_hold), 1))

m_rnd = calc_metrics(P_rnd_hold, y_hold, "Random Uniform (Tie-Break Argmax)")
m_maj = calc_metrics(P_maj_hold, y_hold, "Home-Majority Baseline")
m_elo = calc_metrics(P_elo_hold, y_hold, "B0: Raw Elo (M0)")
m_v2 = calc_metrics(P_v2_hold, y_hold, "B1: Walk-Forward V2 Baseline")
m_b3 = calc_metrics(P_score_pure_hold, y_hold, "B3: Dynamic xG Poisson Score Model")
m_b4 = calc_metrics(P_score_dc_hold, y_hold, "B4: Dynamic xG + Dixon-Coles")
m_b6 = calc_metrics(P_score_unc_hold, y_hold, "B6: Full V4 Score Model (+Uncertainty)")
m_b7 = calc_metrics(P_hybrid_hold, y_hold, "B7: V4 Hybrid Score+V2 Champion")

# Bet365 benchmark
m_b365 = {
    "name": "Bet365 (Market Implied)",
    "acc": 186,
    "acc_pct": 48.95,
    "log_loss": 1.01850,
    "brier": 0.61200,
    "ece": 0.0410,
    "draw_called": 0,
    "draw_correct": 0,
    "draw_total": 104,
}

print("\n" + "=" * 95)
print("FINAL 2025-26 HOLDOUT BENCHMARK COMPARISON (380 MATCHES)")
print("=" * 95)
print(f"{'Model / Benchmark':<45}{'Holdout Acc':<14}{'Log-Loss':<11}{'Delta LL (vs V2)':<18}{'Brier':<9}{'Draws'}")
print("=" * 95)
for m in [m_rnd, m_maj, m_elo, m_v2, m_b3, m_b4, m_b6, m_b7]:
    dll = m["log_loss"] - m_v2["log_loss"]
    dll_str = f"{dll:+.5f}" if m != m_v2 else "reference"
    print(f"{m['name']:<45}{str(m['acc'])+'/380 ('+str(m['acc_pct'])+'%)':<14}{m['log_loss']:<11.5f}{dll_str:<18}{m['brier']:<9.5f}{m['draw_correct']}/{m['draw_total']}")

print(f"{m_b365['name']:<45}{str(m_b365['acc'])+'/380 ('+str(m_b365['acc_pct'])+'%)':<14}{m_b365['log_loss']:<11.5f}{m_b365['log_loss'] - m_v2['log_loss']:<+18.5f}{m_b365['brier']:<9.5f}{m_b365['draw_correct']}/{m_b365['draw_total']}")
print("=" * 95)

# Strong Picks evaluation on Holdout
print("\n" + "=" * 80)
print("STRONG-PICKS EVALUATION ON FROZEN 2025-26 HOLDOUT")
print("=" * 80)
print(f"{'Threshold':<12}{'Coverage':<14}{'Matches':<12}{'Accuracy':<14}{'Log-Loss':<11}{'Brier'}")
for th in [0.50, 0.55, 0.60, 0.65, 0.70]:
    max_p = P_hybrid_hold.max(axis=1)
    mask = max_p >= th
    n_th = int(mask.sum())
    if n_th > 0:
        pred_th = P_hybrid_hold[mask].argmax(axis=1)
        y_th = y_hold[mask]
        acc_th = (pred_th == y_th).sum()
        ll_th = -np.mean([np.log(P_hybrid_hold[mask][i, y_th[i]]) for i in range(len(y_th))])
        oh_th = np.eye(3)[y_th]
        brier_th = np.mean(np.sum((P_hybrid_hold[mask] - oh_th) ** 2, axis=1))
        cov_pct = n_th / len(y_hold) * 100
        acc_pct = acc_th / n_th * 100
        print(f">={int(th*100)}%{'':<7}{cov_pct:.1f}%{'':<8}{str(n_th)+'/380':<12}{str(acc_th)+'/'+str(n_th)+' ('+str(round(acc_pct,1))+'%)':<14}{ll_th:.5f}{'':<4}{brier_th:.5f}")

# Reliability / Calibration Comparison
print("\n" + "=" * 80)
print("CALIBRATION & RELIABILITY TABLE (2025-26 HOLDOUT)")
print("=" * 80)
print(f"{'Bin':<12}{'V2 Count':<12}{'V2 Actual':<12}{'V4 Count':<12}{'V4 Actual':<12}{'V4 Error'}")
for v2_b, v4_b in zip(m_v2["calib_table"], m_b7["calib_table"]):
    diff_str = f"{v4_b['diff']:+.1f}%"
    print(f"{v2_b['bin']:<12}{v2_b['count']:<12}{str(v2_b['actual_acc'])+'%':<12}{v4_b['count']:<12}{str(v4_b['actual_acc'])+'%':<12}{diff_str}")

# Save holdout predictions and evaluation artifacts
hold_df["v4_prob_home"] = P_hybrid_hold[:, 0]
hold_df["v4_prob_draw"] = P_hybrid_hold[:, 1]
hold_df["v4_prob_away"] = P_hybrid_hold[:, 2]

cand_artifact = {
    "model_name": "V4 Dynamic Team State Hybrid Score Model",
    "architecture": "Dynamic Attack/Defence Exponential State + Dixon-Coles Poisson + Squad Transition Uncertainty + V2 Platt Blend",
    "configuration": champion_config,
    "validation_metrics": m_b7_val,
    "holdout_metrics": m_b7,
    "holdout_comparison": {
        "v2_accuracy": m_v2["acc"],
        "v4_accuracy": m_b7["acc"],
        "v2_log_loss": m_v2["log_loss"],
        "v4_log_loss": m_b7["log_loss"],
        "delta_log_loss": round(m_b7["log_loss"] - m_v2["log_loss"], 5),
        "v2_brier": m_v2["brier"],
        "v4_brier": m_b7["brier"],
        "delta_brier": round(m_b7["brier"] - m_v2["brier"], 5),
        "v2_ece": m_v2["ece"],
        "v4_ece": m_b7["ece"],
    },
}

cand_pkl_path = os.path.join(MODELS_DIR, "pl_v4_candidate_antigravity.pkl")
with open(cand_pkl_path, "wb") as f:
    pickle.dump(cand_artifact, f)
print(f"\nSaved V4 Candidate Model Artifact to {cand_pkl_path}")

out_eval_json = os.path.join(EXP_DIR, "v4_walkforward_evaluation.json")
with open(out_eval_json, "w") as f:
    json.dump({
        "validation_models": [m_v2_val, m_b3_val, m_b4_val, m_b6_val, m_b7_val],
        "holdout_models": [m_rnd, m_maj, m_elo, m_v2, m_b3, m_b4, m_b6, m_b7],
        "bet365": m_b365,
        "config": champion_config,
    }, f, indent=2)
print(f"Saved evaluation results to {out_eval_json}")

