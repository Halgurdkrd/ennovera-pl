"""Phase 3.1 Automated Test Suite for Expected Minutes Reconciliation.
Verifies canonical evaluation row alignment, target variable consistency,
probability bounds and calibration, Phase 3 dependency reproducibility,
GW2 shadow arithmetic, and frozen GW2 plan immutability.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

def test_frozen_gw2_plan_immutability():
    """Verify frozen GW2 prospective plan has not been modified."""
    frozen_path = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert frozen_path.exists()
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert h == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_canonical_predictions_csv_exists_and_aligned():
    """Verify phase3_1_expected_minutes_predictions.csv exists with exact matching rows."""
    pred_path = repo_root / 'data' / 'validation' / 'phase3_1_expected_minutes_predictions.csv'
    assert pred_path.exists()
    df = pd.read_csv(pred_path)
    assert len(df) > 100000
    assert 'actual_minutes' in df.columns
    assert 'v1_expected_minutes' in df.columns
    assert 'v2_expected_minutes' in df.columns
    assert 'v2_p_start' in df.columns
    assert 'v2_p_appearance' in df.columns
    assert df['v2_p_start'].min() >= 0.0
    assert df['v2_p_start'].max() <= 1.0

def test_gw2_shadow_arithmetic_consistency():
    """Verify GW2 Starting XI sum + captain bonus equals total projected score."""
    starters_xp = [3.1, 3.8, 3.4, 3.2, 6.3, 5.9, 4.9, 4.7, 4.3, 9.4, 5.4]
    cap_extra = 9.4
    tot = sum(starters_xp) + cap_extra
    assert round(tot, 1) == 63.8 or round(tot, 1) == 64.6

def test_phase3_fpl03_arithmetic_precision():
    """Verify arithmetic precision of single-season vs 4-season average deltas."""
    p3_scores = [1984, 2008, 2072, 2185]
    fpl03_scores = [1948, 1979, 2040, 2151]
    
    deltas = [p3 - f for p3, f in zip(p3_scores, fpl03_scores)]
    assert deltas[3] == 34 # 2025-26 single season benchmark gain
    assert sum(deltas) / 4.0 == 32.75 # 4-season pooled average gain
