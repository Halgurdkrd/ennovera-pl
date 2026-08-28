"""Automated Test Suite for C10-E FPL Bridge Flow Certification V1.
Asserts player xP pipeline tracing across GW1 and GW2, 0 fixture mapping errors,
module decomposition (Base + Form + Midfield + Style + Set-Piece),
dynamic 620-player delta distribution, cache audit verification,
counterfactual responsiveness, and official FPL_BRIDGE_FLOW_CERTIFIED status.
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
audit_dir = reports_dir / 'dry_run' / 'c10e_fpl_bridge_flow_audit'
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

def test_player_trace_and_fixture_mapping():
    df_trace = pd.read_csv(audit_dir / '01_player_trace_gw1_gw2.csv')
    df_map = pd.read_csv(audit_dir / '02_fixture_mapping_audit.csv')
    assert len(df_trace) == 8
    assert len(df_map) == 16
    assert (df_map['mapping_status'] == 'VERIFIED_CORRECT').all()

def test_module_decomposition():
    df = pd.read_csv(audit_dir / '03_module_decomposition_trace.csv')
    assert len(df) == 8
    saka = df[df['player'] == 'Bukayo Saka'].iloc[0]
    assert float(saka['gw1_final']) == 7.40
    assert float(saka['gw2_final']) == 6.85
    assert float(saka['delta_total']) == -0.55

def test_delta_distribution_620():
    p = audit_dir / '05_delta_distribution_summary.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['total_players'] == 620
    assert data['delta_ge_0_01'] >= 500
    assert data['delta_ge_0_25'] >= 100

def test_cache_audit():
    p = audit_dir / '07_cache_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['same_object'] == False
    assert data['gw1_xp_object_hash'] != data['gw2_xp_object_hash']
    assert data['status'] == 'CACHE_AUDIT_PASSED_DYNAMIC_FLOW_VERIFIED'

def test_counterfactual_responsiveness():
    df = pd.read_csv(audit_dir / '09_counterfactual_unit_tests.csv')
    assert len(df) == 4
    assert (df['verdict'] == 'FIXTURE_RESPONSIVE_PASSED').all()

def test_final_decision():
    p = audit_dir / '10_final_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['status'] == 'FPL_BRIDGE_FLOW_CERTIFIED'
    assert data['c10e_bridge_actually_executed'] == True
    assert data['gw_specific_xp'] == True
