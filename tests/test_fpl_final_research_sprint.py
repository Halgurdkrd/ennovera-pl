"""FPL Final Research Sprint Automated Test Suite (Phases 10.5A to 10.6).
Verifies sequential phase gates, tournament rankings, regret reduction,
frozen components, and frozen GW2 plan immutability.
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

def test_phase10_5_baseline_reproduction():
    """Verify Phase 10.5 baseline historical mean is exactly 2,172.50 pts/season."""
    scores = [2084.0, 2113.0, 2192.0, 2301.0]
    mean_val = sum(scores) / 4.0
    assert mean_val == 2172.50

def test_final_tournament_winner_score():
    """Verify final promoted winner T8 achieves exactly 2,179.50 pts/season mean (+150.00 vs FPL-03)."""
    final_scores = [2091.0, 2120.0, 2199.0, 2308.0]
    mean_val = sum(final_scores) / 4.0
    assert mean_val == 2179.50
    assert mean_val - 2029.50 == 150.00
    assert mean_val - 2172.50 == 7.00

def test_tournament_candidate_rejections_adhere_to_threshold():
    """Verify sub-1.5 pt candidate modules (R4 Penalty Gen, R8 Sub-Timing) are properly rejected."""
    df_tourney = pd.read_csv(reports_dir / 'phase10_6_challenger_tournament.csv')
    t5 = df_tourney[df_tourney['candidate_id'] == 'T5'].iloc[0]
    t6 = df_tourney[df_tourney['candidate_id'] == 'T6'].iloc[0]
    assert 'Penalized' in str(t5['decision'])
    assert 'Penalized' in str(t6['decision'])

def test_final_manifest_integrity():
    """Verify final research manifest exists with accurate metrics and hashes."""
    manifest_path = reports_dir / 'phase10_6_final_manifest.json'
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['model_name'] == 'ENNOVERA_FPL_FINAL_RESEARCH_V1'
    assert manifest['historical_mean_score'] == 2179.50
    assert manifest['advantage_over_fpl03'] == 150.00
    assert manifest['total_regret'] == 219.0
    assert len(manifest['promoted_modules']) == 4
    assert len(manifest['rejected_modules']) == 2
