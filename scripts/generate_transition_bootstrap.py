"""Generate m1_transition_bootstrap.json with rigorous subgroup bootstrap statistics."""
import os
import json
import numpy as np
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
EXP_DIR = os.path.join(_ROOT, "data/experiments")
FEAT_DIR = os.path.join(_ROOT, "data/v5_features")

df_xi = pd.read_csv(os.path.join(FEAT_DIR, "m1_expected_xi_features.csv"))
from m1_model_tournament import p_f2_all, p_m1_d_all, y_all, all_m

def compute_ll_vec(P, y):
    return -np.log(np.clip(P[np.arange(len(y)), y], 1e-9, 1))

ll_f2 = compute_ll_vec(p_f2_all, y_all)
ll_m1 = compute_ll_vec(p_m1_d_all, y_all)
d_ll = ll_m1 - ll_f2

df_all_xi = df_xi[all_m].reset_index(drop=True)
prom_mask = (df_all_xi["is_promoted"] == 1.0).values
turn_mask = ((df_all_xi["cont_h"] < 0.75) | (df_all_xi["cont_a"] < 0.75)).values

rng = np.random.default_rng(2026)
def calc_sg_bs(mask):
    sub_d = d_ll[mask]
    N = len(sub_d)
    means = [float(np.mean(sub_d[rng.choice(N, size=N, replace=True)])) for _ in range(5000)]
    return {
        "match_count": int(N),
        "mean_delta_ll": round(float(np.mean(sub_d)), 5),
        "ci_95": [round(float(np.percentile(means, 2.5)), 5), round(float(np.percentile(means, 97.5)), 5)],
        "p_m1_better_pct": round(float(np.mean(np.array(means) < 0.0)) * 100.0, 1)
    }

trans_bs_data = {
    "promoted_teams_bootstrap": calc_sg_bs(prom_mask),
    "high_turnover_teams_bootstrap": calc_sg_bs(turn_mask),
    "overlap_analysis": {
        "promoted_count": int(prom_mask.sum()),
        "high_turnover_count": int(turn_mask.sum()),
        "exact_overlap_count": int((prom_mask & turn_mask).sum()),
        "overlap_percentage": round(float((prom_mask & turn_mask).sum() / max(1, prom_mask.sum()) * 100.0), 1),
        "independent_non_promoted_high_turnover_matches": int((turn_mask & (~prom_mask)).sum()),
        "independent_non_promoted_delta_ll": round(float(np.mean(d_ll[turn_mask & (~prom_mask)])), 5)
    }
}

with open(os.path.join(EXP_DIR, "m1_transition_bootstrap.json"), "w") as f:
    json.dump(trans_bs_data, f, indent=2)

print("Saved data/experiments/m1_transition_bootstrap.json successfully.")
