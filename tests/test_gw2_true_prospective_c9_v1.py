"""Automated Test Suite for GW2 True Prospective C9 + FPL Freeze.
Asserts pre-deadline timing, 10 PL fixture forecasts, 30 top FPL players, legal 15-player squad (£99.5m),
legal 3-5-2 XI (69.3 base xP), Salah captaincy (8.4 xP, 10.2 utility), and immutable prospective freeze.
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
audit_dir = reports_dir / 'dry_run' / 'gw2_true_prospective_c9_v1'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_gw2_prospective_manifest():
    p = audit_dir / '14_gw2_c9_prospective_manifest.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['mode'] == 'TRUE_PROSPECTIVE'
    assert data['immutability_status'] == 'GW2_TRUE_PROSPECTIVE_FROZEN'
    created_dt = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
    deadline_dt = datetime.fromisoformat(data['fpl_deadline'].replace('Z', '+00:00'))
    assert created_dt < deadline_dt

def test_gw1_state_update_audit():
    df = pd.read_csv(audit_dir / '02_gw1_state_update_audit.csv')
    assert len(df) == 20
    assert (df['shrinkage_factor'] == 0.08).all()

def test_gw2_pl_predictions():
    df = pd.read_csv(audit_dir / '03_gw2_c9_pl_predictions.csv')
    assert len(df) == 10
    for idx, row in df.iterrows():
        p_tot = row['p_h'] + row['p_d'] + row['p_a']
        assert abs(p_tot - 1.0) < 1e-4

def test_gw2_fpl_top30_count():
    df = pd.read_csv(audit_dir / '05_gw2_c9_fpl_top30.csv')
    assert len(df) == 30
    assert df.iloc[0]['player'] == 'Mohamed Salah' and df.iloc[0]['xp'] == 8.4
    assert df.iloc[1]['player'] == 'Erling Haaland' and df.iloc[1]['xp'] == 7.9
    assert df.iloc[2]['player'] == 'Bukayo Saka' and df.iloc[2]['xp'] == 7.2

def test_15_player_squad_legality():
    p = audit_dir / '06_gw2_c9_fpl_15_player_squad.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['total_cost'] <= 100.0
    assert data['money_in_bank'] == 0.5
    squad = data['squad']
    assert len(squad) == 15
    gks = [x for x in squad if x['position'] == 'GK']
    defs = [x for x in squad if x['position'] == 'DEF']
    mids = [x for x in squad if x['position'] == 'MID']
    fwds = [x for x in squad if x['position'] == 'FWD']
    assert len(gks) == 2 and len(defs) == 5 and len(mids) == 5 and len(fwds) == 3
    # Check max 3 players per club
    clubs = [x['club'] for x in squad]
    for c in set(clubs):
        assert clubs.count(c) <= 3

def test_starting_xi_legality_and_xp():
    p = audit_dir / '07_gw2_c9_fpl_xi.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['formation'] == '3-5-2'
    assert data['starting_xi_base_xp'] == 69.3
    xi = data['starting_xi']
    assert len(xi) == 11
    tot_xp = sum(x['xp'] for x in xi)
    assert abs(tot_xp - 69.3) < 1e-4

def test_bench_order():
    df = pd.read_csv(audit_dir / '08_gw2_c9_fpl_bench.csv')
    assert len(df) == 4
    assert df.iloc[0]['slot'] == 'GK'
    assert 'Priority 1' in df.iloc[1]['autosub_priority']

def test_captain_and_vice():
    p = audit_dir / '09_gw2_c9_fpl_captain.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['captain']['player'] == 'Mohamed Salah'
    assert data['captain']['mean_xp'] == 8.4
    assert data['captain']['captain_utility'] == 10.2
    assert data['vice_captain']['player'] == 'Erling Haaland'
    assert data['vice_captain']['mean_xp'] == 7.9
    assert len(data['top_5_alternatives']) == 5

def test_transfer_and_chip_decision():
    df = pd.read_csv(audit_dir / '10_gw2_transfer_chip_decision.csv')
    t_row = df[df['decision_type'] == 'Transfer'].iloc[0]
    c_row = df[df['decision_type'] == 'Chip'].iloc[0]
    assert 'ROLL TRANSFER' in t_row['recommendation']
    assert 'NO CHIP' in c_row['recommendation']

def test_data_truth_manifest():
    p = audit_dir / '12_gw2_data_truth_manifest.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['gw2_outcomes_used'] == False
    assert data['gw1_outcomes_ingested'] == True

def test_prospective_snapshots_in_live_dir():
    assert (live_gw2_dir / 'GW2_C9_PROSPECTIVE_PREDICTION.json').exists()
    assert (live_gw2_dir / 'GW2_C9_FPL_15_PLAYER_SQUAD.json').exists()
    assert (live_gw2_dir / 'GW2_C9_FPL_XI.json').exists()
    assert (live_gw2_dir / 'GW2_C9_FPL_CAPTAIN.json').exists()
    assert (live_gw2_dir / 'GW2_PROSPECTIVE_MANIFEST.json').exists()

def test_immutability_verification():
    p = audit_dir / '15_immutability_verification.md'
    assert p.exists()
    assert 'GW2_TRUE_PROSPECTIVE_FROZEN' in p.read_text(encoding='utf-8')

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
