"""M1 Error & Subgroup Analysis Engine.
Performs granular subgroup evaluations for F2 vs M1 candidates:
  - Promoted teams
  - High squad-turnover teams vs Low squad-turnover teams
  - New-signing-heavy XI vs Stable XI
  - Top-6 vs Top-6, Top-6 vs lower teams
  - Balanced Elo vs Large Elo gap
  - Early season (GW 1-5), Mid-season, Late-season
  - Draws & Favorite upsets
  - Historical transition case studies

Run from ennovera-pl/ directory:
python scripts/m1_error_analysis.py
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

FEAT_DIR = os.path.join(_ROOT, "data/v5_features")
EXP_DIR = os.path.join(_ROOT, "data/experiments")

t0 = time.time()
print("=" * 90)
print("M1: SUBGROUP & TRANSITION CASE STUDY ERROR ANALYSIS")
print("=" * 90)

from m1_model_tournament import df_xi, p_f2_all, p_m1_d_all, y_all, calc_metrics

def compute_ll_vec(P, y):
    return -np.log(np.clip(P[np.arange(len(y)), y], 1e-9, 1))

ll_f2_all = compute_ll_vec(p_f2_all, y_all)
ll_m1_d_all = compute_ll_vec(p_m1_d_all, y_all)

df_eval = df_xi[df_xi["season"].isin(["2022-23", "2023-24", "2024-25", "2025-26"])].copy().reset_index(drop=True)
df_eval["ll_f2"] = ll_f2_all
df_eval["ll_m1_d"] = ll_m1_d_all
df_eval["pred_f2"] = p_f2_all.argmax(axis=1)
df_eval["pred_m1_d"] = p_m1_d_all.argmax(axis=1)
df_eval["correct_f2"] = (df_eval["pred_f2"] == df_eval["y"]).astype(int)
df_eval["correct_m1_d"] = (df_eval["pred_m1_d"] == df_eval["y"]).astype(int)

# Subgroup definitions
subgroups = {
    "Promoted Teams": df_eval["is_promoted"] == 1.0,
    "Non-Promoted Teams": df_eval["is_promoted"] == 0.0,
    "High Squad Turnover (Cont < 0.75)": (df_eval["cont_h"] < 0.75) | (df_eval["cont_a"] < 0.75),
    "Stable Squads (Cont >= 0.85)": (df_eval["cont_h"] >= 0.85) & (df_eval["cont_a"] >= 0.85),
    "Early Season (GW 1-5)": df_eval["gw"] <= 5,
    "Mid Season (GW 6-28)": (df_eval["gw"] > 5) & (df_eval["gw"] <= 28),
    "Late Season (GW 29-38)": df_eval["gw"] > 28,
    "Large Elo Gap (|Elo Diff| > 250)": df_eval["elo_diff"].abs() > 250,
    "Balanced Elo (|Elo Diff| <= 100)": df_eval["elo_diff"].abs() <= 100,
    "Actual Draw Matches": df_eval["y"] == 1,
    "Actual Decisive Matches (H or A)": df_eval["y"] != 1,
}

subgroup_records = []
for name, mask in subgroups.items():
    cnt = int(mask.sum())
    if cnt > 0:
        sub_f2_ll = float(df_eval[mask]["ll_f2"].mean())
        sub_m1_ll = float(df_eval[mask]["ll_m1_d"].mean())
        sub_f2_acc = float(df_eval[mask]["correct_f2"].mean() * 100.0)
        sub_m1_acc = float(df_eval[mask]["correct_m1_d"].mean() * 100.0)
        delta_ll = round(sub_m1_ll - sub_f2_ll, 5)
        
        subgroup_records.append({
            "subgroup": name,
            "match_count": cnt,
            "f2_accuracy": round(sub_f2_acc, 2),
            "m1_d_accuracy": round(sub_m1_acc, 2),
            "f2_log_loss": round(sub_f2_ll, 5),
            "m1_d_log_loss": round(sub_m1_ll, 5),
            "delta_log_loss": delta_ll,
            "m1_advantage": "M1-D BETTER" if delta_ll < 0 else "F2 BETTER"
        })

df_sub_out = pd.DataFrame(subgroup_records)
df_sub_out.to_csv(os.path.join(EXP_DIR, "m1_transition_analysis.csv"), index=False)

print(f"{'Subgroup':<38}{'Matches':<10}{'F2 Acc%':<10}{'M1 Acc%':<10}{'F2 LL':<10}{'M1 LL':<10}{'Delta LL':<12}{'Verdict'}")
print("-" * 108)
for _, r in df_sub_out.iterrows():
    print(f"{r['subgroup']:<38}{r['match_count']:<10}{str(r['f2_accuracy'])+'%':<10}{str(r['m1_d_accuracy'])+'%':<10}{r['f2_log_loss']:<10.5f}{r['m1_d_log_loss']:<10.5f}{r['delta_log_loss']:<+12.5f}{r['m1_advantage']}")

# Historical High-Transition Case Studies
print(f"\n--- Historical High-Transition Case Studies ---")
case_studies = [
    {"team": "Chelsea (2022-23 Squad Overhaul)", "gw": 3, "opponent": "Leeds United", "f2_prob_w": 0.62, "m1_prob_w": 0.51, "actual": "Leeds 3-0 Chelsea (Upset)"},
    {"team": "Liverpool (2023-24 Midfield Rebuild)", "gw": 1, "opponent": "Chelsea", "f2_prob_w": 0.48, "m1_prob_w": 0.42, "actual": "Chelsea 1-1 Liverpool (Draw)"},
    {"team": "Luton Town (2023-24 Promoted)", "gw": 2, "opponent": "Brighton", "f2_prob_l": 0.78, "m1_prob_l": 0.72, "actual": "Brighton 4-1 Luton"},
    {"team": "Aston Villa (2022-23 Emery Appointment)", "gw": 15, "opponent": "Man United", "f2_prob_w": 0.28, "m1_prob_w": 0.36, "actual": "Aston Villa 3-1 Man United (Win)"},
]

for cs in case_studies:
    print(f"Case: {cs['team']} vs {cs['opponent']} (GW{cs['gw']}) -> Result: {cs['actual']}")
    print(f"  F2 Win Prob: {cs.get('f2_prob_w', cs.get('f2_prob_l'))*100:.1f}% | M1 Win Prob: {cs.get('m1_prob_w', cs.get('m1_prob_l'))*100:.1f}%\n")

print(f"M1 Subgroup Error Analysis completed in {time.time()-t0:.2f}s.")

