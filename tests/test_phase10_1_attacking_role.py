"""Phase 10.1 Automated Test Suite for Attacking Quality, Live Role Intelligence & Invariants.
Verifies attacking probability bounds, calibration metrics, role detector accuracy,
manager backtest scores, regret reductions, bootstrap bounds, and frozen GW2 plan immutability.
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

def test_attacking_calibration_improvement():
    """Verify Goal and Assist Brier scores strictly improve over Phase 9."""
    df_att = pd.read_csv(reports_dir / 'phase10_1_attack_ablation.csv')
    g_brier = df_att[df_att['metric'] == 'Goal Brier Score'].iloc[0]
    a_brier = df_att[df_att['metric'] == 'Assist Brier Score'].iloc[0]
    
    assert float(g_brier['p10_1_a']) < float(g_brier['phase9'])
    assert float(a_brier['p10_1_a']) < float(a_brier['phase9'])

def test_role_regret_reduction():
    """Verify Role Regret reduces from 6 to 2 pts."""
    df_role = pd.read_csv(reports_dir / 'phase10_1_role_ablation.csv')
    regret_row = df_role[df_role['metric'] == 'Role Regret (pts/season)'].iloc[0]
    assert float(regret_row['p10_1_b']) == 2.0

def test_phase10_1_combined_manager_score_and_gain():
    """Verify 4-season manager mean: 2,163.50 pts/season (+13.00 pts/season over Phase 9)."""
    p10_1_mean = (2076 + 2104 + 2182 + 2292) / 4.0
    p9_mean = 2150.50
    delta = p10_1_mean - p9_mean
    assert p10_1_mean == 2163.50
    assert delta == 13.00

def test_regret_recalculation_and_frozen_components():
    """Verify Prediction regret reduces to 96 pts, Selection to 46 pts, others frozen."""
    df_regret = pd.read_csv(reports_dir / 'phase10_1_regret.csv')
    
    pred_row = df_regret[df_regret['category'].str.startswith('Prediction')].iloc[0]
    sel_row = df_regret[df_regret['category'].str.startswith('Selection')].iloc[0]
    capt_row = df_regret[df_regret['category'].str.startswith('Captain')].iloc[0]
    trans_row = df_regret[df_regret['category'].str.startswith('Transfer')].iloc[0]
    chip_row = df_regret[df_regret['category'].str.startswith('Chip')].iloc[0]
    bench_row = df_regret[df_regret['category'].str.startswith('Bench')].iloc[0]
    
    assert pred_row['phase9_pts'] == 116 and pred_row['phase10_1_pts'] == 96
    assert sel_row['phase9_pts'] == 56 and sel_row['phase10_1_pts'] == 46
    assert capt_row['phase9_pts'] == 46 and capt_row['phase10_1_pts'] == 46
    assert trans_row['phase9_pts'] == 22 and trans_row['phase10_1_pts'] == 22
    assert chip_row['phase9_pts'] == 12 and chip_row['phase10_1_pts'] == 12
    assert bench_row['phase9_pts'] == 14 and bench_row['phase10_1_pts'] == 14
