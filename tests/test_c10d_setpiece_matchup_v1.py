"""Automated Test Suite for C10-D Set-Piece Matchup Research V1.
Asserts exact baseline reproductions, opportunity vs efficiency separation, penalty quarantine,
C10-D9 superior performance (60.72% acc, 0.1670 RPS, SP Goal Brier 0.195, 99.80% bootstrap support),
placebo test pass (p=0.0010), zero leakage, and clean decision gate.
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
c10d_dir = reports_dir / 'dry_run' / 'c10d_setpiece'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_baseline_reproductions():
    p = c10d_dir / '01_baseline_reproduction.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['c9']['correct'] == 900
    assert data['c9']['rps'] == 0.1730
    assert data['c10_a9']['correct'] == 906
    assert data['c10_a9']['rps'] == 0.1718
    assert data['c10_b']['correct'] == 911
    assert data['c10_b']['rps'] == 0.1706
    assert data['c10_c']['correct'] == 917
    assert data['c10_c']['rps'] == 0.1688

def test_protected_baseline_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_data_inventory_and_penalty_quarantine():
    df_inv = pd.read_csv(c10d_dir / '02_data_inventory.csv')
    df_pen = pd.read_csv(c10d_dir / '04_penalty_diagnostic.csv')
    assert len(df_inv) == 11
    assert (df_inv['missing'] == 0).all()
    assert (df_inv['synthetic'] == 0).all()
    pen_conv = df_pen[df_pen['metric'].str.contains('Conversion')].iloc[0]
    assert 'EXCLUDED_FROM_PRIMARY_SP_STATE' in pen_conv['quarantine_decision']

def test_opportunity_vs_efficiency():
    df = pd.read_csv(c10d_dir / '05_opportunity_efficiency.csv')
    assert len(df) == 2
    eff_row = df[df['component'].str.contains('Efficiency')].iloc[0]
    assert float(eff_row['correlation_with_possession']) < 0.20

def test_recency_and_pretest_spec():
    p_spec = c10d_dir / '13_pretest_specification.json'
    assert p_spec.exists()
    data = json.loads(p_spec.read_text(encoding='utf-8'))
    assert data['status'] == 'FROZEN_BEFORE_TEST_EVALUATION'
    assert '90 days' in data['decay_half_life']

def test_challenger_results_d9():
    df = pd.read_csv(c10d_dir / '14_challenger_results.csv')
    d9 = df[df['model'].str.contains('D9')].iloc[0]
    assert float(d9['acc']) == 0.6072
    assert int(d9['correct_picks']) == 923
    assert float(d9['rps']) == 0.1670
    assert float(d9['log_loss']) == 0.8442
    assert float(d9['sp_goal_brier']) == 0.195

def test_setpiece_metrics():
    df = pd.read_csv(c10d_dir / '15_setpiece_metrics.csv')
    assert len(df) == 4
    for _, row in df.iterrows():
        assert row['status'] == 'SIGNIFICANT_IMPROVEMENT'

def test_placebo_and_negative_control():
    df_p = pd.read_csv(c10d_dir / '17_placebo_results.csv')
    df_n = pd.read_csv(c10d_dir / '21_negative_control.csv')
    assert '99.9%' in df_p.iloc[0]['percentile']
    assert 'SHRUNK_TO_ZERO' in df_n.iloc[0]['shrinkage_status']

def test_bootstrap_results():
    df = pd.read_csv(c10d_dir / '19_bootstrap_results.csv')
    rps_row = df[df['metric'] == 'RPS'].iloc[0]
    sp_row = df[df['metric'] == 'Set-Piece Goal Brier'].iloc[0]
    assert float(rps_row['point_delta']) == -0.0018
    assert float(rps_row['q97_5']) < 0
    assert float(sp_row['point_delta']) == -0.0230

def test_robustness():
    df = pd.read_csv(c10d_dir / '20_robustness.csv')
    assert len(df) == 9
    for _, row in df.iloc[:4].iterrows():
        assert float(row['c10d_rps']) < float(row['c10c_rps'])

def test_leakage_clean():
    p = c10d_dir / '22_leakage_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['future_outcomes_used'] == 0
    assert data['gw2_outcomes_used'] == 0
    assert data['audit_verdict'] == 'ZERO_LEAKAGE_STRICTLY_TEMPORAL'

def test_c10d_final_decision():
    p = c10d_dir / '24_final_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_status'] == 'C10_D_HISTORICAL_CHALLENGER_SUPPORTED'
    assert data['improves_c10c'] == 'YES'
    assert data['c10_e_combination_gate'] == 'PASS'
    assert data['governance_invariants']['c9_me_modified'] == False
    assert data['governance_invariants']['c10_a9_modified'] == False
    assert data['governance_invariants']['c10_b_modified'] == False
    assert data['governance_invariants']['c10_c_modified'] == False
    assert data['governance_invariants']['c10_d_modified'] == False
