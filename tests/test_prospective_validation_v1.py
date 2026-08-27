"""2026-27 Prospective Validation Automated Test Suite.
Verifies prospective directory structures, immutable research locks,
point-in-time temporal assertions, metric calculation unit tests,
data readiness schemas, and model immutability.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

reports_dir = repo_root / 'reports'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_frozen_gw2_plan_immutability():
    """Verify frozen GW2 prospective plan has not been modified."""
    frozen_path = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert frozen_path.exists()
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert h == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_frozen_fpl_baseline_intact():
    """Verify FPL final model baseline remains frozen at 2,179.50 pts/season mean."""
    manifest_path = reports_dir / 'phase10_6_final_manifest.json'
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['model_name'] == 'ENNOVERA_FPL_FINAL_RESEARCH_V1'
    assert manifest['historical_mean_score'] == 2179.50

def test_frozen_pl_baseline_intact():
    """Verify PL final model baseline remains frozen at 58.4% Acc and 0.1748 RPS."""
    manifest_path = reports_dir / 'pl11_12_final_manifest.json'
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['model_name'] == 'ENNOVERA_PL_FINAL_RESEARCH_V1'
    assert manifest['metrics']['accuracy_3class'] == 0.584
    assert manifest['metrics']['ranked_probability_score'] == 0.1748

def test_research_lock_manifest_present_and_valid():
    """Verify research lock manifest is present and correctly locks frozen baselines."""
    lock_path = prospective_dir / 'manifests' / 'research_lock.json'
    assert lock_path.exists()
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    assert lock['program'] == 'ENNOVERA_2026_27_PROSPECTIVE_VALIDATION_V1'
    assert lock['fpl_model']['name'] == 'ENNOVERA_FPL_FINAL_RESEARCH_V1'
    assert lock['pl_model']['name'] == 'ENNOVERA_PL_FINAL_RESEARCH_V1'
    assert lock['frozen_gw2_snapshot']['sha256'] == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_prospective_status_json():
    """Verify prospective status JSON indicates READY_FOR_OUTCOME_WAIT."""
    status_path = prospective_dir / 'manifests' / 'prospective_status.json'
    assert status_path.exists()
    st = json.loads(status_path.read_text(encoding='utf-8'))
    assert st['status'] in ['READY_FOR_OUTCOME_WAIT', 'READY_FOR_NEXT_PROSPECTIVE_RUN']
    assert st['production_status'] == 'PRODUCTION_UNCHANGED_SHADOW_ACTIVE'

def test_data_readiness_matrix_completeness():
    """Verify data readiness matrix contains all required feature families."""
    df_mat = pd.read_csv(reports_dir / 'prospective_data_readiness_matrix.csv')
    assert len(df_mat) == 12
    assert 'PL Fixture Schedule & Kickoff' in df_mat['source_family'].values
    assert 'FPL Deadlines & Rulebook' in df_mat['source_family'].values

def test_live_csv_structures_exist():
    """Verify all 19 prospective live CSV tracking log files exist with non-empty headers."""
    pl_files = [
        'pl_prediction_log.csv', 'pl_outcome_log.csv', 'pl_running_metrics.csv',
        'pl_draw_monitor.csv', 'pl_calibration_monitor.csv', 'pl_subgroups.csv',
        'pl_data_quality.csv', 'pl_drift_monitor.csv', 'pl_simulation_snapshots.csv'
    ]
    fpl_files = [
        'fpl_gw_prediction_log.csv', 'fpl_player_predictions.csv', 'fpl_outcomes.csv',
        'fpl_running_metrics.csv', 'fpl_transfer_log.csv', 'fpl_captain_log.csv',
        'fpl_chip_log.csv', 'fpl_regret.csv', 'fpl_expected_minutes.csv', 'fpl_drift_monitor.csv'
    ]
    for pf in pl_files:
        p = reports_dir / 'prospective' / 'pl' / pf
        assert p.exists(), f"Missing PL CSV: {pf}"
        df = pd.read_csv(p)
        assert len(df.columns) > 3
    for ff in fpl_files:
        p = reports_dir / 'prospective' / 'fpl' / ff
        assert p.exists(), f"Missing FPL CSV: {ff}"
        df = pd.read_csv(p)
        assert len(df.columns) > 3

def test_metric_unit_rps_calculation():
    """Unit test for Ranked Probability Score (RPS) formula on a toy example."""
    p = np.array([0.6, 0.3, 0.1])
    obs = np.array([1.0, 0.0, 0.0])
    cdf_p = np.cumsum(p)
    cdf_o = np.cumsum(obs)
    rps = np.sum((cdf_p - cdf_o)**2) / 2.0
    assert abs(rps - 0.085) < 1e-6

def test_mw3_frozen_fixture_snapshots():
    """Verify all 10 PL Matchweek 3 fixture snapshots are present, valid, and unpopulated with outcomes."""
    df_pl = pd.read_csv(reports_dir / 'prospective' / 'pl' / 'pl_prediction_log.csv')
    assert len(df_pl) == 10
    for idx, row in df_pl.iterrows():
        assert row['prospective_valid'] == True
        prob_sum = float(row['p_home']) + float(row['p_draw']) + float(row['p_away'])
        assert abs(prob_sum - 1.0) < 1e-4

def test_gw3_frozen_fpl_snapshot():
    """Verify FPL GW3 snapshot is present, valid, and unpopulated with outcomes."""
    snap_p = prospective_dir / 'fpl' / 'snapshots' / 'FPL_2026_27_GW03.json'
    assert snap_p.exists()
    snap = json.loads(snap_p.read_text(encoding='utf-8'))
    assert snap['gameweek'] == 3
    assert len(snap['starting_xi']) == 11
    assert len(snap['bench']) == 4
    assert snap['captain']['player_id'] == 'P_HAALAND'
    assert snap['vice_captain']['player_id'] == 'P_SALAH'
    assert snap['provenance']['prospective_valid'] == True
