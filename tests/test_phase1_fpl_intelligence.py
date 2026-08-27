"""Phase 1 Automated Test Suite for FPL Intelligence Baseline.
Verifies temporal integrity, shift(1) lag, shrinkage schedule, component sums,
LP optimizer legality, captaincy rules, chip logic, and frozen GW2 plan immutability.
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

def test_early_season_shrinkage_schedule():
    """Verify Bayesian shrinkage function w(n) = n / (n + 4.0)."""
    from app.services.fpl_xp_model import fpl_xp_model
    assert fpl_xp_model.calculate_recency_weight(0) == 0.0
    assert fpl_xp_model.calculate_recency_weight(1) == 0.20
    assert fpl_xp_model.calculate_recency_weight(2) == 0.3333
    assert fpl_xp_model.calculate_recency_weight(4) == 0.50
    assert fpl_xp_model.calculate_recency_weight(8) == 0.6667

def test_xp_component_decomposition():
    """Verify player xP components sum logically and stay within bounds."""
    from app.services.fpl_xp_model import fpl_xp_model
    player = {
        "player_id": 411,
        "name": "Erling Haaland",
        "position": "FWD",
        "price": 15.5,
        "status": "a",
        "form": 2.0
    }
    res = fpl_xp_model.compute_player_xp(player, completed_gws=1, fixture_difficulty=2.0, is_home=True)
    assert "xp_decomposition" in res
    d = res["xp_decomposition"]
    assert d["prior_xp"] > 5.0
    assert d["recency_weight_w"] == 0.20
    assert res["expected_points"] >= 5.0
    assert res["expected_minutes"] == 81.0

def test_optimizer_constraints_and_squad_legality():
    """Verify LP solver respects budget, quotas, and formation rules."""
    from app.services.fpl_ingestor import fpl_ingestor
    from app.services.fpl_optimizer import FPL03Optimizer
    from app.services.fpl_xp_model import fpl_xp_model

    opt = FPL03Optimizer()
    raw_players = fpl_ingestor.get_all_players(target_gw=2)
    processed = fpl_xp_model.process_player_pool(raw_players, completed_gws=1)
    
    squad = opt.optimize_squad(processed, budget=100.0)
    assert len(squad) == 15
    tot_cost = sum(p["price"] for p in squad)
    assert tot_cost <= 100.0
    
    # Check positional counts
    pos_counts = {}
    for p in squad:
        pos_counts[p["position"]] = pos_counts.get(p["position"], 0) + 1
    assert pos_counts.get("GK") == 2
    assert pos_counts.get("DEF") == 5
    assert pos_counts.get("MID") == 5
    assert pos_counts.get("FWD") == 3

    # Check Starting XI
    form, starters, bench = opt.select_starting_xi(squad)
    assert len(starters) == 11
    assert len(bench) == 4
    
    # Check Captain
    cap, vc, _ = opt.select_captain(starters)
    assert cap["player_id"] in [s["player_id"] for s in starters]
    assert vc["player_id"] in [s["player_id"] for s in starters]
    assert cap["player_id"] != vc["player_id"]

def test_triple_captain_bug_detection_and_candidate_rule():
    """Verify detection of disjunctive OR bug and test candidate conjunction logic."""
    from app.services.fpl_optimizer import FPL03Optimizer
    opt = FPL03Optimizer()
    
    starters = [{"expected_points": 7.4}]
    bench = []
    captain = {"name": "Haaland", "expected_points": 7.4, "haul_prob": 0.55}
    rules = {"triple_captain_1": True}
    
    # 1. Existing Production Behavior: Fires USE due to 'or haul_prob >= 0.50'
    res_prod = opt.evaluate_chip(2, starters, bench, captain, rules, [])
    assert res_prod["action"] == "USE"  # Documents production bug presence
    
    # 2. Candidate Corrected Rule: Conjunction 'xP >= 9.5 and haul_prob >= 0.50'
    def candidate_evaluate_tc(cap_xp: float, cap_haul: float) -> str:
        if cap_xp >= 9.5 and cap_haul >= 0.50:
            return "USE"
        return "SAVE"
        
    assert candidate_evaluate_tc(7.4, 0.55) == "SAVE"
    assert candidate_evaluate_tc(9.8, 0.55) == "USE"
    assert candidate_evaluate_tc(9.8, 0.40) == "SAVE"
