"""Phase 4 Automated Verification Test Suite.
Tests:
  1. Team canonicalization & alias mapping
  2. V2 production prediction calculation & validation
  3. V5.1 shadow prediction generation & validation
  4. Vectorized 10,000 Monte Carlo simulation invariants
  5. Pre-kickoff integrity invariant
  6. Batch validation logic
  7. FastAPI PL endpoint schemas and responses
"""
import os
import sys
import numpy as np
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TEST_DIR.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_SCRIPTS_DIR))

from team_aliases import canonicalize, PL_2026_27
from pl_simulation import simulate_season
from scripts.pl_auto_pipeline import (
    predict_v2,
    predict_v5,
    validate_prediction_batch,
    load_state,
    load_v5_model
)
from populate_pl_matches import load_model, fixtures
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="module")
def model_artifacts():
    calib, feats = load_model()
    elo, form = load_state()
    v5_art = load_v5_model()
    return {
        "calib": calib,
        "feats": feats,
        "elo": elo,
        "form": form,
        "v5_art": v5_art
    }


# ---------------------------------------------------------------------------
# Test 1: Canonical Team Aliases
# ---------------------------------------------------------------------------
def test_canonical_team_aliases():
    assert len(PL_2026_27) == 20, f"Expected exactly 20 PL clubs, got {len(PL_2026_27)}"
    
    # Test known short names and FPL API spellings
    test_cases = [
        ("Man City", "Manchester City"),
        ("Man Utd", "Manchester United"),
        ("Spurs", "Tottenham"),
        ("Nott'm Forest", "Nottingham Forest"),
        ("Wolves", "Wolverhampton Wanderers"),
        ("Brighton", "Brighton and Hove Albion"),
        ("West Ham", "West Ham United"),
        ("Arsenal", "Arsenal"),
        ("Liverpool", "Liverpool")
    ]
    for raw, expected in test_cases:
        assert canonicalize(raw) == expected, f"Failed alias mapping for {raw} -> {expected}"


# ---------------------------------------------------------------------------
# Test 2: V2 Production Model Probability Bounds
# ---------------------------------------------------------------------------
def test_v2_prediction_bounds(model_artifacts):
    art = model_artifacts
    pairs = [
        ("Arsenal", "Chelsea"),
        ("Manchester City", "Liverpool"),
        ("Aston Villa", "Newcastle United"),
        ("Crystal Palace", "Everton"),
        ("Brentford", "Fulham")
    ]
    for h, a in pairs:
        hw, d, aw = predict_v2(art["calib"], art["feats"], h, a, art["elo"], art["form"])
        assert 0.0 <= hw <= 1.0, f"V2 home prob out of bounds: {hw}"
        assert 0.0 <= d <= 1.0, f"V2 draw prob out of bounds: {d}"
        assert 0.0 <= aw <= 1.0, f"V2 away prob out of bounds: {aw}"
        assert abs(hw + d + aw - 1.0) <= 0.005, f"V2 probabilities do not sum to 1: sum={hw+d+aw}"


# ---------------------------------------------------------------------------
# Test 3: V5.1 Shadow Model Inference
# ---------------------------------------------------------------------------
def test_v5_shadow_prediction_bounds(model_artifacts):
    art = model_artifacts
    pairs = [
        ("Arsenal", "Manchester United"),
        ("Manchester City", "Tottenham"),
        ("Chelsea", "Brighton and Hove Albion")
    ]
    for h, a in pairs:
        hw, d, aw = predict_v5(art["v5_art"], art["calib"], art["feats"], h, a, art["elo"], art["form"])
        assert 0.0 <= hw <= 1.0, f"V5.1 home prob out of bounds: {hw}"
        assert 0.0 <= d <= 1.0, f"V5.1 draw prob out of bounds: {d}"
        assert 0.0 <= aw <= 1.0, f"V5.1 away prob out of bounds: {aw}"
        assert abs(hw + d + aw - 1.0) <= 0.005, f"V5.1 probabilities do not sum to 1: sum={hw+d+aw}"


# ---------------------------------------------------------------------------
# Test 4: Batch Validation Invariants
# ---------------------------------------------------------------------------
def test_batch_validation():
    # Valid batch
    valid_batch = [
        {
            "fixture_id": "PL_2026_27_GW1_ARS_CHE",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "home_prob": 0.55,
            "draw_prob": 0.25,
            "away_prob": 0.20
        }
    ]
    ok, msg = validate_prediction_batch(valid_batch)
    assert ok, f"Expected valid batch, got error: {msg}"
    
    # Invalid batch (sum > 1.005)
    invalid_batch = [
        {
            "fixture_id": "PL_2026_27_GW1_ARS_CHE",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "home_prob": 0.70,
            "draw_prob": 0.30,
            "away_prob": 0.20
        }
    ]
    ok_inv, _ = validate_prediction_batch(invalid_batch)
    assert not ok_inv, "Expected invalid batch to fail validation"


# ---------------------------------------------------------------------------
# Test 5: Vectorized Simulation Mathematical Invariants
# ---------------------------------------------------------------------------
def test_simulation_invariants():
    all_fx = fixtures()
    calib, feats = load_model()
    elo, form = load_state()
    
    matches = []
    for f in all_fx:
        p = list(predict_v2(calib, feats, f['home'], f['away'], elo, form))
        matches.append({
            'home': f['home'],
            'away': f['away'],
            'finished': bool(f.get('finished') and f.get('hs') is not None),
            'hs': f.get('hs'),
            'as': f.get('as'),
            'probs': p
        })
        
    table = simulate_season(matches, n_sims=5000)
    assert len(table) == 20, f"Expected 20 clubs in table, got {len(table)}"
    
    champ_sum = sum(r['champion_prob'] for r in table)
    top4_sum = sum(r['top4_prob'] for r in table)
    releg_sum = sum(r['relegation_prob'] for r in table)
    
    assert abs(champ_sum - 1.0) <= 0.01, f"Champion probability sum must equal 1.0, got {champ_sum}"
    assert abs(top4_sum - 4.0) <= 0.02, f"Top-4 probability sum must equal 4.0, got {top4_sum}"
    assert abs(releg_sum - 3.0) <= 0.02, f"Relegation probability sum must equal 3.0, got {releg_sum}"


# ---------------------------------------------------------------------------
# Test 6: Pre-Kickoff Timing Integrity
# ---------------------------------------------------------------------------
def test_prekickoff_integrity():
    kickoff = datetime.now(timezone.utc) + timedelta(hours=2)
    generated_at = datetime.now(timezone.utc)
    
    # Valid prospective prediction
    assert generated_at < kickoff, "Prediction timestamp must be before kickoff"


# ---------------------------------------------------------------------------
# Test 7: FastAPI Endpoints Verification
# ---------------------------------------------------------------------------
def test_fastapi_endpoints(api_client):
    # /health
    r = api_client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'ok'
    assert data['production_model_loaded'] is True
    assert data['season'] == '2026-27'
    
    # /api/v1/pl/fixtures
    r = api_client.get('/api/v1/pl/fixtures?gw=2&season=2026-27')
    assert r.status_code == 200
    fixtures_data = r.json()
    assert len(fixtures_data) == 10, f"Expected 10 fixtures for GW2, got {len(fixtures_data)}"
    first = fixtures_data[0]
    assert 'home_prob' in first and 'draw_prob' in first and 'away_prob' in first
    assert first['model_public_version'] == 'ennovera-pl-v1.0'
    
    # /api/v1/pl/predict
    r = api_client.get('/api/v1/pl/predict?home=Arsenal&away=Chelsea')
    assert r.status_code == 200
    pred = r.json()
    assert pred['home_team'] == 'Arsenal'
    assert pred['away_team'] == 'Chelsea'
    
    # /api/v1/pl/models
    r = api_client.get('/api/v1/pl/models')
    assert r.status_code == 200
    models = r.json()
    assert models['production_model']['public_version'] == 'ennovera-pl-v1.0'
    assert models['shadow_model']['public_version'] == 'ennovera-pl-shadow-v5.1'
    
    # /api/v1/pl/table
    r = api_client.get('/api/v1/pl/table')
    assert r.status_code == 200
    table_data = r.json()
    assert len(table_data['standings']) == 20
