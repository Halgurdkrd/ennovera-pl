"""M1 Player-First Team Strength Builder.
Produces current player-derived team strength ratings and match differentials.
Evaluates role-balanced aggregations (GK, DEF, MID, FWD) and interaction terms.

Run from ennovera-pl/ directory:
python scripts/m1_player_team_strength.py
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

FEAT_DIR = os.path.join(_ROOT, "data/v5_features")
EXP_DIR = os.path.join(_ROOT, "data/experiments")

t0 = time.time()
print("=" * 90)
print("M1: PLAYER-FIRST TEAM STRENGTH MODEL (ZERO TEAM IDENTITY AUDIT)")
print("=" * 90)

df_xi = pd.read_csv(os.path.join(FEAT_DIR, "m1_expected_xi_features.csv"))
print(f"Loaded {len(df_xi)} Expected XI match records.")

# Splits
dev_mask = df_xi["season"].isin(["2022-23", "2023-24"])
val_mask = df_xi["season"] == "2024-25"
hold_mask = df_xi["season"] == "2025-26"

# Feature subsets
# Pure Player State Features (ZERO Elo, ZERO club identity, ZERO multi-season history)
player_only_cols = [
    "diff_xi_att", "diff_xi_cre", "diff_xi_def", "diff_xi_gk", "diff_xi_xgi",
    "diff_depth", "diff_cont", "diff_unc", "inter_att_cre", "inter_opp_att_def", "inter_cont_att"
]

X_dev_p = df_xi[dev_mask][player_only_cols].values
y_dev = df_xi[dev_mask]["y"].values

X_val_p = df_xi[val_mask][player_only_cols].values
y_val = df_xi[val_mask]["y"].values

X_hold_p = df_xi[hold_mask][player_only_cols].values
y_hold = df_xi[hold_mask]["y"].values

# Train Regularized Player-Only Multinomial Logistic Model
clf_player_only = LogisticRegression(C=0.5, penalty="l2", random_state=42, max_iter=1000)
clf_player_only.fit(X_dev_p, y_dev)

p_player_val = clf_player_only.predict_proba(X_val_p)
p_player_hold = clf_player_only.predict_proba(X_hold_p)

def eval_ll_acc(P, y):
    pred = P.argmax(axis=1)
    acc = float((pred == y).mean() * 100.0)
    ll = float(-np.mean([np.log(np.clip(P[i, y[i]], 1e-9, 1)) for i in range(len(y))]))
    return acc, ll

val_acc, val_ll = eval_ll_acc(p_player_val, y_val)
hold_acc, hold_ll = eval_ll_acc(p_player_hold, y_hold)

print(f"\n--- M1-A Pure Player-Only Model (Zero Club Identity / Zero Elo) ---")
print(f"Validation (2024-25): Accuracy = {val_acc:.2f}% | Log-Loss = {val_ll:.5f}")
print(f"Research Test (2025-26): Accuracy = {hold_acc:.2f}% | Log-Loss = {hold_ll:.5f}")
print(f"Coefficients (Home Win logit):")
for col, coef in zip(player_only_cols, clf_player_only.coef_[0]):
    print(f"  {col:<20}: {coef:+.4f}")

print(f"\nPlayer-First Team Strength Builder completed in {time.time()-t0:.2f}s.")

