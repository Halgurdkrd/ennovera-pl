import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from app.services.fpl_service import FPLService
from app.services.fpl_ingestor import fpl_ingestor

BOOTSTRAP_PATH = _REPO_ROOT / "data" / "processed" / "fpl_live_bootstrap.json"


def test_haaland_gw1_official_raw_points():
    """Factual check: Haaland GW1 raw points must equal 2 in the official 2026-27 bootstrap data."""
    assert BOOTSTRAP_PATH.exists(), "Bootstrap data file must exist"
    with open(BOOTSTRAP_PATH, "r", encoding="utf-8") as f:
        bootstrap = json.load(f)
    
    haaland = next((el for el in bootstrap.get("elements", []) if "Haaland" in el.get("web_name", "")), None)
    assert haaland is not None, "Haaland must exist in elements database"
    assert haaland["id"] == 411, "Haaland element ID must be 411"
    
    # Check official points
    raw_pts = haaland.get("event_points", haaland.get("total_points", 0))
    assert raw_pts == 2, f"Expected Haaland raw GW1 points to be 2, got {raw_pts}"


def test_fpl_performance_mathematical_reproducibility():
    """Verify that get_performance() produces mathematically sound scores from player-level events."""
    service = FPLService()
    perf = service.get_performance("2026-27")
    
    assert perf["season"] == "2026-27"
    assert perf["completed_gameweeks"] == 1
    assert len(perf["history"]) == 1
    
    gw1 = perf["history"][0]
    assert gw1["gameweek"] == 1
    assert gw1["status"] == "HISTORICAL_BASELINE"
    
    # Audit player list
    players = gw1.get("players", [])
    assert len(players) == 15, "GW1 record must include all 15 players"
    
    starters = [p for p in players if p["is_starter"]]
    bench = [p for p in players if not p["is_starter"]]
    assert len(starters) == 11, "Must have exactly 11 starters"
    assert len(bench) == 4, "Must have exactly 4 bench substitutes"
    
    # Audit captain
    captain = next((p for p in starters if p["is_captain"]), None)
    assert captain is not None, "A captain must be designated in starting XI"
    assert captain["multiplier"] == 2, "Standard captain multiplier must be 2"
    assert captain["effective_points"] == captain["raw_points"] * 2
    
    # Verify starting XI raw sum
    xi_raw_sum = sum(p["raw_points"] for p in starters)
    assert xi_raw_sum == gw1["starting_xi_raw_points"], "Starting XI raw sum must match"
    
    # Verify final score calculation: sum(effective_points of starters) - hit_cost
    expected_score = sum(p["effective_points"] for p in starters) - gw1["hit_cost"]
    assert expected_score == gw1["final_points"], "Final score must equal sum of starter effective points"
    assert expected_score == gw1["score"]
    
    # Verify bench points missed
    bench_sum = sum(p["raw_points"] for p in bench)
    assert bench_sum == gw1["bench_points"]
    assert bench_sum == perf["bench_points_missed"]
    
    # Verify cumulative aggregates
    assert perf["total_points"] == expected_score
    assert perf["average_points"] == float(expected_score)
    assert perf["captain_points"] == captain["effective_points"]
