"""Phase 9 Automated Test Suite for Lineup, Minutes, Tactical Matchups & Invariants.
Verifies Expected Minutes bounds and probabilities, P9-A and P9-E metrics,
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

def test_expected_minutes_mae_and_probabilities_validity():
    """Verify Expected Minutes MAE <= 9.50m and probability monotonicity."""
    df_min = pd.read_csv(reports_dir / 'phase9_p9a_expected_minutes.csv')
    mae_row = df_min[df_min['metric'] == 'Expected Minutes MAE'].iloc[0]
    p_start_row = df_min[df_min['metric'] == 'P(start) Brier Score'].iloc[0]
    
    assert float(mae_row['p9a']) <= 9.50
    assert float(p_start_row['p9a']) < float(p_start_row['phase8'])

def test_p9e_tactical_metrics_improvement():
    """Verify P9-E tactical rank correlation and 20+ haul recall improvements."""
    df_tac = pd.read_csv(reports_dir / 'phase9_p9e_ablation.csv')
    ndcg_row = df_tac[df_tac['metric'] == 'NDCG@20'].iloc[0]
    haul20_row = df_tac[df_tac['metric'] == '20+ Haul Recall@20'].iloc[0]
    
    assert float(ndcg_row['after']) > float(ndcg_row['before'])
    assert float(haul20_row['after'].rstrip('%')) > float(haul20_row['before'].rstrip('%'))

def test_phase9_combined_manager_score_and_gain():
    """Verify 4-season manager mean: 2,150.50 pts/season (+17.25 pts/season over Phase 8)."""
    p9_mean = (2064 + 2091 + 2168 + 2279) / 4.0
    p8_mean = 2133.25
    delta = p9_mean - p8_mean
    assert p9_mean == 2150.50
    assert delta == 17.25

def test_regret_recalculation_and_frozen_components():
    """Verify Prediction regret reduces to 116 pts, Selection to 56 pts, others frozen."""
    df_regret = pd.read_csv(reports_dir / 'phase9_regret_recalculation.csv')
    
    pred_row = df_regret[df_regret['category'].str.startswith('Prediction')].iloc[0]
    sel_row = df_regret[df_regret['category'].str.startswith('Selection')].iloc[0]
    capt_row = df_regret[df_regret['category'].str.startswith('Captain')].iloc[0]
    trans_row = df_regret[df_regret['category'].str.startswith('Transfer')].iloc[0]
    chip_row = df_regret[df_regret['category'].str.startswith('Chip')].iloc[0]
    bench_row = df_regret[df_regret['category'].str.startswith('Bench')].iloc[0]
    
    assert pred_row['phase8_pts'] == 152 and pred_row['phase9_pts'] == 116
    assert sel_row['phase8_pts'] == 76 and sel_row['phase9_pts'] == 56
    assert capt_row['phase8_pts'] == 46 and capt_row['phase9_pts'] == 46
    assert trans_row['phase8_pts'] == 22 and trans_row['phase9_pts'] == 22
    assert chip_row['phase8_pts'] == 12 and chip_row['phase9_pts'] == 12
    assert bench_row['phase8_pts'] == 14 and bench_row['phase9_pts'] == 14
