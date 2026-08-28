"""Automated Test Suite for GW2 Final Prospective Integrity Lock V1.
Asserts pre-deadline timing, V1 preservation, 20-club universe, 615 active players, 50-player sample pass,
exact SHA-256 manifest uniqueness, legal squad (£99.8m), 3-4-3 formation (66.9 xP), Haaland captaincy, and write-lock marker.
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
audit_dir = reports_dir / 'dry_run' / 'gw2_final_prospective_lock_v1'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_starting_condition_timing():
    p = audit_dir / '02_v1_v2_separation_proof.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    gen_dt = datetime.fromisoformat(data['v2_created_at'].replace('Z', '+00:00'))
    dead_dt = datetime.fromisoformat(data['fpl_deadline'].replace('Z', '+00:00'))
    assert gen_dt < dead_dt
    assert data['v1_preserved_for_audit'] == True

def test_v1_v2_distinct():
    p = audit_dir / '02_v1_v2_separation_proof.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['distinct_artifacts'] == True
    assert data['v1_artifact_path'] != data['v2_artifact_path']

def test_20_clubs_recalculated():
    df = pd.read_csv(audit_dir / '04_pl_20_clubs_authenticated.csv')
    assert len(df) == 20
    clubs = df['club_name'].tolist()
    assert 'Arsenal' in clubs and 'Man City' in clubs and 'Liverpool' in clubs

def test_616_players_registry():
    df = pd.read_csv(audit_dir / '03_live_fpl_universe_recalculated.csv')
    tot_row = df[df['metric'].str.contains('Total Active FPL Players')].iloc[0]
    assert int(tot_row['value']) == 616

def test_sample_50_audit():
    df = pd.read_csv(audit_dir / '06_canary_and_sample50_audit.csv')
    assert len(df) == 50
    assert (df['audit_result'] == 'PASS').all()

def test_source_manifest_structure():
    p = audit_dir / '07_source_manifest_v2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'primary_live_sources' in data
    assert 'derived_internal_tables' in data

def test_fpl_bootstrap_provenance():
    p = audit_dir / '08_fpl_bootstrap_provenance.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['player_count'] == 616
    assert data['club_count'] == 20

def test_manager_current_registry():
    df = pd.read_csv(audit_dir / '10_manager_current_registry.csv')
    assert len(df) == 20
    assert (df['cutoff_valid'] == True).all()

def test_expected_xi_cutoff_audit():
    df = pd.read_csv(audit_dir / '11_expected_xi_cutoff_audit.csv')
    assert df.iloc[0]['status'] == 'PASS'
    assert df.iloc[0]['confirmed_lineups_used'] == False

def test_live_feature_store_audit():
    df = pd.read_csv(audit_dir / '12_live_feature_store_audit.csv')
    assert (df['count'] == 0).all()
    assert (df['status'] == 'PASS').all()

def test_gw1_state_shrinkage_weight():
    df = pd.read_csv(audit_dir / '13_gw1_state_shrinkage_verification.csv')
    w_row = df[df['parameter'].str.contains('Shrinkage Weight')].iloc[0]
    assert float(w_row['verified_value']) == 0.08

def test_sha256_manifest_uniqueness():
    df = pd.read_csv(audit_dir / '14_sha256_standardized_manifest.csv')
    assert len(df) == 12
    hashes = df['sha256'].tolist()
    assert len(hashes) == len(set(hashes))

def test_read_only_reproduced_pl_predictions():
    df = pd.read_csv(audit_dir / '15_gw2_c9_pl_reproduced_readonly.csv')
    assert len(df) == 10
    for idx, row in df.iterrows():
        p_tot = row['new_p_h'] + row['new_p_d'] + row['new_p_a']
        assert abs(p_tot - 1.0) < 1e-4

def test_read_only_reproduced_squad_and_budget():
    p = audit_dir / '16_gw2_c9_fpl_reproduced_readonly.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['total_cost'] == 99.8
    assert data['money_in_bank'] == 0.2
    assert data['formation'] == '3-4-3'
    assert data['starting_xi_base_xp'] == 66.9

def test_read_only_captain_derivation():
    p = live_gw2_dir / 'GW2_C9_FPL_CAPTAIN_V2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['captain']['player'] == 'Erling Haaland'
    assert data['captain']['mean_xp'] == 8.1
    assert data['captain']['captain_utility'] == 10.1
    assert data['vice_captain']['player'] == 'Cole Palmer'
    assert data['vice_captain']['mean_xp'] == 7.6
    assert data['vice_captain']['captain_utility'] == 9.4

def test_final_lock_manifest():
    p = audit_dir / '18_final_lock_manifest.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['prospective_certification'] == 'GW2_TRUE_PROSPECTIVE_CERTIFIED'
    assert data['status'] == 'GW2_C9_PROSPECTIVE_V2_LOCKED'

def test_write_lock_marker_exists():
    p = live_gw2_dir / 'GW2_C9_PROSPECTIVE_V2_LOCKED'
    assert p.exists()
    assert 'LOCKED_AT_' in p.read_text(encoding='utf-8')

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
