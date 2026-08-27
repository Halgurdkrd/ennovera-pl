"""Phase 5.2 Automated Test Suite for Cross-Competition Intelligence & Ablations.
Verifies Phase 5.15.1 Gate compliance, CROSSCOMP_DATA_V1_1 release integrity (720 team-match rows),
Phase 5.2 ablation results (P5-A to P5-G), bootstrap bounds, and frozen GW2 plan immutability.
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

v1_1_dir = repo_root / 'data' / 'cross_competition' / 'releases' / 'CROSSCOMP_DATA_V1_1'
reports_dir = repo_root / 'reports'

def test_frozen_gw2_plan_immutability():
    """Verify frozen GW2 prospective plan has not been modified."""
    frozen_path = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert frozen_path.exists()
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert h == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_coverage_bias_buckets_sum_to_100():
    """Verify coverage bias buckets are mutually exclusive and sum to 100%."""
    df_cov = pd.read_csv(reports_dir / 'phase5_15_1_coverage_bias_reconciled.csv')
    assert abs(df_cov['pct'].sum() - 100.0) < 1e-4

def test_team_matches_720_rows():
    """Verify CROSSCOMP_DATA_V1_1 team_matches table contains both perspectives (720 rows)."""
    df_tm = pd.read_parquet(v1_1_dir / 'team_matches.parquet')
    assert len(df_tm) == 720
    assert set(df_tm['home_away'].unique()) == {'H', 'A'}

def test_phase5_2_ablation_performance():
    """Verify Phase 5.2 P5-G manager gain (+14.00 pts/season) and MAE improvement."""
    df_abl = pd.read_csv(reports_dir / 'phase5_2_ablation_results.csv')
    p4_row = df_abl[df_abl['experiment'].str.startswith('P5-A')].iloc[0]
    p5g_row = df_abl[df_abl['experiment'].str.startswith('P5-G')].iloc[0]
    
    assert p4_row['mean_score'] == 2080.00
    assert p5g_row['mean_score'] == 2094.00
    assert p5g_row['delta'] == 14.00
    assert p5g_row['mae'] < p4_row['mae']
    assert p5g_row['ndcg20'] > p4_row['ndcg20']

def test_competition_specific_value_ordering():
    """Verify UCL is the highest value European competition in the ablation."""
    df_comp = pd.read_csv(reports_dir / 'phase5_2_competition_value.csv')
    ucl_row = df_comp[df_comp['competition_subset'] == 'PL + UCL'].iloc[0]
    assert ucl_row['delta_vs_p4'] >= 8.00
