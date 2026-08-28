"""Automated Test Suite for C10-B Bootstrap Arithmetic Fix V1.
Asserts 100% mathematical consistency between empirical quantiles and favorable draw counts,
immutability of point estimates, and clean Gate 1 certification.
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
boot_dir = reports_dir / 'dry_run' / 'c10b_bootstrap_fix_v1'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_protected_baseline_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_root_cause_analysis():
    p = boot_dir / '01_root_cause_analysis.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    assert 'FAVOR_PERCENTAGE_FROM_DIFFERENT_DISTRIBUTION' in text

def test_point_estimates_unchanged():
    p = boot_dir / '06_point_estimates_immutability.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['point_estimates_unchanged'] == True
    assert data['c9_baseline']['correct'] == 900
    assert data['c10_a9']['correct'] == 906
    assert data['c10_b_full']['correct'] == 911

def test_c10b_vs_c9_reconciled():
    df = pd.read_csv(boot_dir / '03_c10b_vs_c9_bootstrap_reconciled.csv')
    assert len(df) == 4
    for _, row in df.iterrows():
        assert row['status'] == 'CONSISTENT'
    rps_row = df[df['metric'].str.contains('RPS')].iloc[0]
    assert float(rps_row['point_delta']) == -0.0014
    assert '1995 / 2000' in rps_row['count_favorable']
    assert '99.75%' in rps_row['pct_favorable']

def test_c10b_vs_c10a9_reconciled():
    df = pd.read_csv(boot_dir / '04_c10b_vs_c10a9_bootstrap_reconciled.csv')
    assert len(df) == 4
    for _, row in df.iterrows():
        assert row['status'] == 'CONSISTENT'
    rps_row = df[df['metric'].str.contains('RPS')].iloc[0]
    assert float(rps_row['point_delta']) == -0.0012
    assert '1987 / 2000' in rps_row['count_favorable']
    assert '99.35%' in rps_row['pct_favorable']

def test_mathematical_consistency_condition():
    df_all = pd.read_csv(boot_dir / '02_stored_draws_full_distribution.csv')
    assert len(df_all) == 8
    for _, row in df_all.iterrows():
        is_loss = 'Accuracy' not in row['metric']
        if is_loss:
            if float(row['q97_5']) < 0:
                assert float(row['pct_fav']) >= 97.5
        else:
            if float(row['q2_5']) > 0:
                assert float(row['pct_fav']) >= 97.5

def test_c10b_certified_decision():
    p = boot_dir / '07_c10b_final_certified_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['internal_consistency'] == 'PASS'
    assert data['c10_c_gate'] == 'PASS'
    assert data['hard_governance']['c10_c_started_in_this_run'] == False
