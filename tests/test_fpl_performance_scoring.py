import json
import pytest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(_REPO_ROOT))

from app.services.fpl_service import FPLService


def test_haaland_gw1_official_raw_points():
    """Verify that Erling Haaland (ID: 411) actually scored exactly 2 points in GW1."""
    bootstrap_file = _REPO_ROOT / "data" / "processed" / "fpl_live_bootstrap.json"
    assert bootstrap_file.exists(), "FPL live bootstrap cache must exist"
    
    data = json.loads(bootstrap_file.read_text(encoding="utf-8"))
    elements = data.get("elements", [])
    
    haaland = next((el for el in elements if el["id"] == 411), None)
    assert haaland is not None, "Haaland ID 411 must exist in FPL database"
    assert haaland["web_name"] == "Haaland"
    
    raw_gw1_points = haaland.get("event_points")
    assert raw_gw1_points == 2, f"Expected Haaland GW1 raw points == 2, got {raw_gw1_points}"


def test_fpl_performance_governance_reproducibility():
    """Verify that get_performance() reports prospective governance starting at GW2 with 0 completed GWs."""
    service = FPLService()
    perf = service.get_performance("2026-27")
    
    assert perf["season"] == "2026-27"
    assert perf["official_start_gw"] == 2
    assert perf["completed_gameweeks"] == 0
    assert perf["total_points"] == 0
    assert perf["active_gameweek"]["status"] == "FROZEN_PENDING"
    assert len(perf["excluded_gameweeks"]) >= 1
    assert "INVALID_RETROSPECTIVE_RECONSTRUCTION_EXCLUDED" == perf["excluded_gameweeks"][0]["status"]
