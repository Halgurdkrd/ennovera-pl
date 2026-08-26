"""V4 Live Shadow Mode Performance Evaluator.
Processes logged shadow results to monitor live V2 vs V4 metrics, delta log-loss, Brier,
calibration, draw handling, and Strong-Picks performance with exact Wilson 95% CIs.

Run from ennovera-pl/ directory:
python scripts/v4_shadow_evaluator.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.stats import norm

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

SHADOW_DIR = os.path.join(_ROOT, "data/shadow")
PRED_FILE = os.path.join(SHADOW_DIR, "v4_shadow_predictions.csv")
RESULT_FILE = os.path.join(SHADOW_DIR, "v4_shadow_results.csv")

def wilson_score_interval(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0
    z = norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return round(float(center - margin) * 100, 2), round(float(center + margin) * 100, 2)

def evaluate_shadow_season():
    if not os.path.exists(RESULT_FILE) or not os.path.exists(PRED_FILE):
        print("Shadow tables not initialized or no fixtures logged.")
        return
        
    df_pred = pd.read_csv(PRED_FILE)
    df_res = pd.read_csv(RESULT_FILE)
    
    merged = pd.merge(df_pred, df_res[["fixture_id", "actual_result", "home_goals", "away_goals", "v2_correct", "v4_correct", "v2_match_logloss", "v4_match_logloss", "v2_match_brier", "v4_match_brier"]], on="fixture_id")
    
    n_completed = len(merged)
    if n_completed == 0:
        print("No completed fixtures logged in shadow mode yet.")
        return
        
    print("=" * 80)
    print(f"ENNOVERA V4 SHADOW MODE LIVE EVALUATION REPORT ({n_completed} MATCHES COMPLETED)")
    print("=" * 80)
    
    v2_acc = merged["v2_correct"].sum()
    v4_acc = merged["v4_correct"].sum()
    v2_ll = merged["v2_match_logloss"].mean()
    v4_ll = merged["v4_match_logloss"].mean()
    v2_br = merged["v2_match_brier"].mean()
    v4_br = merged["v4_match_brier"].mean()
    
    print(f"Overall Match Winner Accuracy:")
    print(f"  V2: {v2_acc}/{n_completed} ({v2_acc/n_completed*100:.2f}%) | LL: {v2_ll:.5f} | Brier: {v2_br:.5f}")
    print(f"  V4: {v4_acc}/{n_completed} ({v4_acc/n_completed*100:.2f}%) | LL: {v4_ll:.5f} | Brier: {v4_br:.5f}")
    print(f"  Delta: Acc = {v4_acc-v2_acc:+d} matches | Delta LL = {v4_ll-v2_ll:+.5f} | Delta Brier = {v4_br-v2_br:+.5f}")
    
    print("\n" + "-" * 80)
    print("Strong Picks Performance Tiers:")
    print(f"{'Tier':<12}{'Picks':<12}{'Coverage':<12}{'Correct':<12}{'Accuracy':<14}{'95% Wilson CI':<18}{'LL'}")
    print("-" * 80)
    
    for th in [0.50, 0.55, 0.60, 0.65]:
        col = f"v4_strong_pick_{int(th*100)}"
        picks_df = merged[merged[col] == 1]
        n_p = len(picks_df)
        if n_p > 0:
            corr = int(picks_df["v4_correct"].sum())
            acc = corr / n_p * 100
            cov = n_p / n_completed * 100
            ll = picks_df["v4_match_logloss"].mean()
            ci_low, ci_high = wilson_score_interval(corr, n_p)
            print(f">={int(th*100)}%{'':<7}{str(n_p)+'/'+str(n_completed):<12}{cov:.1f}%{'':<6}{str(corr)+'/'+str(n_p):<12}{acc:.2f}%{'':<6}[{ci_low:.1f}%, {ci_high:.1f}%]{'':<2}{ll:.5f}")
        else:
            print(f">={int(th*100)}%{'':<7}0/{n_completed}{'':<8}0.0%{'':<6}0/0{'':<9}0.0%{'':<8}--{'':<16}--")
            
    print("=" * 80)

if __name__ == "__main__":
    evaluate_shadow_season()

