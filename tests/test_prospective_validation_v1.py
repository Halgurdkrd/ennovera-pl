"""2026-27 Prospective Validation Automated Test Suite (Hardened Governance v2).
Verifies prospective directory structures, immutable research locks,
timing semantics, future freeze rejection, stage classification,
fallback provenance, duplicate prevention, and counter accuracy.
"""
import sys
import json
import hashlib
from datetime import datetime, timezone
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

def test_research_lock_v2_hash_reconciliation():
    """Verify research lock v2 documents canonical physical hashes accurately."""
    lock_v2_path = prospective_dir / 'manifests' / 'research_lock_v2_hash_reconciliation.json'
    assert lock_v2_path.exists()
    lock_v2 = json.loads(lock_v2_path.read_text(encoding='utf-8'))
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    assert lock_v2['fpl_model']['canonical_artifact_sha256'] == hashlib.sha256(fpl_p.read_bytes()).hexdigest()
    assert lock_v2['pl_model']['canonical_artifact_sha256'] == hashlib.sha256(pl_p.read_bytes()).hexdigest()

def test_prospective_status_json():
    """Verify prospective status JSON indicates WAITING_FOR_CANONICAL_FREEZE_WINDOWS."""
    status_path = prospective_dir / 'manifests' / 'prospective_status.json'
    assert status_path.exists()
    st = json.loads(status_path.read_text(encoding='utf-8'))
    assert st['status'] == 'WAITING_FOR_CANONICAL_FREEZE_WINDOWS'
    assert st['pl_canonical_predictions_frozen'] == 0
    assert st['pl_early_forecasts_total'] == 10

def test_data_readiness_matrix_completeness():
    """Verify data readiness matrix contains all required feature families."""
    df_mat = pd.read_csv(reports_dir / 'prospective_data_readiness_matrix.csv')
    assert len(df_mat) == 12
    assert 'PL Fixture Schedule & Kickoff' in df_mat['source_family'].values
    assert 'FPL Deadlines & Rulebook' in df_mat['source_family'].values

def test_snapshot_registry_structure_and_uniqueness():
    """Verify snapshot registry exists and has zero duplicate canonical entries."""
    reg_path = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert reg_path.exists()
    df_reg = pd.read_csv(reg_path)
    assert len(df_reg) == 11
    # Zero canonical entries in early forecast batch
    canonical_entries = df_reg[df_reg['canonical_evaluation_eligible'] == True]
    assert len(canonical_entries) == 0
    # All 10 PL entries are EARLY_FORECAST
    pl_early = df_reg[df_reg['track'] == 'PL']
    assert len(pl_early) == 10
    assert all(pl_early['stage'] == 'EARLY_FORECAST')

def test_timing_semantics_and_future_freeze_invariant():
    """Verify invariant: official_freeze_at cannot be in the future relative to snapshot creation."""
    reg_path = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    df_reg = pd.read_csv(reg_path)
    for idx, row in df_reg.iterrows():
        gen_at = datetime.fromisoformat(row['generated_at'].replace('Z', '+00:00'))
        snap_at = datetime.fromisoformat(row['snapshot_created_at'].replace('Z', '+00:00'))
        plan_at = datetime.fromisoformat(row['planned_cutoff_at'].replace('Z', '+00:00'))
        assert gen_at <= snap_at
        assert snap_at < plan_at  # Generated early
        assert row['official_freeze_at'] == 'NONE_EARLY'

def test_metric_unit_rps_calculation():
    """Unit test for Ranked Probability Score (RPS) formula on a toy example."""
    p = np.array([0.6, 0.3, 0.1])
    obs = np.array([1.0, 0.0, 0.0])
    cdf_p = np.cumsum(p)
    cdf_o = np.cumsum(obs)
    rps = np.sum((cdf_p - cdf_o)**2) / 2.0
    assert abs(rps - 0.085) < 1e-6

def test_mw3_early_fixture_snapshots_preserved():
    """Verify all 10 PL Matchweek 3 fixture snapshots are preserved with non-canonical flags."""
    df_pl = pd.read_csv(reports_dir / 'prospective' / 'pl' / 'pl_prediction_log.csv')
    assert len(df_pl) == 10
    for idx, row in df_pl.iterrows():
        assert row['prospective_valid'] == False  # Early forecast, not canonical benchmark
        assert row['snapshot_stage'] == 'EARLY_FORECAST'
        prob_sum = float(row['p_home']) + float(row['p_draw']) + float(row['p_away'])
        assert abs(prob_sum - 1.0) < 1e-4

def test_gw3_early_fpl_snapshot_preserved():
    """Verify FPL GW3 snapshot is preserved with early stage classification."""
    snap_p = prospective_dir / 'fpl' / 'snapshots' / 'FPL_2026_27_GW03.json'
    assert snap_p.exists()
    snap = json.loads(snap_p.read_text(encoding='utf-8'))
    assert snap['gameweek'] == 3
    assert len(snap['starting_xi']) == 11
    assert len(snap['bench']) == 4

def test_drift_language_insufficient_sample():
    """Verify drift monitor reports insufficient sample rather than premature zero drift."""
    status_path = prospective_dir / 'manifests' / 'prospective_status.json'
    st = json.loads(status_path.read_text(encoding='utf-8'))
    assert st['drift_status'] == 'INSUFFICIENT_SAMPLE_FOR_DRIFT_CONCLUSION'

def test_fallback_provenance_offline_priors():
    """Verify offline fallbacks are documented and match frozen research architecture."""
    audit_md = (reports_dir / 'prospective' / 'fallback_provenance_audit.md').read_text(encoding='utf-8')
    assert 'VALID_FROZEN_FALLBACK' in audit_md
    assert 'Decoupled Bayesian prior' in audit_md
    assert 'Phase 10.5A' in audit_md
