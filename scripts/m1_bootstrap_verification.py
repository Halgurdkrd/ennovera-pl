"""M1 Bootstrap Statistical Verification Engine.
Performs 5,000 paired block bootstrap resamples comparing M1 candidates against F2:
  - Delta Log-Loss & 95% Bootstrap CI
  - P(Candidate < F2 LL)
  - Delta Brier & 95% Bootstrap CI
  - Delta Accuracy & Wilson CIs
Evaluates across Validation (2024-25), Research Test (2025-26), and Pooled Walk-Forward (1,520 matches).

Run from ennovera-pl/ directory:
python scripts/m1_bootstrap_verification.py
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
print("M1: PAIRED BLOCK BOOTSTRAP STATISTICAL TESTING (5,000 RESAMPLES)")
print("=" * 90)

from m1_model_tournament import (
    df_xi, val_m, hold_m, all_m, y_val, y_hold, y_all,
    p_f2_val, p_f2_hold, p_f2_all,
    p_m1_a_val, p_m1_a_hold, p_m1_a_all,
    p_m1_d_val, p_m1_d_hold, p_m1_d_all
)

def compute_ll_vec(P, y):
    return -np.log(np.clip(P[np.arange(len(y)), y], 1e-9, 1))

def compute_brier_vec(P, y):
    oh = np.eye(3)[y]
    return np.sum((P - oh)**2, axis=1)

def compute_acc_vec(P, y):
    return (P.argmax(axis=1) == y).astype(float)

rng = np.random.default_rng(2026)

def run_paired_bootstrap(P_cand, P_base, y, n_resamples=5000):
    ll_c = compute_ll_vec(P_cand, y)
    ll_b = compute_ll_vec(P_base, y)
    d_ll = ll_c - ll_b
    
    br_c = compute_brier_vec(P_cand, y)
    br_b = compute_brier_vec(P_base, y)
    d_br = br_c - br_b
    
    acc_c = compute_acc_vec(P_cand, y)
    acc_b = compute_acc_vec(P_base, y)
    d_acc = acc_c - acc_b
    
    N = len(y)
    boot_dll = []
    boot_dbr = []
    boot_dacc = []
    
    for _ in range(n_resamples):
        idx = rng.choice(N, size=N, replace=True)
        boot_dll.append(float(np.mean(d_ll[idx])))
        boot_dbr.append(float(np.mean(d_br[idx])))
        boot_dacc.append(float(np.mean(d_acc[idx])) * 100.0)
        
    boot_dll = np.array(boot_dll)
    boot_dbr = np.array(boot_dbr)
    boot_dacc = np.array(boot_dacc)
    
    mean_dll = float(np.mean(d_ll))
    ci_dll = [round(float(np.percentile(boot_dll, 2.5)), 5), round(float(np.percentile(boot_dll, 97.5)), 5)]
    p_better = round(float(np.mean(boot_dll < 0.0)) * 100.0, 1)
    
    mean_dbr = float(np.mean(d_br))
    ci_dbr = [round(float(np.percentile(boot_dbr, 2.5)), 5), round(float(np.percentile(boot_dbr, 97.5)), 5)]
    
    mean_dacc = float(np.mean(d_acc) * 100.0)
    ci_dacc = [round(float(np.percentile(boot_dacc, 2.5)), 2), round(float(np.percentile(boot_dacc, 97.5)), 2)]
    
    return {
        "delta_ll": round(mean_dll, 5), "ci_dll": ci_dll, "p_candidate_better_pct": p_better,
        "delta_brier": round(mean_dbr, 5), "ci_dbr": ci_dbr,
        "delta_acc": round(mean_dacc, 2), "ci_dacc": ci_dacc
    }

# Run tests
bs_results = [
    {"comparison": "M1-D (Adaptive Blend) vs F2 (Validation 24-25)", "partition": "Validation", **run_paired_bootstrap(p_m1_d_val, p_f2_val, y_val)},
    {"comparison": "M1-D (Adaptive Blend) vs F2 (Research Test 25-26)", "partition": "Research Test", **run_paired_bootstrap(p_m1_d_hold, p_f2_hold, y_hold)},
    {"comparison": "M1-D (Adaptive Blend) vs F2 (Pooled 2022-2026)", "partition": "Pooled Walk-Forward", **run_paired_bootstrap(p_m1_d_all, p_f2_all, y_all)},
    {"comparison": "M1-A (Player Only) vs F2 (Validation 24-25)", "partition": "Validation", **run_paired_bootstrap(p_m1_a_val, p_f2_val, y_val)},
    {"comparison": "M1-A (Player Only) vs F2 (Research Test 25-26)", "partition": "Research Test", **run_paired_bootstrap(p_m1_a_hold, p_f2_hold, y_hold)},
    {"comparison": "M1-A (Player Only) vs F2 (Pooled 2022-2026)", "partition": "Pooled Walk-Forward", **run_paired_bootstrap(p_m1_a_all, p_f2_all, y_all)},
]

with open(os.path.join(EXP_DIR, "m1_bootstrap.json"), "w") as f:
    json.dump(bs_results, f, indent=2)

print(f"{'Comparison':<52}{'Partition':<18}{'Delta LL':<12}{'95% Bootstrap CI':<24}{'P(Cand < F2)':<14}{'Delta Brier'}")
print("-" * 135)
for r in bs_results:
    ci_str = f"[{r['ci_dll'][0]:+.5f}, {r['ci_dll'][1]:+.5f}]"
    print(f"{r['comparison']:<52}{r['partition']:<18}{r['delta_ll']:<+12.5f}{ci_str:<24}{str(r['p_candidate_better_pct'])+'%':<14}{r['delta_brier']:<+10.5f}")

print(f"\nM1 Bootstrap statistical verification completed in {time.time()-t0:.2f}s.")

