"""V5.1 Signal Screening Engine: Independent Testing of Expected XI Features over Frozen V4.
Evaluates each player-state feature family on Dev (2022-24, 760m) and Validation (2024-25, 380m).
Computes delta Log-Loss, delta Brier, and accuracy over frozen V4.

Run from ennovera-pl/ directory:
python scripts/v5_signal_screening.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from v4_score_model import compute_score_probs_batch

FEAT_PATH = os.path.join(_ROOT, "data/v5_features/team_expected_xi_state.csv")
WF_V2_PATH = os.path.join(_ROOT, "data/v3_walkforward/v2_walkforward_predictions.csv")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
os.makedirs(EXP_DIR, exist_ok=True)

print("=" * 80)
print("V5.1 SIGNAL SCREENING OVER FROZEN V4 BASELINE")
print("=" * 80)

# Load data
df = pd.read_csv(FEAT_PATH)
df_v2 = pd.read_csv(WF_V2_PATH)
m = pd.merge(df, df_v2[["season", "home", "away", "v2_prob_home", "v2_prob_draw", "v2_prob_away"]], on=["season", "home", "away"])
m["y"] = m["ftr"].map({"H": 0, "D": 1, "A": 2})

# Frozen V4 Probability Generator
def get_v4_base_probs(sub_df):
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
    
    P_v4 = 0.0928 * P_score + 0.9072 * P_v2
    return P_v4

# Metric Evaluator
def eval_metrics(P, y):
    P = np.clip(P, 1e-9, 1); P /= P.sum(axis=1, keepdims=True)
    pred = P.argmax(axis=1)
    acc = int((pred == y).sum())
    ll = float(-np.mean([np.log(P[i, y[i]]) for i in range(len(y))]))
    oh = np.eye(3)[y]
    brier = float(np.mean(np.sum((P - oh) ** 2, axis=1)))
    return acc, round(ll, 5), round(brier, 5)

# Splits
dev_mask = m["season"].isin(["2022-23", "2023-24"]).values
val_mask = (m["season"] == "2024-25").values

y_dev = m["y"].values[dev_mask]
y_val = m["y"].values[val_mask]

P_v4_dev = get_v4_base_probs(m[dev_mask])
P_v4_val = get_v4_base_probs(m[val_mask])

acc_v4_dev, ll_v4_dev, br_v4_dev = eval_metrics(P_v4_dev, y_dev)
acc_v4_val, ll_v4_val, br_v4_val = eval_metrics(P_v4_val, y_val)

print(f"Frozen V4 Baseline:")
print(f"  Dev (2022-24, 760m): Acc = {acc_v4_dev}/760 ({acc_v4_dev/760*100:.2f}%) | LL = {ll_v4_dev:.5f} | Brier = {br_v4_dev:.5f}")
print(f"  Val (2024-25, 380m): Acc = {acc_v4_val}/380 ({acc_v4_val/380*100:.2f}%) | LL = {ll_v4_val:.5f} | Brier = {br_v4_val:.5f}")

# Signals to screen
signals = [
    ("Signal A: Expected XI Attack", ["diff_exp_xi_att"]),
    ("Signal B: Expected XI Creativity", ["diff_exp_xi_creativity"]),
    ("Signal C: Expected XI Total xGI", ["diff_exp_xi_xgi"]),
    ("Signal D: Expected XI Squad Value", ["diff_exp_xi_value"]),
    ("Signal E: XI Continuity Differential", ["home_xi_continuity", "away_xi_continuity"]),
    ("Signal F: Bench Depth Differential", ["home_exp_bench_value", "away_exp_bench_value"]),
    ("Signal G: Top-Creator Dependency", ["home_top_creator_dep", "away_top_creator_dep"]),
    ("Signal H: Combined XI Attack & Creativity", ["diff_exp_xi_att", "diff_exp_xi_creativity"]),
    ("Signal I: Combined XI Attack, Depth & Continuity", ["diff_exp_xi_att", "diff_exp_xi_creativity", "diff_exp_xi_value", "home_xi_continuity", "away_xi_continuity"]),
]

screen_results = []
print("\n" + "=" * 105)
print(f"{'Signal Family':<45}{'Dev LL':<12}{'Delta Dev LL':<14}{'Val LL':<12}{'Delta Val LL':<14}{'Val Acc'}")
print("=" * 105)

for sig_name, sig_cols in signals:
    X_dev = m.loc[dev_mask, sig_cols].values
    X_val = m.loc[val_mask, sig_cols].values
    
    # Fit a low-complexity residual correction on Dev logits
    # Convert V4 base probs to logit offsets
    eps = 1e-6
    logit_h_dev = np.log(P_v4_dev[:, 0] / (P_v4_dev[:, 1] + eps))
    logit_a_dev = np.log(P_v4_dev[:, 2] / (P_v4_dev[:, 1] + eps))
    
    # We fit a ridge multinomial model combining base logits + candidate signal
    X_comb_dev = np.column_stack([logit_h_dev, logit_a_dev, X_dev])
    
    logit_h_val = np.log(P_v4_val[:, 0] / (P_v4_val[:, 1] + eps))
    logit_a_val = np.log(P_v4_val[:, 2] / (P_v4_val[:, 1] + eps))
    X_comb_val = np.column_stack([logit_h_val, logit_a_val, X_val])
    
    # L2 regularized logistic regression (C=0.1 to avoid overfit)
    clf = LogisticRegression(C=0.1, max_iter=500, random_state=13)
    clf.fit(X_comb_dev, y_dev)
    
    P_sig_dev = clf.predict_proba(X_comb_dev)
    P_sig_val = clf.predict_proba(X_comb_val)
    
    # Conservative shrinkage blend (0.15 signal + 0.85 V4)
    w_sig = 0.15
    P_final_dev = w_sig * P_sig_dev + (1.0 - w_sig) * P_v4_dev
    P_final_val = w_sig * P_sig_val + (1.0 - w_sig) * P_v4_val
    
    acc_d, ll_d, br_d = eval_metrics(P_final_dev, y_dev)
    acc_v, ll_v, br_v = eval_metrics(P_final_val, y_val)
    
    d_ll_dev = ll_d - ll_v4_dev
    d_ll_val = ll_v - ll_v4_val
    
    print(f"{sig_name:<45}{ll_d:<12.5f}{d_ll_dev:<+14.5f}{ll_v:<12.5f}{d_ll_val:<+14.5f}{str(acc_v)+'/380 ('+str(round(acc_v/380*100,2))+'%)'}")
    
    screen_results.append({
        "signal": sig_name,
        "features": sig_cols,
        "dev_ll": ll_d,
        "delta_dev_ll": round(d_ll_dev, 5),
        "val_ll": ll_v,
        "delta_val_ll": round(d_ll_val, 5),
        "val_acc": acc_v,
        "val_brier": br_v,
    })

out_screen_path = os.path.join(EXP_DIR, "v5_1_signal_tests.json")
with open(out_screen_path, "w") as f:
    json.dump(screen_results, f, indent=2)
print(f"\nSaved Signal Screening Results to {out_screen_path}")

