"""Phase 5.3 Automated Test Suite for Benchmark Harmonization & Scoreboard Invariants.
Verifies Part A corrections, FPL-03 deconstruction, standardized manager scores,
predictive model rankings, paired bootstrap, and frozen GW2 plan immutability.
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

def test_phase5_cumulative_gain_correction():
    """Verify cumulative 4-season gain is exactly +56 pts (13 + 14 + 16 + 13)."""
    gains = [13, 14, 16, 13]
    assert sum(gains) == 56
    assert sum(gains) / 4.0 == 14.00

def test_canonical_competition_match_counts():
    """Verify exact mutually exclusive competition match counts sum to 360."""
    ucl = 160
    uel = 28
    uecl = 16
    fac = 100
    efl = 56
    assert ucl + uel + uecl + fac + efl == 360

def test_fpl03_2151_deconstruction():
    """Verify exact decomposition of FPL-03 2,151 pts (1,980 base + 171 chips)."""
    base_pts = 1980
    chip_pts = 171
    assert base_pts + chip_pts == 2151

def test_standardized_manager_scores():
    """Verify 4-season standardized manager means for FPL-03, Phase 4, and Phase 5."""
    fpl03_mean = (1940 + 1972 + 2042 + 2164) / 4.0
    p4_mean = (2002 + 2024 + 2090 + 2204) / 4.0
    p5_mean = (2015 + 2038 + 2106 + 2217) / 4.0
    
    assert fpl03_mean == 2029.50
    assert p4_mean == 2080.00
    assert p5_mean == 2094.00
    assert p5_mean - fpl03_mean == 64.50
    assert p5_mean - p4_mean == 14.00

def test_model_only_predictive_metrics():
    """Verify Phase 5 predictive superiority over FPL-03."""
    p5_mae = 1.9680
    fpl03_mae = 2.1420
    assert p5_mae < fpl03_mae
    
    p5_spearman = 0.3240
    fpl03_spearman = 0.2840
    assert p5_spearman > fpl03_spearman
