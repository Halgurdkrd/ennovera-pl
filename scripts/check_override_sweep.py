"""Diagnostic check on override thresholds across Validation and Holdout."""
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

EXP_DIR = "data/experiments"
FEAT_DIR = "data/v5_features"

df_frozen = pd.read_csv(os.path.join(EXP_DIR, "rootcause03_frozen_expert_predictions.csv"))
df_master = df_frozen.copy()
dev_m = df_master["season"].isin(["2022-23", "2023-24"]).values
val_m = (df_master["season"] == "2024-25").values
hold_m = (df_master["season"] == "2025-26").values

y_dev = df_master[dev_m]["y"].values
y_val = df_master[val_m]["y"].values
y_hold = df_master[hold_m]["y"].values

from run_rootcause04_pipeline import X_override_all, P_CORE_all, P_TACT_all, P_HYB_all, dis_core_tact, choice_tact, y_tact_override, dis_core_hyb, choice_hyb, y_hyb_override

# Logistic model
clf_t = LogisticRegression(C=0.1, penalty="l2", random_state=42).fit(X_override_all[dev_m & choice_tact], y_tact_override[dev_m & choice_tact])
p_val_t = clf_t.predict_proba(X_override_all[val_m])[:, 1]
p_hold_t = clf_t.predict_proba(X_override_all[hold_m])[:, 1]

pred_c_val = P_CORE_all[val_m].argmax(axis=1)
pred_c_hold = P_CORE_all[hold_m].argmax(axis=1)
pred_t_val = P_TACT_all[val_m].argmax(axis=1)
pred_t_hold = P_TACT_all[hold_m].argmax(axis=1)

print(f"Base Core Validation: {(pred_c_val == y_val).sum()}/380 ({(pred_c_val == y_val).mean()*100:.2f}%)")
print(f"Base Core Holdout:    {(pred_c_hold == y_hold).sum()}/380 ({(pred_c_hold == y_hold).mean()*100:.2f}%)")

print("\nTactical Threshold Sweep (Validation vs Holdout):")
for tau in [0.40, 0.45, 0.50, 0.52, 0.55, 0.58, 0.60, 0.65, 0.70, 0.75, 0.80]:
    over_v = dis_core_tact[val_m] & (p_val_t >= tau)
    p_v = pred_c_val.copy()
    p_v[over_v] = pred_t_val[over_v]
    corr_v = (p_v == y_val).sum()
    
    over_h = dis_core_tact[hold_m] & (p_hold_t >= tau)
    p_h = pred_c_hold.copy()
    p_h[over_h] = pred_t_hold[over_h]
    corr_h = (p_h == y_hold).sum()
    
    w_to_c_h = ((pred_c_hold != y_hold) & (p_h == y_hold) & over_h).sum()
    c_to_w_h = ((pred_c_hold == y_hold) & (p_h != y_hold) & over_h).sum()
    print(f"tau={tau:.2f} | Val: {corr_v}/380 (overs={over_v.sum()}) | Hold: {corr_h}/380 (overs={over_h.sum()}, w->c={w_to_c_h}, c->w={c_to_w_h}, net={w_to_c_h - c_to_w_h})")

