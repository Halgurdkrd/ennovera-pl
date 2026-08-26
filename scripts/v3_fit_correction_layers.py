"""Step 4: Multi-Signal Model Fitting & Validation Selection (2024-25).
Fits regularized candidate correction architectures strictly on 2022-23 + 2023-24 (760 matches).
Evaluates candidate architectures on 2024-25 (380 matches).
Selects ONE champion candidate and FREEZES all parameters.

Run from ennovera-pl/ directory.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression, RidgeClassifier

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

DATA_PATH = os.path.join(_ROOT, "data/v3_walkforward/fpl_leakfree_features.csv")
OUT_DIR = os.path.join(_ROOT, "data/v3_walkforward")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
MODELS_DIR = os.path.join(_ROOT, "data/models")
os.makedirs(EXP_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
np.random.seed(13)

df = pd.read_csv(DATA_PATH)
df["y"] = df["ftr"].map({"H": 0, "D": 1, "A": 2})

dev_df = df[df["season"].isin(["2022-23", "2023-24"])].copy().reset_index(drop=True)
val_df = df[df["season"] == "2024-25"].copy().reset_index(drop=True)

y_dev = dev_df["y"].values
y_val = val_df["y"].values

def get_p_v2(sub_df):
    p = sub_df[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
    p = np.clip(p, 1e-9, 1)
    return p / p.sum(axis=1, keepdims=True)

P_v2_dev = get_p_v2(dev_df)
P_v2_val = get_p_v2(val_df)

def calc_metrics(P, y):
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
    return {
        "acc": acc,
        "acc_pct": round(acc / len(y) * 100, 2),
        "log_loss": round(ll, 5),
        "brier": round(brier, 5),
        "draw_called": draw_called,
        "draw_correct": draw_correct,
        "draw_total": total_draws,
    }

base_dev_m = calc_metrics(P_v2_dev, y_dev)
base_val_m = calc_metrics(P_v2_val, y_val)

print("=" * 80)
print("MULTI-SIGNAL MODEL SELECTION ON VALIDATION SPLIT (2024-25)")
print("=" * 80)
print(f"Base Walk-Forward V2 on Dev (760m): Acc {base_dev_m['acc']}/760 ({base_dev_m['acc_pct']}%), LL {base_dev_m['log_loss']}, Brier {base_dev_m['brier']}")
print(f"Base Walk-Forward V2 on Val (380m): Acc {base_val_m['acc']}/380 ({base_val_m['acc_pct']}%), LL {base_val_m['log_loss']}, Brier {base_val_m['brier']}")

# ---------------------------------------------------------------------------
# Candidate 1: Best Single Signal (Rolling xA)
# ---------------------------------------------------------------------------
def fit_candidate_1(dev, val):
    f_dev = dev["s3_roll_xa_diff"].values
    f_val = val["s3_roll_xa_diff"].values
    
    def loss(b):
        log_p = np.log(np.clip(P_v2_dev, 1e-7, 1-1e-7)).copy()
        log_p[:, 0] += b[0] * f_dev
        log_p[:, 2] -= b[0] * f_dev
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        p = p / p.sum(axis=1, keepdims=True)
        return -np.mean([np.log(p[i, y_dev[i]]) for i in range(len(y_dev))])
    
    res = minimize(loss, x0=[0.4], method="Nelder-Mead")
    b_opt = float(res.x[0])
    
    def predict(P_base, f_vals):
        log_p = np.log(np.clip(P_base, 1e-7, 1-1e-7)).copy()
        log_p[:, 0] += b_opt * f_vals
        log_p[:, 2] -= b_opt * f_vals
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        return p / p.sum(axis=1, keepdims=True)
        
    return {
        "name": "Candidate 1: Rolling xA Overlay",
        "params": {"beta_xa": b_opt},
        "predict_func": lambda sub_df, P_base: predict(P_base, sub_df["s3_roll_xa_diff"].values),
    }

# ---------------------------------------------------------------------------
# Candidate 2: Opponent-Adjusted xG + Rolling xA Composite
# ---------------------------------------------------------------------------
def fit_candidate_2(dev, val):
    f1_dev = dev["s_opp_adj_xg_diff"].values
    f2_dev = dev["s3_roll_xa_diff"].values
    
    f1_val = val["s_opp_adj_xg_diff"].values
    f2_val = val["s3_roll_xa_diff"].values
    
    def loss(b):
        log_p = np.log(np.clip(P_v2_dev, 1e-7, 1-1e-7)).copy()
        shift = b[0] * f1_dev + b[1] * f2_dev
        log_p[:, 0] += shift
        log_p[:, 2] -= shift
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        p = p / p.sum(axis=1, keepdims=True)
        # L2 penalty
        reg = 0.001 * (b[0]**2 + b[1]**2)
        return -np.mean([np.log(p[i, y_dev[i]]) for i in range(len(y_dev))]) + reg
    
    res = minimize(loss, x0=[0.1, 0.3], method="Nelder-Mead")
    b1, b2 = float(res.x[0]), float(res.x[1])
    
    def predict(P_base, f1, f2):
        log_p = np.log(np.clip(P_base, 1e-7, 1-1e-7)).copy()
        shift = b1 * f1 + b2 * f2
        log_p[:, 0] += shift
        log_p[:, 2] -= shift
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        return p / p.sum(axis=1, keepdims=True)
        
    return {
        "name": "Candidate 2: Opp-Adj xG + xA Composite",
        "params": {"beta_opp_adj_xg": b1, "beta_xa": b2},
        "predict_func": lambda sub_df, P_base: predict(P_base, sub_df["s_opp_adj_xg_diff"].values, sub_df["s3_roll_xa_diff"].values),
    }

# ---------------------------------------------------------------------------
# Candidate 3: Multi-Signal Regularized Linear Overlay (Surviving Signals)
# (Prior strength S1 + Opp-Adj xG + xA + xGA + Squad Value S5)
# ---------------------------------------------------------------------------
def fit_candidate_3(dev, val):
    cols = ["s1_strength_diff", "s_opp_adj_xg_diff", "s3_roll_xa_diff", "s4_roll_xga_diff", "s5_squad_val_diff"]
    X_dev = dev[cols].values
    
    def loss(b):
        log_p = np.log(np.clip(P_v2_dev, 1e-7, 1-1e-7)).copy()
        shift = X_dev @ b
        log_p[:, 0] += shift
        log_p[:, 2] -= shift
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        p = p / p.sum(axis=1, keepdims=True)
        # L2 ridge regularization
        reg = 0.05 * np.sum(b**2)
        return -np.mean([np.log(p[i, y_dev[i]]) for i in range(len(y_dev))]) + reg
    
    res = minimize(loss, x0=np.zeros(len(cols)), method="L-BFGS-B")
    b_opt = res.x
    
    def predict(P_base, X_mat):
        log_p = np.log(np.clip(P_base, 1e-7, 1-1e-7)).copy()
        shift = X_mat @ b_opt
        # Bound maximum adjustment to +/- 0.06 to prevent overconfidence
        shift = np.clip(shift, -0.6, 0.6)
        log_p[:, 0] += shift
        log_p[:, 2] -= shift
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        return p / p.sum(axis=1, keepdims=True)
        
    return {
        "name": "Candidate 3: Multi-Signal Regularized Overlay (5 signals)",
        "params": {c: round(float(w), 4) for c, w in zip(cols, b_opt)},
        "predict_func": lambda sub_df, P_base: predict(P_base, sub_df[cols].values),
    }

# ---------------------------------------------------------------------------
# Candidate 4: 3-Class Multinomial Logit Overlay with Draw Gate Calibration
# ---------------------------------------------------------------------------
def fit_candidate_4(dev, val):
    cols = ["s1_strength_diff", "s_opp_adj_xg_diff", "s3_roll_xa_diff", "s5_squad_val_diff"]
    X_dev = dev[cols].values
    
    # Feature for draw logit: absolute difference / closeness of teams
    abs_xg_diff = np.abs(dev["s_opp_adj_xg_diff"].values)
    
    def loss(params):
        # params: [w_home (4), w_draw (1)]
        b_h = params[:4]
        b_d = params[4]
        
        log_p = np.log(np.clip(P_v2_dev, 1e-7, 1-1e-7)).copy()
        shift_h = X_dev @ b_h
        log_p[:, 0] += shift_h
        log_p[:, 2] -= shift_h
        log_p[:, 1] += b_d * (1.0 - np.clip(abs_xg_diff, 0, 1.5))
        
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        p = p / p.sum(axis=1, keepdims=True)
        reg = 0.05 * (np.sum(b_h**2) + b_d**2)
        return -np.mean([np.log(p[i, y_dev[i]]) for i in range(len(y_dev))]) + reg
    
    res = minimize(loss, x0=np.zeros(5), method="L-BFGS-B")
    b_opt = res.x
    b_h_opt = b_opt[:4]
    b_d_opt = b_opt[4]
    
    def predict(P_base, sub_df):
        X_mat = sub_df[cols].values
        abs_diff = np.abs(sub_df["s_opp_adj_xg_diff"].values)
        log_p = np.log(np.clip(P_base, 1e-7, 1-1e-7)).copy()
        shift_h = np.clip(X_mat @ b_h_opt, -0.6, 0.6)
        log_p[:, 0] += shift_h
        log_p[:, 2] -= shift_h
        log_p[:, 1] += b_d_opt * (1.0 - np.clip(abs_diff, 0, 1.5))
        p = np.exp(log_p - np.max(log_p, axis=1, keepdims=True))
        return p / p.sum(axis=1, keepdims=True)
        
    return {
        "name": "Candidate 4: Multinomial H/D/A Logit Overlay",
        "params": {
            "home_weights": {c: round(float(w), 4) for c, w in zip(cols, b_h_opt)},
            "draw_closeness_beta": round(float(b_d_opt), 4),
        },
        "predict_func": lambda sub_df, P_base: predict(P_base, sub_df),
    }

# Fit all candidate models on Dev Split
candidates = [
    fit_candidate_1(dev_df, val_df),
    fit_candidate_2(dev_df, val_df),
    fit_candidate_3(dev_df, val_df),
    fit_candidate_4(dev_df, val_df),
]

val_results = {}
print("\n" + "=" * 90)
print(f"{'Candidate Architecture':<45}{'Val Acc':<10}{'Val LL':<11}{'Delta LL':<11}{'Brier':<9}{'Draws'}")
print("=" * 90)
print(f"{'Walk-Forward V2 Baseline':<45}{str(base_val_m['acc'])+'/380':<10}{base_val_m['log_loss']:<11.5f}{'+0.00000':<11}{base_val_m['brier']:<9.5f}{base_val_m['draw_correct']}/{base_val_m['draw_total']}")

best_cand = None
best_val_ll = 999.0

for cand in candidates:
    P_val_adj = cand["predict_func"](val_df, P_v2_val)
    m = calc_metrics(P_val_adj, y_val)
    d_ll = m["log_loss"] - base_val_m["log_loss"]
    
    print(f"{cand['name']:<45}{str(m['acc'])+'/380':<10}{m['log_loss']:<11.5f}{d_ll:<+11.5f}{m['brier']:<9.5f}{m['draw_correct']}/{m['draw_total']}")
    val_results[cand["name"]] = {
        "params": cand["params"],
        "val_metrics": m,
        "delta_ll_val": round(d_ll, 5),
    }
    
    if m["log_loss"] < best_val_ll:
        best_val_ll = m["log_loss"]
        best_cand = cand

print("=" * 90)
print(f"\nWINNING VALIDATION CHAMPION: {best_cand['name']}")
print(f"Validation Log-Loss: {best_val_ll:.5f} (Delta LL: {best_val_ll - base_val_m['log_loss']:+.5f})")
print(f"Fitted Parameters: {json.dumps(best_cand['params'], indent=2)}")

# Save the frozen configuration and parameters
frozen_config = {
    "champion_name": best_cand["name"],
    "fitted_on": "2022-23 + 2023-24 (760 matches)",
    "selected_on": "2024-25 (380 matches)",
    "frozen_parameters": best_cand["params"],
    "validation_metrics": val_results[best_cand["name"]]["val_metrics"],
    "all_candidates": val_results,
}

out_config_path = os.path.join(EXP_DIR, "v3_frozen_configuration.json")
with open(out_config_path, "w") as f:
    json.dump(frozen_config, f, indent=2)
print(f"Saved frozen configuration to {out_config_path}")

