"""Step 3: Independent Signal Screening on Development Split (2022-23 + 2023-24, 760 matches).
Evaluates each candidate FPL signal independently on top of Walk-Forward V2 base probabilities.
Uses vectorized block/round-aware bootstrap resampling (1,000 iterations) for 95% CI on Delta Log-Loss.

Run from ennovera-pl/ directory.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

DATA_PATH = os.path.join(_ROOT, "data/v3_walkforward/fpl_leakfree_features.csv")
OUT_DIR = os.path.join(_ROOT, "data/v3_walkforward")
EXP_DIR = os.path.join(_ROOT, "data/experiments")
os.makedirs(EXP_DIR, exist_ok=True)
np.random.seed(13)

df = pd.read_csv(DATA_PATH)
df["y"] = df["ftr"].map({"H": 0, "D": 1, "A": 2})

# Restrict strictly to development split: 2022-23 + 2023-24 (760 matches)
dev_df = df[df["season"].isin(["2022-23", "2023-24"])].copy().reset_index(drop=True)
print(f"Loaded Development Split: {len(dev_df)} matches ({dev_df['season'].value_counts().to_dict()})")

y_dev = dev_df["y"].values
P_v2 = dev_df[["v2_prob_home", "v2_prob_draw", "v2_prob_away"]].values
P_v2 = np.clip(P_v2, 1e-9, 1)
P_v2 = P_v2 / P_v2.sum(axis=1, keepdims=True)

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

base_m = calc_metrics(P_v2, y_dev)
print(f"\nWalk-Forward V2 Baseline on Dev Split (760m):")
print(f"  Acc: {base_m['acc']}/760 ({base_m['acc_pct']}%), Log-Loss: {base_m['log_loss']}, Brier: {base_m['brier']}, Draws: {base_m['draw_correct']}/{base_m['draw_total']}")

# ---------------------------------------------------------------------------
# Signal Adjustment Formulation
# ---------------------------------------------------------------------------
def apply_signal_logit(P_base, feat_vals, beta):
    eps = 1e-7
    P = np.clip(P_base, eps, 1 - eps)
    log_p = np.log(P)
    
    adj_log_p = log_p.copy()
    adj_log_p[:, 0] += beta * feat_vals
    adj_log_p[:, 2] -= beta * feat_vals
    
    adj_p = np.exp(adj_log_p - np.max(adj_log_p, axis=1, keepdims=True))
    adj_p = adj_p / adj_p.sum(axis=1, keepdims=True)
    return adj_p

# Pre-compute block indices for fast vectorized bootstrap
dev_df["block"] = dev_df["season"] + "_GW" + dev_df["gw"].astype(str)
unique_blocks = dev_df["block"].unique()
block_indices = [np.where(dev_df["block"].values == b)[0] for b in unique_blocks]
n_blocks = len(block_indices)

def bootstrap_delta_ll_fast(P_base, P_adj, y, n_boot=1000):
    rng = np.random.default_rng(13)
    deltas = []
    
    # Precompute per-sample log-losses
    ll_base_all = -np.log(P_base[np.arange(len(y)), y])
    ll_adj_all = -np.log(P_adj[np.arange(len(y)), y])
    diff_all = ll_adj_all - ll_base_all
    
    # Pre-calculate block sums and lengths
    block_sums = np.array([diff_all[idx].sum() for idx in block_indices])
    block_lens = np.array([len(idx) for idx in block_indices])
    
    for _ in range(n_boot):
        sample_b = rng.integers(0, n_blocks, size=n_blocks)
        total_diff = block_sums[sample_b].sum()
        total_len = block_lens[sample_b].sum()
        deltas.append(total_diff / total_len)
        
    ci_lower = float(np.percentile(deltas, 2.5))
    ci_upper = float(np.percentile(deltas, 97.5))
    return round(ci_lower, 5), round(ci_upper, 5)

# ---------------------------------------------------------------------------
# Candidate Signals to Screen
# ---------------------------------------------------------------------------
CANDIDATE_SIGNALS = {
    "S1_prior_strength": {
        "col": "s1_strength_diff",
        "desc": "Prior-season FPL Strength Composite (lagged S-1)",
    },
    "S1_atk_strength": {
        "col": "s1_atk_diff",
        "desc": "Prior-season FPL Attack Strength (lagged S-1)",
    },
    "S1_def_strength": {
        "col": "s1_def_diff",
        "desc": "Prior-season FPL Defence Strength (lagged S-1)",
    },
    "S2_rolling_xg": {
        "col": "s2_roll_xg_diff",
        "desc": "Rolling Real Team xG Differential (last 5 GWs < N)",
    },
    "S3_rolling_xa": {
        "col": "s3_roll_xa_diff",
        "desc": "Rolling Real Team xA Differential (last 5 GWs < N)",
    },
    "S4_rolling_xga": {
        "col": "s4_roll_xga_diff",
        "desc": "Rolling Defensive xGA Differential (last 5 GWs < N)",
    },
    "S5_squad_value": {
        "col": "s5_squad_val_diff",
        "desc": "Contemporaneous Squad Value Differential (£100M units)",
    },
    "S6_player_dependency": {
        "col": "s6_dependency_diff",
        "desc": "Player Dependency Differential (Top-2 xG+xA Share)",
    },
    "S7_rolling_ict": {
        "col": "s7_roll_ict_diff",
        "desc": "Rolling Team ICT Index Differential",
    },
    "S8_rolling_clean_sheet": {
        "col": "s8_roll_cs_diff",
        "desc": "Rolling Clean Sheet Rate Differential",
    },
    "S_opp_adj_xg": {
        "col": "s_opp_adj_xg_diff",
        "desc": "Opponent-Adjusted Rolling xG Differential",
    },
}

screening_results = {}

print("\n" + "=" * 95)
print(f"{'Signal':<24}{'Beta':<8}{'Acc':<10}{'Log-Loss':<11}{'Delta LL':<11}{'95% Bootstrap CI':<22}{'Brier':<9}{'Status'}")
print("=" * 95)

for sig_name, sig_info in CANDIDATE_SIGNALS.items():
    col = sig_info["col"]
    feat_vals = dev_df[col].values
    
    # Optimize beta on dev split to minimize log-loss
    def loss_func(b):
        adj_p = apply_signal_logit(P_v2, feat_vals, b[0])
        return -np.mean([np.log(adj_p[i, y_dev[i]]) for i in range(len(y_dev))])
    
    res = minimize(loss_func, x0=[0.0], method="Nelder-Mead")
    opt_beta = float(res.x[0])
    
    adj_P = apply_signal_logit(P_v2, feat_vals, opt_beta)
    m = calc_metrics(adj_P, y_dev)
    
    delta_ll = m["log_loss"] - base_m["log_loss"]
    ci_low, ci_high = bootstrap_delta_ll_fast(P_v2, adj_P, y_dev)
    
    # Signal status rule:
    # Meaningful improvement if Delta LL < -0.0005 and CI upper bound <= 0.0005
    is_improving = delta_ll < -0.0003
    is_stable = ci_high <= 0.0002
    if is_improving and is_stable:
        status = "PROMISING"
    elif is_improving:
        status = "MARGINAL"
    else:
        status = "NO GAIN"
        
    ci_str = f"[{ci_low:+.5f}, {ci_high:+.5f}]"
    print(f"{sig_name:<24}{opt_beta:<8.3f}{str(m['acc'])+'/760':<10}{m['log_loss']:<11.5f}{delta_ll:<+11.5f}{ci_str:<22}{m['brier']:<9.5f}{status}")
    
    screening_results[sig_name] = {
        "description": sig_info["desc"],
        "column": col,
        "opt_beta": round(opt_beta, 4),
        "acc": m["acc"],
        "acc_pct": m["acc_pct"],
        "log_loss": m["log_loss"],
        "delta_ll": round(delta_ll, 5),
        "ci_95": [ci_low, ci_high],
        "brier": m["brier"],
        "delta_brier": round(m["brier"] - base_m["brier"], 5),
        "draws_called": m["draw_called"],
        "status": status,
    }

out_json = os.path.join(EXP_DIR, "v3_signal_screening_dev.json")
with open(out_json, "w") as f:
    json.dump({"baseline_v2": base_m, "signals": screening_results}, f, indent=2)
print(f"\nSaved screening results to {out_json}")

