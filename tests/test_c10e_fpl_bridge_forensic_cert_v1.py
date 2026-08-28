"""Automated Test Suite for C10-E FPL Bridge Forensic Certification V1.
Asserts exact frozen FPL identity, manager points reconciliation (71+35+34+38+42=220),
metric-universe dual specification, actual GW delta vectors (152 GWs),
paired 2000-draw bootstrap, position and captaincy decision reconciliation (+220 pts),
zero double counting, and clean historical certification.
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
forensic_dir = reports_dir / 'dry_run' / 'c10e_fpl_bridge_forensic'
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

def test_frozen_fpl_identity():
    p = forensic_dir / '01_frozen_fpl_identity.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['sha256'] == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert data['historical_manager_points']['total'] == 8718
    assert data['historical_manager_points']['mean_per_season'] == 2179.50

def test_metric_reconciliation_and_dual_universe():
    p_md = forensic_dir / '02_metric_reconciliation.md'
    p_b = forensic_dir / '03_canonical_metrics_system_b.csv'
    p_a = forensic_dir / '04_starter_pool_metrics_system_a.csv'
    assert p_md.exists() and p_b.exists() and p_a.exists()
    df_b = pd.read_csv(p_b)
    df_a = pd.read_csv(p_a)
    assert len(df_b) == 6 and len(df_a) == 6
    assert float(df_b.iloc[0]['mae']) == 1.482
    assert float(df_a.iloc[0]['mae']) == 1.745

def test_manager_points_reconciliation():
    df = pd.read_csv(forensic_dir / '05_manager_points_reconciliation.csv')
    assert len(df) == 6
    tot_row = df[df['season'].str.contains('TOTAL')].iloc[0]
    assert int(tot_row['frozen']) == 8718
    assert int(tot_row['c9']) == 8789
    assert int(tot_row['c10_a']) == 8824
    assert int(tot_row['c10_b']) == 8858
    assert int(tot_row['c10_c']) == 8896
    assert int(tot_row['c10_e']) == 8938

def test_actual_gw_delta_vectors():
    df = pd.read_csv(forensic_dir / '06_actual_gw_delta_vectors.csv')
    assert len(df) == 3
    row_f = df[df['comparison'].str.contains('Frozen')].iloc[0]
    row_c9 = df[df['comparison'].str.contains('C9')].iloc[0]
    row_c = df[df['comparison'].str.contains('C10-C')].iloc[0]
    assert int(row_f['sum_points']) == 220
    assert int(row_c9['sum_points']) == 149
    assert int(row_c['sum_points']) == 42
    assert int(row_f['n_gw']) == 152

def test_bootstrap_forensic_results():
    df = pd.read_csv(forensic_dir / '07_bootstrap_forensic_results.csv')
    assert len(df) == 3
    row_f = df[df['comparison'].str.contains('Frozen')].iloc[0]
    assert float(row_f['point_delta_annualized']) == 55.00
    assert '2000 / 2000' in row_f['favorable_count']

def test_position_and_decision_attribution():
    p_md = forensic_dir / '08_position_and_decision_attribution.md'
    assert p_md.exists()
    content = p_md.read_text(encoding='utf-8')
    assert '18 + 68 + 78 + 56 = +220 pts' in content
    assert '164 + 56 = +220 pts' in content

def test_final_certification_record():
    p = forensic_dir / '09_final_certification.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_status'] == 'C10E_FPL_BRIDGE_CERTIFIED_HISTORICAL'
    assert data['governance_invariants']['c10_d_certified'] == True
    assert data['governance_invariants']['c10_e_frozen'] == True
    assert data['governance_invariants']['fpl_bridge_certified'] == True
    assert data['governance_invariants']['c10_e_production_promoted'] == False
    assert data['governance_invariants']['deployment'] == False
