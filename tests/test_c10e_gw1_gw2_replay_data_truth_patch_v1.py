"""Automated Test Suite for C10-E GW1 + GW2 Replay Data Truth Patch V1.
Asserts authentic 2026-27 FPL player databases, 0 invalid club assignments,
exact price provenance (£0.1m precision), corrected legal FPL squads,
authentic old GW2 prospective artifact hash and probabilities, zero leakage, and strict governance.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

reports_dir = repo_root / 'reports'
patch_dir = reports_dir / 'dry_run' / 'c10e_gw1_gw2_replay_data_truth'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_protected_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_stale_registry_investigation():
    p = patch_dir / '01_stale_registry_investigation.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'MIXING_PRIOR_SEASON' in data['root_cause']
    assert 'PREVIOUS_FPL_REPLAY_INVALIDATED' in data['status']

def test_club_universe_hard_gate():
    p = patch_dir / '04_club_universe_hard_gate.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['gw1_invalid_clubs'] == 0
    assert data['gw2_invalid_clubs'] == 0
    assert len(data['authentic_20_clubs']) == 20
    assert data['status'] == 'CLUB_UNIVERSE_HARD_GATE_PASSED'

def test_price_hard_gate():
    df = pd.read_csv(patch_dir / '05_price_hard_gate.csv')
    assert len(df) >= 15
    assert (df['status'] == 'AUTHENTICATED').all()
    haaland = df[df['player'] == 'Erling Haaland'].iloc[0]
    assert float(haaland['official_price']) == 15.5

def test_corrected_gw1_fpl_squad():
    df = pd.read_csv(patch_dir / '07_gw1_fpl_corrected_squad.csv')
    assert len(df) == 15
    cost = df['price'].sum()
    assert cost <= 100.0
    club_counts = df['club'].value_counts()
    assert (club_counts <= 3).all()
    pos_counts = df['pos'].value_counts()
    assert pos_counts['GK'] == 2 and pos_counts['DEF'] == 5 and pos_counts['MID'] == 5 and pos_counts['FWD'] == 3

def test_corrected_captain_rankings():
    df1 = pd.read_csv(patch_dir / '09_gw1_corrected_captain_ranking.csv')
    df2 = pd.read_csv(patch_dir / '12_gw2_corrected_captain_ranking.csv')
    assert df1.iloc[0]['player'] == 'Erling Haaland' and df1.iloc[0]['selection'] == 'CAPTAIN'
    assert df2.iloc[0]['player'] == 'Erling Haaland' and df2.iloc[0]['selection'] == 'CAPTAIN'
    assert df2.iloc[1]['player'] == 'Cole Palmer' and df2.iloc[1]['selection'] == 'VICE_CAPTAIN'

def test_old_gw2_artifact_authentication():
    p = patch_dir / '13_old_gw2_artifact_forensics.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['old_gw2_artifact_authentic'] == 'YES'
    assert data['sha256'] == '07db1a6ff58675a1f4c8fdf5549e2916c6b23ec5a3f93dada86c3e864a36af0f'
    palace_city = data['stored_exact_probabilities'][0]
    assert palace_city['p_h'] == 0.15 and palace_city['p_d'] == 0.22 and palace_city['p_a'] == 0.63

def test_data_integrity_audit():
    p = patch_dir / '16_data_integrity_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['invalid_clubs'] == 0
    assert data['stale_prices'] == 0
    assert data['post_cutoff_fpl_data'] == 0
    assert data['post_cutoff_pl_features'] == 0
    assert data['status'] == 'DATA_TRUTH_PRISTINE'
