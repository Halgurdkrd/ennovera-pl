"""Automated Test Suite for GW2 Live Data Truth Emergency Recovery V1.
Asserts invalidation of V1 template, authentic 2026-27 bootstrap data (Haaland 15.5m, Palmer 9.5m, Isak Liverpool 9.0m),
budget legality (£99.8m <= £100.0m), 3-4-3 formation (66.9 base xP), Haaland captaincy, and pre-deadline V2 freeze.
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
audit_dir = reports_dir / 'dry_run' / 'gw2_live_data_truth_recovery_v1'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_v1_invalidated_audit():
    p = audit_dir / '02_v1_invalidated_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'GW2_PROSPECTIVE_INVALIDATED' in data['status']
    assert data['preserved_for_audit'] == True

def test_20_pl_clubs_authenticated():
    df = pd.read_csv(audit_dir / '03_pl_20_clubs_authenticated.csv')
    assert len(df) == 20
    clubs = df['club_name'].tolist()
    assert 'Arsenal' in clubs and 'Liverpool' in clubs and 'Hull City' in clubs
    assert 'West Ham' not in clubs and 'Leicester' not in clubs

def test_canary_comparison_table():
    df = pd.read_csv(audit_dir / '05_canary_comparison_table.csv')
    h_row = df[df['player'] == 'Erling Haaland'].iloc[0]
    p_row = df[df['player'] == 'Cole Palmer'].iloc[0]
    i_row = df[df['player'] == 'Alexander Isak'].iloc[0]
    assert '15.5m' in h_row['authenticated_state']
    assert '9.5m' in p_row['authenticated_state']
    assert 'Liverpool' in i_row['authenticated_state'] and '9.0m' in i_row['authenticated_state']

def test_departed_players_ineligible():
    df = pd.read_csv(audit_dir / '05_canary_comparison_table.csv')
    s_row = df[df['player'] == 'Mohamed Salah'].iloc[0]
    t_row = df[df['player'] == 'Trent Alexander-Arnold'].iloc[0]
    f_row = df[df['player'] == 'Wout Faes'].iloc[0]
    fb_row = df[df['player'] == 'Lukasz Fabianski'].iloc[0]
    assert s_row['result'] == 'INELIGIBLE_REMOVED'
    assert t_row['result'] == 'INELIGIBLE_REMOVED'
    assert f_row['result'] == 'INELIGIBLE_REMOVED'
    assert fb_row['result'] == 'INELIGIBLE_REMOVED'

def test_budget_recomputation():
    df = pd.read_csv(audit_dir / '07_budget_recomputation_audit.csv')
    assert len(df) == 15
    tot_price = df['price'].sum()
    assert tot_price <= 100.0
    assert abs(tot_price - 99.8) < 1e-4

def test_recomputed_pl_predictions():
    df = pd.read_csv(audit_dir / '09_gw2_pl_recomputed_predictions.csv')
    assert len(df) == 10
    for idx, row in df.iterrows():
        p_tot = row['new_p_h'] + row['new_p_d'] + row['new_p_a']
        assert abs(p_tot - 1.0) < 1e-4

def test_squad_v2_legality():
    p = audit_dir / '11_gw2_c9_fpl_15_squad_v2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['total_cost'] <= 100.0
    assert data['money_in_bank'] == 0.2
    squad = data['squad']
    assert len(squad) == 15
    gks = [x for x in squad if x['position'] == 'GK']
    defs = [x for x in squad if x['position'] == 'DEF']
    mids = [x for x in squad if x['position'] == 'MID']
    fwds = [x for x in squad if x['position'] == 'FWD']
    assert len(gks) == 2 and len(defs) == 5 and len(mids) == 5 and len(fwds) == 3
    clubs = [x['club'] for x in squad]
    for c in set(clubs):
        assert clubs.count(c) <= 3

def test_xi_v2_legality_and_xp():
    p = audit_dir / '12_gw2_c9_fpl_xi_v2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['formation'] == '3-4-3'
    assert data['starting_xi_base_xp'] == 66.9
    xi = data['starting_xi']
    assert len(xi) == 11
    tot_xp = sum(x['xp'] for x in xi)
    assert abs(tot_xp - 66.9) < 1e-4

def test_captain_v2_selection():
    p = audit_dir / '13_gw2_c9_fpl_captain_v2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['captain']['player'] == 'Erling Haaland'
    assert data['captain']['price'] == 15.5
    assert data['captain']['mean_xp'] == 8.1
    assert data['vice_captain']['player'] == 'Cole Palmer'
    assert data['vice_captain']['price'] == 9.5
    assert data['vice_captain']['mean_xp'] == 7.6

def test_manifest_v2_timing():
    p = audit_dir / '15_gw2_prospective_manifest_v2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['mode'] == 'TRUE_PROSPECTIVE'
    assert data['immutability_status'] == 'GW2_PROSPECTIVE_V2_FROZEN'
    gen_dt = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))
    dead_dt = datetime.fromisoformat(data['fpl_deadline'].replace('Z', '+00:00'))
    assert gen_dt < dead_dt

def test_live_snapshots_v2_exist():
    assert (live_gw2_dir / 'GW2_C9_PROSPECTIVE_V2_CORRECTED.json').exists()
    assert (live_gw2_dir / 'GW2_C9_FPL_15_SQUAD_V2.json').exists()
    assert (live_gw2_dir / 'GW2_C9_FPL_XI_V2.json').exists()
    assert (live_gw2_dir / 'GW2_C9_FPL_CAPTAIN_V2.json').exists()
    assert (live_gw2_dir / 'GW2_PROSPECTIVE_MANIFEST_V2.json').exists()

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
