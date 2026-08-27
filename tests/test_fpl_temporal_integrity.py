import sys
import json
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from app.services.temporal_governance import TemporalLeakageError, FPLMode, assert_predeadline_integrity
from app.services.fpl_ingestor import fpl_ingestor
from app.services.fpl_service import FPLService


def test_past_gw_with_current_bootstrap_rejected():
    """Test 1: Requesting historical replay of past GW with LIVE_PROSPECTIVE mode raises TemporalLeakageError."""
    with pytest.raises(TemporalLeakageError) as exc_info:
        fpl_ingestor.get_all_players(target_gw=1, mode=FPLMode.LIVE_PROSPECTIVE)
    assert "Cannot use LIVE_PROSPECTIVE mode with current bootstrap for past Gameweek" in str(exc_info.value)


def test_historical_replay_without_snapshot_fails_closed():
    """Test 2: Historical replay without an archived snapshot fails closed with TemporalLeakageError."""
    # GW 99 has no snapshot archived
    with pytest.raises(TemporalLeakageError) as exc_info:
        fpl_ingestor.get_all_players(target_gw=99, mode=FPLMode.HISTORICAL_REPLAY)
    assert "HISTORICAL_SNAPSHOT_UNAVAILABLE" in str(exc_info.value)


def test_post_deadline_feature_assertion_fails():
    """Test 3: Feature timestamp at or after deadline raises TemporalLeakageError."""
    deadline = "2026-08-28T17:30:00Z"
    post_deadline_ts = "2026-08-28T18:00:00Z"
    
    with pytest.raises(TemporalLeakageError):
        assert_predeadline_integrity(post_deadline_ts, deadline)


def test_pre_deadline_feature_assertion_accepted():
    """Test 4: Feature timestamp prior to deadline passes cleanly."""
    deadline = "2026-08-28T17:30:00Z"
    pre_deadline_ts = "2026-08-27T12:00:00Z"
    
    # Should not raise
    assert_predeadline_integrity(pre_deadline_ts, deadline)


def test_live_prospective_current_data_accepted():
    """Test 5: Live prospective mode for upcoming GW2 is accepted and returns players with temporal metadata."""
    players = fpl_ingestor.get_all_players(target_gw=2, mode=FPLMode.LIVE_PROSPECTIVE)
    assert len(players) > 500
    p0 = players[0]
    assert "temporal_metadata" in p0
    assert p0["temporal_metadata"]["mode"] == FPLMode.LIVE_PROSPECTIVE
    assert p0["temporal_metadata"]["gameweek_context"] == 2


def test_archived_predeadline_snapshot_accepted():
    """Test 6: Pre-deadline archived snapshot for GW02 is accepted in HISTORICAL_REPLAY mode."""
    # Archive GW2 snapshot first to ensure it exists
    fpl = FPLService()
    plan_gw2 = fpl.get_gameweek_plan("2026-27", gw=2)
    fpl_ingestor.archive_predeadline_snapshot("2026-27", 2, plan_gw2["deadline"], plan_gw2)
    
    # Ingest using HISTORICAL_REPLAY
    players_replay = fpl_ingestor.get_all_players(target_gw=2, mode=FPLMode.HISTORICAL_REPLAY)
    assert len(players_replay) > 500


def test_historical_benchmark_script_shift_safety():
    """Test 7: Verify that run_fpl03_pipeline.py strictly uses .shift(1) for rolling feature calculations."""
    pipeline_script = _REPO_ROOT / "scripts" / "run_fpl03_pipeline.py"
    assert pipeline_script.exists(), "FPL-03 research pipeline script must exist"
    txt = pipeline_script.read_text(encoding="utf-8")
    
    assert 'grp["minutes"].shift(1).rolling' in txt, "Historical script must use .shift(1) on minutes"
    assert 'grp["total_points"].shift(1).rolling' in txt, "Historical script must use .shift(1) on total_points"
    assert 'grp["expected_goal_involvements"].shift(1).rolling' in txt, "Historical script must use .shift(1) on xGI"


def test_prospective_performance_governance_state():
    """Test 8: Verify that get_performance() reports 0 completed prospective GWs and excludes GW1."""
    fpl = FPLService()
    perf = fpl.get_performance("2026-27")
    
    assert perf["completed_gameweeks"] == 0
    assert perf["total_points"] == 0
    assert perf["official_start_gw"] == 2
    assert perf["active_gameweek"]["status"] == "FROZEN_PENDING"
    assert len(perf["excluded_gameweeks"]) >= 1
    assert "INVALID_RETROSPECTIVE_RECONSTRUCTION" in perf["excluded_gameweeks"][0]["status"]
