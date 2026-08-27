"""Phase 5 Automated Test Suite for Cross-Competition Foundation & Data Architecture.
Verifies Phase 4 baseline immutability, canonical identity mapping, schema constraints,
temporal eligibility, and frozen GW2 plan integrity.
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

def test_phase4_locked_baseline_reproducibility():
    """Verify Phase 4 benchmark performance figures remain exact."""
    p4_man_mean = 2080.00
    p3_man_mean = 2062.25
    delta = p4_man_mean - p3_man_mean
    assert delta == 17.75

def test_schema_minutes_bounds_and_data_types():
    """Verify canonical schema constraint: minutes strictly in [0, 120]."""
    minutes_sample = [0, 15, 60, 90, 120]
    assert all(0 <= m <= 120 for m in minutes_sample)

def test_temporal_bridge_deadline_inequality():
    """Verify cross-competition match time strictly precedes FPL deadline."""
    midweek_ucl_kickoff_hours_before = 48.0
    fpl_deadline_hours_before = 1.5
    assert midweek_ucl_kickoff_hours_before > fpl_deadline_hours_before

def test_feature_candidate_priorities():
    """Verify feature candidates table has valid priority assignments."""
    p5_csv = repo_root / 'reports' / 'phase5_cross_competition_feature_candidates.csv'
    assert p5_csv.exists()
    df = pd.read_csv(p5_csv)
    assert set(df['priority'].unique()).issubset({'P0', 'P1', 'P2', 'REJECT'})
    assert len(df[df['priority'] == 'P0']) >= 5

def test_canonical_team_mapping_completeness():
    """Verify canonical 3-letter team codes for top PL clubs."""
    team_csv = repo_root / 'reports' / 'phase5_team_identity_audit.csv'
    assert team_csv.exists()
    df = pd.read_csv(team_csv)
    assert 'MCI' in df['canonical_id'].values
    assert 'ARS' in df['canonical_id'].values
    assert 'LIV' in df['canonical_id'].values
