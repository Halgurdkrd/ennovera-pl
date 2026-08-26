"""M1 Model Tournament Engine.
Implements the required model tournament:
  - Baseline F2: Frozen research benchmark
  - M1-A: Player Only (Zero team identity / Zero Elo)
  - M1-B: Player + Learned Historical Prior (Weight fit strictly on Dev 2022-24)
  - M1-C: F2 + Player Expert (Independent expert blend fit on Dev 2022-24)
  - M1-D: Adaptive Player/History Blend (Gating on squad turnover, promoted status, XI continuity, uncertainty)

Run from ennovera-pl/ directory:
python scripts/m1_model_tournament.py
"""
import os
import sys
import json
import time
import pickle
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

FEAT_DIR = os.path.join(_ROOT, "data/v5_features")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
MOD_DIR = os.path.join(_ROOT, "data/models")
os.makedirs(EXP_DIR, exist_ok=True)
os.makedirs(MOD_DIR, exist_ok=True)

t0 = time.time()
print("=" * 90)
print("M1: MODEL TOURNAMENT (F2 vs M1-A vs M1-B vs M1-C vs M1-D)")
print("=" * 90)

df_xi = pd.read_csv(os.path.join(FEAT_DIR, "m1_expected_xi_features.csv"))

# Partitions
dev_m = df_xi["season"].isin(["2022-23", "2023-24"])
val_m = df_xi["season"] == "2024-25"
hold_m = df_xi["season"] == "2025-26"
all_m = df_xi["season"].isin(["2022-23", "2023-24", "2024-25", "2025-26"])

# Targets
y_dev = df_xi[dev_m]["y"].values
y_val = df_xi[val_m]["y"].values
y_hold = df_xi[hold_m]["y"].values
y_all = df_xi[all_m]["y"].values

# Compute Baseline F2 Probabilities
def compute_f2_probs(df_sub):
    probs = []
    for _, r in df_sub.iterrows():
        elo_diff = float(r["elo_diff"])
        e_h = 1 / (1 + 10 ** (-(elo_diff + 100) / 400))
        p_elo = np.array([e_h * 0.74, 0.26, (1 - e_h) * 0.74]); p_elo /= p_elo.sum()
        
        diff_xg = float(r["diff_xi_att"])
        p_f0 = np.array([1 / (1 + np.exp(-(0.80 * diff_xg + 0.30))), 0.26, 1 / (1 + np.exp(0.80 * diff_xg - 0.30))]); p_f0 /= p_f0.sum()
        
        cont = float(r["cont_h"]) * 0.5 + float(r["cont_a"]) * 0.5
        gw = int(r["gw"])
        w = np.clip(1 / (1 + np.exp(-(1.5 * cont + 0.5 * np.log(max(1, gw))))), 0.40, 0.90)
        p = w * p_elo + (1.0 - w) * p_f0
        probs.append(p / p.sum())
    return np.array(probs)

p_f2_dev = compute_f2_probs(df_xi[dev_m])
p_f2_val = compute_f2_probs(df_xi[val_m])
p_f2_hold = compute_f2_probs(df_xi[hold_m])
p_f2_all = compute_f2_probs(df_xi[all_m])

# Model M1-A: Pure Player Only (Zero Team Identity)
player_only_cols = [
    "diff_xi_att", "diff_xi_cre", "diff_xi_def", "diff_xi_gk", "diff_xi_xgi",
    "diff_depth", "diff_cont", "diff_unc", "inter_att_cre", "inter_opp_att_def", "inter_cont_att"
]
X_dev_p = df_xi[dev_m][player_only_cols].values
X_val_p = df_xi[val_m][player_only_cols].values
X_hold_p = df_xi[hold_m][player_only_cols].values
X_all_p = df_xi[all_m][player_only_cols].values

clf_m1_a = LogisticRegression(C=0.5, penalty="l2", random_state=42, max_iter=1000)
clf_m1_a.fit(X_dev_p, y_dev)

p_m1_a_dev = clf_m1_a.predict_proba(X_dev_p)
p_m1_a_val = clf_m1_a.predict_proba(X_val_p)
p_m1_a_hold = clf_m1_a.predict_proba(X_hold_p)
p_m1_a_all = clf_m1_a.predict_proba(X_all_p)

# Model M1-B: Player + Learned Historical Prior (Weight fit strictly on Dev 2022-24)
def compute_elo_probs(df_sub):
    probs = []
    for _, r in df_sub.iterrows():
        elo_diff = float(r["elo_diff"])
        e_h = 1 / (1 + 10 ** (-(elo_diff + 100) / 400))
        p = np.array([e_h * 0.74, 0.26, (1 - e_h) * 0.74]); p /= p.sum()
        probs.append(p)
    return np.array(probs)

p_elo_dev = compute_elo_probs(df_xi[dev_m])
p_elo_val = compute_elo_probs(df_xi[val_m])
p_elo_hold = compute_elo_probs(df_xi[hold_m])
p_elo_all = compute_elo_probs(df_xi[all_m])

# Optimize fixed blending weight on Dev 2022-24
def obj_blend(w):
    p = w[0] * p_elo_dev + (1.0 - w[0]) * p_m1_a_dev
    return -np.mean([np.log(np.clip(p[i, y_dev[i]], 1e-9, 1)) for i in range(len(y_dev))])

res_b = minimize(obj_blend, [0.50], bounds=[(0.0, 1.0)], method="L-BFGS-B")
w_learned_b = float(res_b.x[0])
print(f"Model M1-B Learned Historical Prior Weight on Dev (2022-24): {w_learned_b*100:.1f}% Elo, {(1-w_learned_b)*100:.1f}% Player")

p_m1_b_dev = w_learned_b * p_elo_dev + (1.0 - w_learned_b) * p_m1_a_dev
p_m1_b_val = w_learned_b * p_elo_val + (1.0 - w_learned_b) * p_m1_a_val
p_m1_b_hold = w_learned_b * p_elo_hold + (1.0 - w_learned_b) * p_m1_a_hold
p_m1_b_all = w_learned_b * p_elo_all + (1.0 - w_learned_b) * p_m1_a_all

# Model M1-C: F2 + Player Expert Blend (Fit on Dev 2022-24)
def obj_expert(w):
    p = w[0] * p_f2_dev + (1.0 - w[0]) * p_m1_a_dev
    return -np.mean([np.log(np.clip(p[i, y_dev[i]], 1e-9, 1)) for i in range(len(y_dev))])

res_c = minimize(obj_expert, [0.80], bounds=[(0.0, 1.0)], method="L-BFGS-B")
w_learned_c = float(res_c.x[0])
print(f"Model M1-C Learned Expert Blend Weight on Dev (2022-24): {w_learned_c*100:.1f}% F2, {(1-w_learned_c)*100:.1f}% Player Expert")

p_m1_c_dev = w_learned_c * p_f2_dev + (1.0 - w_learned_c) * p_m1_a_dev
p_m1_c_val = w_learned_c * p_f2_val + (1.0 - w_learned_c) * p_m1_a_val
p_m1_c_hold = w_learned_c * p_f2_hold + (1.0 - w_learned_c) * p_m1_a_hold
p_m1_c_all = w_learned_c * p_f2_all + (1.0 - w_learned_c) * p_m1_a_all

# Model M1-D: Adaptive Player/History Blend (Gating Network)
# When squad continuity is low or team is promoted or uncertainty is high -> shift weight dynamically to Player Model
def compute_m1_d_probs(df_sub, p_base_expert, p_player_expert):
    probs = []
    for idx, (_, r) in enumerate(df_sub.iterrows()):
        cont = float(r["cont_h"]) * 0.5 + float(r["cont_a"]) * 0.5
        unc = float(r["unc_h"]) * 0.5 + float(r["unc_a"]) * 0.5
        is_prom = float(r["is_promoted"])
        gw = int(r["gw"])
        
        # Adaptive gating: weight on historical F2 decreases for promoted teams and low continuity
        gate_logit = 1.80 * cont - 1.20 * is_prom - 0.90 * unc + 0.40 * np.log(max(1, gw))
        w_f2_dyn = np.clip(1 / (1 + np.exp(-gate_logit)), 0.30, 0.95)
        
        p = w_f2_dyn * p_base_expert[idx] + (1.0 - w_f2_dyn) * p_player_expert[idx]
        probs.append(p / p.sum())
    return np.array(probs)

p_m1_d_dev = compute_m1_d_probs(df_xi[dev_m], p_f2_dev, p_m1_a_dev)
p_m1_d_val = compute_m1_d_probs(df_xi[val_m], p_f2_val, p_m1_a_val)
p_m1_d_hold = compute_m1_d_probs(df_xi[hold_m], p_f2_hold, p_m1_a_hold)
p_m1_d_all = compute_m1_d_probs(df_xi[all_m], p_f2_all, p_m1_a_all)

# Save candidate model artifact
m1_artifact = {
    "model_name": "pl_m1_candidate",
    "clf_player_only": clf_m1_a,
    "w_learned_b": w_learned_b,
    "w_learned_c": w_learned_c,
    "player_features": player_only_cols
}
with open(os.path.join(MOD_DIR, "pl_m1_candidate.pkl"), "wb") as f:
    pickle.dump(m1_artifact, f)

# Evaluation function
def calc_metrics(P, y):
    pred = P.argmax(axis=1)
    acc = float((pred == y).mean() * 100.0)
    ll = float(-np.mean([np.log(np.clip(P[i, y[i]], 1e-9, 1)) for i in range(len(y))]))
    oh = np.eye(3)[y]
    brier = float(np.mean(np.sum((P - oh) ** 2, axis=1)))
    
    # ECE
    conf = P.max(axis=1)
    correct = (pred == y).astype(float)
    bin_edges = np.linspace(0.33, 1.0, 10)
    ece = 0.0
    for b in range(len(bin_edges)-1):
        in_b = (conf >= bin_edges[b]) & (conf < bin_edges[b+1])
        if in_b.sum() > 0:
            ece += (in_b.sum() / len(y)) * abs(correct[in_b].mean() - conf[in_b].mean())
            
    # Draw Recall
    draw_rec = float(((pred == 1) & (y == 1)).sum() / max(1, (y == 1).sum()) * 100.0)
    
    # Strong Picks
    sp55 = (conf >= 0.55); sp55_acc = float((pred[sp55] == y[sp55]).mean() * 100.0) if sp55.sum()>0 else 0.0
    sp60 = (conf >= 0.60); sp60_acc = float((pred[sp60] == y[sp60]).mean() * 100.0) if sp60.sum()>0 else 0.0
    sp65 = (conf >= 0.65); sp65_acc = float((pred[sp65] == y[sp65]).mean() * 100.0) if sp65.sum()>0 else 0.0
    
    return {
        "accuracy": round(acc, 2), "log_loss": round(ll, 5), "brier": round(brier, 5), "ece": round(ece, 4),
        "draw_recall": round(draw_rec, 2),
        "sp55_cnt": int(sp55.sum()), "sp55_acc": round(sp55_acc, 2), "sp55_cov": round(sp55.sum()/len(y)*100, 1),
        "sp60_cnt": int(sp60.sum()), "sp60_acc": round(sp60_acc, 2), "sp60_cov": round(sp60.sum()/len(y)*100, 1),
        "sp65_cnt": int(sp65.sum()), "sp65_acc": round(sp65_acc, 2), "sp65_cov": round(sp65.sum()/len(y)*100, 1),
    }

models_eval = {
    "Candidate F2 (Baseline)": (p_f2_dev, p_f2_val, p_f2_hold, p_f2_all),
    "M1-A: Player Only (Zero Identity)": (p_m1_a_dev, p_m1_a_val, p_m1_a_hold, p_m1_a_all),
    "M1-B: Player + Learned Prior": (p_m1_b_dev, p_m1_b_val, p_m1_b_hold, p_m1_b_all),
    "M1-C: F2 + Player Expert Blend": (p_m1_c_dev, p_m1_c_val, p_m1_c_hold, p_m1_c_all),
    "M1-D: Adaptive Player/History Blend": (p_m1_d_dev, p_m1_d_val, p_m1_d_hold, p_m1_d_all),
}

tournament_records = []
for name, (p_d, p_v, p_h, p_a) in models_eval.items():
    m_dev = calc_metrics(p_d, y_dev)
    m_val = calc_metrics(p_v, y_val)
    m_hold = calc_metrics(p_h, y_hold)
    m_all = calc_metrics(p_a, y_all)
    tournament_records.append({
        "model": name,
        "dev_acc": m_dev["accuracy"], "dev_ll": m_dev["log_loss"],
        "val_acc": m_val["accuracy"], "val_ll": m_val["log_loss"],
        "hold_acc": m_hold["accuracy"], "hold_ll": m_hold["log_loss"], "hold_brier": m_hold["brier"], "hold_ece": m_hold["ece"],
        "hold_draw_rec": m_hold["draw_recall"],
        "sp55_acc": m_hold["sp55_acc"], "sp55_cov": m_hold["sp55_cov"],
        "sp60_acc": m_hold["sp60_acc"], "sp60_cov": m_hold["sp60_cov"], "sp60_cnt": m_hold["sp60_cnt"],
        "sp65_acc": m_hold["sp65_acc"], "sp65_cov": m_hold["sp65_cov"],
        "pooled_acc": m_all["accuracy"], "pooled_ll": m_all["log_loss"]
    })

df_tourn = pd.DataFrame(tournament_records)
df_tourn.to_csv(os.path.join(EXP_DIR, "m1_tournament_results.csv"), index=False)

print(f"\n{'Model':<36}{'Val Acc%':<10}{'Val LL':<10}{'Hold Acc%':<11}{'Hold LL':<11}{'Hold Brier':<12}{'Strong Picks (>=60%)'}")
print("-" * 105)
for _, r in df_tourn.iterrows():
    sp_str = f"{r['sp60_acc']}% ({r['sp60_cnt']} picks, {r['sp60_cov']}%)"
    print(f"{r['model']:<36}{str(r['val_acc'])+'%':<10}{r['val_ll']:<10.5f}{str(r['hold_acc'])+'%':<11}{r['hold_ll']:<11.5f}{r['hold_brier']:<12.4f}{sp_str}")

print(f"\nM1 Model Tournament finished in {time.time()-t0:.2f}s.")

