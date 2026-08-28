"""Automated Test Suite for C10-E GW2 FPL Final Render Patch V1.
Asserts authentic object hashes, distinct GW1/GW2 vectors,
exact arithmetic verification (Starting XI 66.15 + Captain 7.90 = 74.05),
captaincy rankings, realistic vs from-scratch efficiency (99.46%),
and report rendering correction provenance.
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
render_dir = reports_dir / 'dry_run' / 'c10e_gw2_fpl_render_patch'
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

def test_authentic_object_hashes():
    p = render_dir / '01_authentic_object_hashes.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['c10e_model_hash'] == '95a70fe854b4237d9b9323381a1795c378aa89cbb3b90da893eaef3ef7ce8371'
    assert data['fpl_bridge_hash'] == 'b4e8921af78c01625da38290f146a89c201948ba12049c823058240be363cca2'
    assert data['gw1_xp_hash'] == '3e5e6e30018f6f57876a40a831e5f8fdf48074d28e75fa9ee0e6c5c05ab59ce2'
    assert data['gw2_xp_hash'] == 'b90a61849e75924fa682e022f46a29be634351a6697b09325603f9050d2ce2c2'
    assert data['hashes_distinct'] == True

def test_gw2_squad_and_arithmetic():
    df = pd.read_csv(render_dir / '02_gw2_fpl_realistic_path_corrected.csv')
    assert len(df) == 15
    starting_xi = df[df['lineup_role'].str.contains('STARTING_XI')]
    assert len(starting_xi) == 11
    xi_sum = round(starting_xi['gw2_xp'].sum(), 2)
    assert xi_sum == 66.15
    capt = starting_xi[starting_xi['lineup_role'].str.endswith('(C)')].iloc[0]
    assert capt['player'] == 'Erling Haaland' and float(capt['gw2_xp']) == 7.90
    total = round(xi_sum + float(capt['gw2_xp']), 2)
    assert total == 74.05

def test_top10_captains():
    df = pd.read_csv(render_dir / '05_gw2_top10_captains.csv')
    assert len(df) == 10
    assert df.iloc[0]['player'] == 'Erling Haaland' and df.iloc[0]['selection'] == 'CAPTAIN'
    assert df.iloc[1]['player'] == 'Cole Palmer' and df.iloc[1]['selection'] == 'VICE_CAPTAIN'

def test_realistic_vs_from_scratch():
    df = pd.read_csv(render_dir / '06_gw2_from_scratch_comparison.csv')
    assert len(df) == 2
    r_pts = df.iloc[0]['total_expected_points']
    fs_pts = df.iloc[1]['total_expected_points']
    eff = round(r_pts / fs_pts * 100, 2)
    assert eff == 99.46

def test_report_rendering_correction():
    p = render_dir / '08_report_rendering_correction_manifest.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['previous_gw2_displayed_xp'] == 'INVALIDATED'
    assert data['reason'] == 'GW1_TABLE_DISPLAY_PLACEHOLDER'
    assert data['underlying_gw2_prediction_object'] == 'VALID'
