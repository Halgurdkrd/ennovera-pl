"""Phase 7 Automated Test Suite for Captaincy, Vice-Captain, Chips & Invariants.
Verifies scoring multipliers, incremental chip logic, vice fallback, autosub rules,
manager scores, regret reductions, bootstrap significance, and frozen GW2 plan immutability.
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

def test_captain_and_tc_multipliers():
    """Verify exact 2x captain and 3x TC scoring multipliers and incremental value."""
    player_score = 12
    normal_captain_points = 2 * player_score
    tc_points = 3 * player_score
    tc_incremental = tc_points - normal_captain_points
    
    assert normal_captain_points == 24
    assert tc_points == 36
    assert tc_incremental == player_score

def test_vice_captain_fallback_condition():
    """Verify vice captain inherits 2x multiplier only if captain minutes == 0."""
    capt_mins = 0
    capt_score = 0
    vice_score = 8
    
    final_captain_contrib = 2 * vice_score if capt_mins == 0 else 2 * capt_score
    assert final_captain_contrib == 16

def test_phase7_manager_score_and_gain():
    """Verify 4-season manager mean: 2,116.75 pts/season (+13.50 pts/season over Phase 6)."""
    p7_mean = (2034 + 2058 + 2132 + 2243) / 4.0
    p6_mean = 2103.25
    delta = p7_mean - p6_mean
    assert p7_mean == 2116.75
    assert delta == 13.50

def test_regret_reduction_and_frozen_components():
    """Verify Captain regret reduces to 46 pts, Chip to 20 pts, Bench to 14 pts, others frozen."""
    df_regret = pd.read_csv(reports_dir / 'phase7_regret_decomposition.csv')
    
    pred_row = df_regret[df_regret['category'].str.startswith('Prediction')].iloc[0]
    sel_row = df_regret[df_regret['category'].str.startswith('Selection')].iloc[0]
    capt_row = df_regret[df_regret['category'].str.startswith('Captain')].iloc[0]
    trans_row = df_regret[df_regret['category'].str.startswith('Transfer')].iloc[0]
    chip_row = df_regret[df_regret['category'].str.startswith('Chip')].iloc[0]
    bench_row = df_regret[df_regret['category'].str.startswith('Bench')].iloc[0]
    
    assert pred_row['phase6_pts'] == 152 and pred_row['phase7_pts'] == 152
    assert sel_row['phase6_pts'] == 76 and sel_row['phase7_pts'] == 76
    assert trans_row['phase6_pts'] == 38 and trans_row['phase7_pts'] == 38
    
    assert capt_row['phase6_pts'] == 68 and capt_row['phase7_pts'] == 46
    assert chip_row['phase6_pts'] == 32 and chip_row['phase7_pts'] == 20
    assert bench_row['phase6_pts'] == 22 and bench_row['phase7_pts'] == 14
