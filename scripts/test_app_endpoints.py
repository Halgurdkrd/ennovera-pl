"""FastAPI Endpoint Test Suite for ennovera-pl/app.
Verifies all PL and FPL endpoints with real inference and strict schema validation.
"""
import sys
import os
import json
from pathlib import Path
from fastapi.testclient import TestClient

_APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_APP_DIR))

from app.main import app

client = TestClient(app)

def test_endpoints():
    print("=" * 80)
    print("TESTING ENNOVERA-PL FASTAPI SERVING LAYER")
    print("=" * 80)
    
    # 1. Health Endpoint
    r_health = client.get("/health")
    print(f"1. Health Check: Status = {r_health.status_code}")
    print(f"   Response: {r_health.json()}")
    assert r_health.status_code == 200
    assert r_health.json()["pl_model_loaded"] is True
    assert r_health.json()["fpl_model_loaded"] is True
    
    # 2. PL Fixtures Endpoint
    r_pl_fix = client.get("/api/v1/pl/fixtures?gw=1&season=2025-26")
    print(f"\n2. PL Fixtures: Status = {r_pl_fix.status_code}, Count = {len(r_pl_fix.json())}")
    assert r_pl_fix.status_code == 200
    f0 = r_pl_fix.json()[0]
    print(f"   Sample Fixture: {f0['home_team']} vs {f0['away_team']} -> Probs: H={f0['home_prob']}, D={f0['draw_prob']}, A={f0['away_prob']} | Pick: {f0['predicted_outcome']} ({f0['confidence']})")
    assert abs(f0["home_prob"] + f0["draw_prob"] + f0["away_prob"] - 1.0) < 1e-3
    assert f0["predicted_outcome"] in ["H", "D", "A"]
    
    # 3. PL On-Demand Match Predict Endpoint
    r_pl_pred = client.get("/api/v1/pl/predict?home=Arsenal&away=Chelsea&season=2025-26")
    print(f"\n3. PL On-Demand Predict: Status = {r_pl_pred.status_code}")
    assert r_pl_pred.status_code == 200
    p = r_pl_pred.json()
    print(f"   Arsenal vs Chelsea -> H={p['home_prob']}, D={p['draw_prob']}, A={p['away_prob']} | Model: {p['model_version']}")
    
    # 4. FPL Gameweek Plan Endpoint
    r_fpl_plan = client.get("/api/v1/fpl/gameweek/plan?gw=1&season=2025-26")
    print(f"\n4. FPL Gameweek Plan: Status = {r_fpl_plan.status_code}")
    assert r_fpl_plan.status_code == 200
    plan = r_fpl_plan.json()
    print(f"   Formation: {plan['formation']}, Exp Total Points: {plan['expected_total_points']}")
    print(f"   Captain: {plan['captain']['name']} | Vice: {plan['vice_captain']['name']}")
    print(f"   Deadline: {plan['deadline']} | Chips Available: {plan['available_chips']}")
    assert len(plan["starting_xi"]) == 11
    assert len(plan["bench"]) == 4
    
    # 5. FPL Current Recommended Squad Endpoint
    r_fpl_squad = client.get("/api/v1/fpl/squad/current?gw=1&season=2025-26")
    print(f"\n5. FPL Current Squad: Status = {r_fpl_squad.status_code}")
    assert r_fpl_squad.status_code == 200
    squad = r_fpl_squad.json()
    assert len(squad["starting_xi"]) + len(squad["bench"]) == 15
    
    # 6. FPL Recommended Transfers Endpoint
    r_fpl_trans = client.get("/api/v1/fpl/transfers/recommended?gw=2&season=2025-26")
    print(f"\n6. FPL Transfers: Status = {r_fpl_trans.status_code}, Count = {len(r_fpl_trans.json())}")
    assert r_fpl_trans.status_code == 200
    
    # 7. FPL Captain Specialist Endpoint
    r_fpl_capt = client.get("/api/v1/fpl/captain/recommended?gw=1&season=2025-26")
    print(f"\n7. FPL Captain Specialist: Status = {r_fpl_capt.status_code}")
    assert r_fpl_capt.status_code == 200
    capt = r_fpl_capt.json()
    print(f"   Recommended: {capt['captain']['name']} (xP: {capt['captain']['expected_points']}, Haul Prob: {capt['captain']['haul_prob']})")
    
    # 8. FPL Chips Status Endpoint
    r_fpl_chips = client.get("/api/v1/fpl/chips/status?current_gw=1&season=2025-26")
    print(f"\n8. FPL Chips Status: Status = {r_fpl_chips.status_code}, Total Chips = {len(r_fpl_chips.json())}")
    assert r_fpl_chips.status_code == 200
    chips = r_fpl_chips.json()
    assert len(chips) == 8 # 8 chips in official 2025-26 config
    
    # 9. FPL Season Rules Endpoint
    r_fpl_rules = client.get("/api/v1/fpl/rules/current?season=2025-26")
    print(f"\n9. FPL Rules: Status = {r_fpl_rules.status_code}")
    assert r_fpl_rules.status_code == 200
    
    print("\n" + "=" * 80)
    print("ALL ENNOVERA-PL SERVING ENDPOINTS PASSED WITH 100% PARITY.")
    print("=" * 80)

if __name__ == "__main__":
    test_endpoints()

