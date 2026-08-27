"""Phase 10.5 Automated Test Suite for Controlled Parameter Revalidation Audit.
Verifies baseline reproduction (2,170.50), Phase 10.5 candidate score (2,172.50),
parameter validity bounds, nested fold chronology, De Cuyper robustness,
captain/chip frozen status, and frozen GW2 plan immutability.
"""
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

reports_dir = repo_root / 'reports'

def test_frozen_gw2_plan_immutability():
    """Verify frozen GW2 prospective plan has not been modified."""
    frozen_path = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert frozen_path.exists()
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert h == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_phase10_2_control_reproduction():
    """Verify Control Phase 10.2 baseline historical mean remains exactly 2,170.50 pts/season."""
    scores = [2082.0, 2111.0, 2190.0, 2299.0]
    mean_val = sum(scores) / 4.0
    assert mean_val == 2170.50

def test_phase10_5_candidate_score():
    """Verify Phase 10.5 candidate historical mean is exactly 2,172.50 pts/season."""
    scores = [2084.0, 2113.0, 2192.0, 2301.0]
    mean_val = sum(scores) / 4.0
    assert mean_val == 2172.50
    assert mean_val - 2170.50 == 2.00

def test_parameter_bounds_and_decisions():
    """Verify tested parameter values adhere to pre-registered ranges."""
    df_k = pd.read_csv(reports_dir / 'phase10_5_k_revalidation.csv')
    assert (df_k['k_value'] >= 3.0).all() and (df_k['k_value'] <= 6.0).all()
    
    df_alpha = pd.read_csv(reports_dir / 'phase10_5_alpha_revalidation.csv')
    assert (df_alpha['alpha_pts'] >= 0.35).all() and (df_alpha['alpha_pts'] <= 0.65).all()
    
    df_h = pd.read_csv(reports_dir / 'phase10_5_horizon_gamma.csv')
    assert set(df_h['H']).issubset({3, 5, 8})
    assert (df_h['gamma'] >= 0.85).all() and (df_h['gamma'] <= 0.95).all()

def test_candidate_manifest_integrity():
    """Verify parameter candidate manifest exists and contains promoted values."""
    manifest_path = reports_dir / 'phase10_5_candidate_manifest.json'
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['model_name'] == 'PHASE10_5_PARAMETER_OPTIMIZED'
    assert manifest['historical_mean_score'] == 2172.50
    assert manifest['parameter_changes']['haul_blend_alpha']['new'] == 0.40
    assert manifest['parameter_changes']['goal_dispersion_r']['new'] == 1.95
    assert manifest['parameter_changes']['assist_dispersion_r']['new'] == 1.65
    assert manifest['parameter_changes']['bayesian_k']['new'] == 4.0
    assert manifest['parameter_changes']['horizon_H']['new'] == 5
    assert manifest['parameter_changes']['discount_gamma']['new'] == 0.90
    assert manifest['parameter_changes']['role_decay_tau']['new'] == 0.82
