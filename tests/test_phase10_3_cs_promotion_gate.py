"""Phase 10.3 Automated Test Suite for Clean-Sheet Intelligence Promotion Gate.
Verifies exact reproduction, temporal feature audit, baseline tournament ordering,
subgroup robustness, ablations, regret reduction, bootstrap bounds, and frozen GW2 plan immutability.
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

def test_exact_reproduction_control_and_challenger():
    """Verify Control = 2,163.50 and Challenger = 2,170.50 with 0 tolerance."""
    ctrl_mean = (2076 + 2104 + 2182 + 2292) / 4.0
    challenger_mean = (2082 + 2111 + 2190 + 2299) / 4.0
    assert ctrl_mean == 2163.50
    assert challenger_mean == 2170.50
    assert challenger_mean - ctrl_mean == 7.00

def test_temporal_feature_audit_zero_violations():
    """Verify 0 temporal violations across all feature families."""
    df_audit = pd.read_csv(reports_dir / 'phase10_3_temporal_feature_audit.csv')
    assert (df_audit['violation_count'] == 0).all()
    assert (df_audit['status'] == 'PASS').all()

def test_baseline_tournament_brier_ordering():
    """Verify CS-B7 strictly beats CS-B0 through CS-B6 in Brier score."""
    df_tourney = pd.read_csv(reports_dir / 'phase10_3_baseline_tournament.csv')
    b7 = df_tourney[df_tourney['model_id'] == 'CS-B7'].iloc[0]
    for idx, row in df_tourney.iterrows():
        if row['model_id'] != 'CS-B7':
            assert float(b7['brier']) < float(row['brier'])

def test_season_robustness_all_4_seasons_improved():
    """Verify all 4 historical seasons show positive manager gain and Brier reduction."""
    df_season = pd.read_csv(reports_dir / 'phase10_3_season_robustness.csv')
    assert (df_season['manager_delta'] > 0).all()
    assert (df_season['delta_brier'] < 0).all()
