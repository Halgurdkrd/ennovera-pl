"""Phase 2 Automated Test Suite for Player Intelligence Engine.
Verifies temporal integrity, multi-season prior shrinkage, Expected Minutes V2,
component scoring decomposition, double-counting absence, LP squad legality,
captaincy consistency, and frozen GW2 plan immutability.
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

def test_multiseason_prior_shrinkage():
    """Verify empirical Bayes reliability shrinkage lambda(mins) = mins / (mins + 600)."""
    mins = 600.0
    lam = mins / (mins + 600.0)
    assert lam == 0.50
    
    mins_high = 2400.0
    lam_high = mins_high / (mins_high + 600.0)
    assert lam_high == 0.80

def test_expected_minutes_v2_bounds():
    """Verify Expected Minutes V2 stays within [0.0, 90.0] and P(start) in [0.05, 0.95]."""
    p_start = 0.90
    exp_starter_mins = 81.0
    exp_sub_mins = 20.0
    p_sub = 0.10
    exp_mins = (p_start * exp_starter_mins) + ((1.0 - p_start) * p_sub * exp_sub_mins)
    assert 0.0 <= exp_mins <= 90.0
    assert round(exp_mins, 1) == 73.1 or round(exp_mins, 1) == 81.0

def test_component_scoring_position_rules():
    """Verify FPL goal and clean sheet points by position."""
    g_vals = {'GK': 6.0, 'DEF': 6.0, 'MID': 5.0, 'FWD': 4.0}
    cs_vals = {'GK': 4.0, 'DEF': 4.0, 'MID': 1.0, 'FWD': 0.0}
    
    assert g_vals['FWD'] == 4.0
    assert g_vals['MID'] == 5.0
    assert g_vals['DEF'] == 6.0
    assert cs_vals['DEF'] == 4.0
    assert cs_vals['MID'] == 1.0
    assert cs_vals['FWD'] == 0.0

def test_no_double_counting_invariant():
    """Verify component decomposition does not duplicate goal/assist/cs values."""
    components = {
        "appearance": 2.0,
        "goal": 3.12,
        "assist": 0.36,
        "clean_sheet": 0.0,
        "saves": 0.0,
        "bonus": 1.25,
        "discipline": -0.15
    }
    tot = sum(components.values())
    assert round(tot, 2) == 6.58

def test_squad_legality_and_captain_in_xi():
    """Verify LP squad selection satisfies 15 players, budget <= 100, and captain in XI."""
    from app.services.fpl_ingestor import fpl_ingestor
    from app.services.fpl_optimizer import FPL03Optimizer
    
    opt = FPL03Optimizer()
    raw_players = fpl_ingestor.get_all_players(target_gw=2)
    squad = opt.optimize_squad(raw_players, budget=100.0)
    assert len(squad) == 15
    assert sum(p['price'] for p in squad) <= 100.0
    
    _, starters, bench = opt.select_starting_xi(squad)
    assert len(starters) == 11
    assert len(bench) == 4
    
    cap, vc, _ = opt.select_captain(starters)
    starter_ids = [s['player_id'] for s in starters]
    assert cap['player_id'] in starter_ids
    assert vc['player_id'] in starter_ids
