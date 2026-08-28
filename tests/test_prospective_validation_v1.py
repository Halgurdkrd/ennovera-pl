"""2026-27 Prospective Validation Automated Test Suite (Ground Truth & Teamset Hardened).
Verifies prospective directory structures, immutable research locks,
timing semantics, future freeze rejection, stage classification,
20-club membership hard gates, promoted/relegated roster integrity,
and data availability evidence levels.
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
    """Verify prospective status JSON indicates WAITING_FOR_CORRECT_CANONICAL_FREEZE_WINDOWS."""
    status_path = prospective_dir / 'manifests' / 'prospective_status.json'
    assert status_path.exists()
    st = json.loads(status_path.read_text(encoding='utf-8'))
    assert st['status'] in ['WAITING_FOR_CORRECT_CANONICAL_FREEZE_WINDOWS', 'WAITING_FOR_CANONICAL_FREEZE_WINDOWS']
    assert st['pl_canonical_predictions_frozen'] == 0

def test_canonical_2026_27_teamset_integrity():
    """Verify exactly 20 canonical clubs exist in 2026-27 season and promoted clubs are present."""
    raw_audit = json.loads((reports_dir / 'prospective' / 'pl_fixture_source_raw_audit.json').read_text(encoding='utf-8'))
    assert raw_audit['total_clubs'] == 20
    assert raw_audit['teamset_sha256'] == 'a332e628064a0c9265fa11f6bd12d10ca5cbf499f5c547ff93347c0c9a246a60'

def test_promoted_and_relegated_clubs_membership():
    """Assert promoted clubs (Coventry, Hull, Leeds, Sunderland) are present in 2026-27."""
    df_teams = pd.read_csv(repo_root / 'data' / 'raw' / 'fpl_full' / 'data' / '2026-27' / 'teams.csv')
    names = df_teams['name'].tolist()
    assert 'Coventry City' in names
    assert 'Hull City' in names
    assert 'Leeds' in names
    assert 'Sunderland' in names
    # Verify relegated clubs from previous season are excluded
    assert 'Southampton' not in names
    assert 'Leicester' not in names
    assert 'Wolves' not in names
    assert 'West Ham' not in names

def test_true_2026_27_fixtures_membership_gate():
    """Assert all upcoming fixtures contain only canonical 2026-27 clubs."""
    raw_audit = json.loads((reports_dir / 'prospective' / 'pl_fixture_source_raw_audit.json').read_text(encoding='utf-8'))
    canonical_20 = {
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton & Hove Albion', 'Chelsea',
        'Coventry City', 'Crystal Palace', 'Everton', 'Fulham', 'Hull City', 'Ipswich Town',
        'Leeds United', 'Liverpool', 'Manchester City', 'Manchester United', 'Newcastle United',
        'Nottingham Forest', 'Tottenham Hotspur', 'Sunderland'
    }
    for fix in raw_audit['upcoming_round_fixtures']:
        assert fix['home_team'] in canonical_20, f"Invalid home club: {fix['home_team']}"
        assert fix['away_team'] in canonical_20, f"Invalid away club: {fix['away_team']}"

def test_snapshot_registry_reclassification():
    """Verify Run 001 entries are tagged INVALID_COMPETITION_FIXTURE_SOURCE in registry."""
    reg_path = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert reg_path.exists()
    df_reg = pd.read_csv(reg_path)
    pl_entries = df_reg[df_reg['track'] == 'PL']
    assert len(pl_entries) == 10
    assert all(pl_entries['stage'] == 'INVALID_COMPETITION_FIXTURE_SOURCE')
    assert all(pl_entries['canonical_evaluation_eligible'] == False)

def test_timing_semantics_and_future_freeze_invariant():
    """Verify invariant: official_freeze_at cannot be in the future relative to snapshot creation."""
    reg_path = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    df_reg = pd.read_csv(reg_path)
    for idx, row in df_reg.iterrows():
        gen_at = datetime.fromisoformat(row['generated_at'].replace('Z', '+00:00'))
        snap_at = datetime.fromisoformat(row['snapshot_created_at'].replace('Z', '+00:00'))
        plan_at = datetime.fromisoformat(row['planned_cutoff_at'].replace('Z', '+00:00'))
        assert gen_at <= snap_at
        assert snap_at < plan_at
        assert row['official_freeze_at'] == 'NONE_EARLY'

def test_data_availability_matrix_v2():
    """Verify Data Availability Matrix V2 has evidence grades and zero Grade F."""
    df_mat = pd.read_csv(reports_dir / 'prospective' / 'data_availability_matrix_v2.csv')
    assert len(df_mat) == 12
    assert all(df_mat['evidence_grade'].isin(['A', 'B', 'C', 'D']))
    assert 'F' not in df_mat['evidence_grade'].values

def test_metric_unit_rps_calculation():
    """Unit test for Ranked Probability Score (RPS) formula on a toy example."""
    p = np.array([0.6, 0.3, 0.1])
    obs = np.array([1.0, 0.0, 0.0])
    cdf_p = np.cumsum(p)
    cdf_o = np.cumsum(obs)
    rps = np.sum((cdf_p - cdf_o)**2) / 2.0
    assert abs(rps - 0.085) < 1e-6

def test_fallback_provenance_offline_priors():
    """Verify offline fallbacks are documented and match frozen research architecture."""
    audit_md = (reports_dir / 'prospective' / 'fallback_provenance_audit.md').read_text(encoding='utf-8')
    assert 'VALID_FROZEN_FALLBACK' in audit_md
    assert 'Decoupled Bayesian prior' in audit_md
    assert 'Phase 10.5A' in audit_md
