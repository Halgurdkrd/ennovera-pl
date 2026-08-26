"""Phase 7: Ultra-Fast Vectorized Poisson & Dixon-Coles Score Distribution Engine.
Computes expected goals (lambda_home, lambda_away) from dynamic team states,
computes bivariate score distributions with Dixon-Coles low-score correlation via vectorized 3D tensors,
and derives clean, calibrated match probabilities P(H), P(D), P(A).

Run from ennovera-pl/ directory:
python scripts/v4_score_model.py
"""
import os
import sys
import numpy as np
from scipy.special import factorial

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

MAX_GOALS = 9  # Support score lines 0-0 to 9-9
GOALS_ARR = np.arange(MAX_GOALS + 1)
FACT_ARR = factorial(GOALS_ARR)

def compute_score_probs_batch(lambda_h_arr, lambda_a_arr, rho=-0.05, uncertainty_arr=None):
    """
    Vectorized computation of 1X2 match probabilities across N matches.
    lambda_h_arr, lambda_a_arr: shape (N,)
    Returns probs of shape (N, 3) -> [P(H), P(D), P(A)]
    """
    lh = np.clip(np.asarray(lambda_h_arr, dtype=float), 0.1, 8.0)
    la = np.clip(np.asarray(lambda_a_arr, dtype=float), 0.1, 8.0)
    N = len(lh)
    
    # If uncertainty is active, widen the effective lambda variance
    if uncertainty_arr is not None:
        unc = np.clip(np.asarray(uncertainty_arr, dtype=float), 0.0, 0.6)
        # Soft dispersion adjustment: blends toward league equilibrium for uncertain teams
        lh = (1.0 - 0.4 * unc) * lh + 0.4 * unc * 1.35 * 1.18
        la = (1.0 - 0.4 * unc) * la + 0.4 * unc * 1.35
        
    # Shape: (N, 10)
    # p_x[i, x] = lh[i]^x * exp(-lh[i]) / x!
    p_x = (lh[:, None] ** GOALS_ARR[None, :]) * np.exp(-lh[:, None]) / FACT_ARR[None, :]
    p_y = (la[:, None] ** GOALS_ARR[None, :]) * np.exp(-la[:, None]) / FACT_ARR[None, :]
    
    # Outer product -> shape (N, 10, 10)
    S = p_x[:, :, None] * p_y[:, None, :]
    
    # Apply Dixon-Coles low-score adjustments
    if abs(rho) > 1e-6:
        # S[:, 0, 0] *= max(0, 1 - lh * la * rho)
        tau_00 = np.clip(1.0 - lh * la * rho, 0.0, 3.0)
        tau_01 = np.clip(1.0 + lh * rho, 0.0, 3.0)
        tau_10 = np.clip(1.0 + la * rho, 0.0, 3.0)
        tau_11 = np.clip(1.0 - rho, 0.0, 3.0)
        
        S[:, 0, 0] *= tau_00
        S[:, 0, 1] *= tau_01
        S[:, 1, 0] *= tau_10
        S[:, 1, 1] *= tau_11
        
    # Normalize score matrix
    sums = S.sum(axis=(1, 2), keepdims=True)
    S /= np.where(sums > 0, sums, 1.0)
    
    # Lower triangle (x > y): Home win
    tril_mask = np.tril(np.ones((MAX_GOALS + 1, MAX_GOALS + 1), dtype=bool), -1)
    # Diagonal (x == y): Draw
    diag_mask = np.eye(MAX_GOALS + 1, dtype=bool)
    # Upper triangle (x < y): Away win
    triu_mask = np.triu(np.ones((MAX_GOALS + 1, MAX_GOALS + 1), dtype=bool), 1)
    
    p_h = S[:, tril_mask].sum(axis=1)
    p_d = S[:, diag_mask].sum(axis=1)
    p_a = S[:, triu_mask].sum(axis=1)
    
    probs = np.stack([p_h, p_d, p_a], axis=1)
    probs = np.clip(probs, 1e-9, 1.0)
    return probs / probs.sum(axis=1, keepdims=True)

if __name__ == "__main__":
    # Test batch
    lh = np.array([1.85, 1.20, 2.40])
    la = np.array([1.05, 1.10, 0.70])
    p = compute_score_probs_batch(lh, la, rho=-0.06)
    print("Vectorized Score Probs:")
    for i in range(len(lh)):
        print(f"  Match {i}: lh={lh[i]}, la={la[i]} -> P(H)={p[i,0]*100:.1f}%, P(D)={p[i,1]*100:.1f}%, P(A)={p[i,2]*100:.1f}%")

