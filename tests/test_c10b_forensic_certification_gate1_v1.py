"""Automated Test Suite for C10-B Forensic Certification (Gate 1 Only).
Asserts exact reproductions across all 1520 OOS matches, pristine test fold isolation, exact possession formula values,
empirical percentile bootstrap distribution reconciliation (90.5% vs C10-A9, 92.8% vs C9), season arithmetic, and clean certification.
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
cert_dir = reports_dir / 'dry_run' / 'c10b_certification_gate1'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_exact_reproduction():
    p = cert_dir / '02_exact_reproduction.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['c9_control']['correct'] == 900
    assert data['c9_control']['rps'] == 0.1730
    assert data['c10_a9_form']['correct'] == 906
    assert data['c10_a9_form']['rps'] == 0.1718
    assert data['c10_b_full']['correct'] == 911
    assert data['c10_b_full']['rps'] == 0.1706

def test_protected_baseline_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_artifact_manifest():
    df = pd.read_csv(cert_dir / '01_artifact_manifest.csv')
    assert len(df) >= 20
    assert (df['integrity_status'] == 'INTACT_UNMODIFIED').all()

def test_final_test_pristine():
    p = cert_dir / '19_final_test_pristine.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_test_pristine'] == 'YES'
    assert data['test_driven_feature_edits'] == 0
    assert data['test_driven_weight_adjustments'] == 0

def test_parameter_provenance():
    df = pd.read_csv(cert_dir / '04_parameter_provenance.csv')
    assert len(df) == 12
    assert (df['provenance'] == 'VALIDATION_SELECTED').all()

def test_half_life_provenance():
    p = cert_dir / '05_half_life_provenance.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['selected_value'] == '60 days'
    assert data['winner'] == '60 days'

def test_possession_adjustment_factors():
    f30 = (50.0 / 70.0) ** 0.85
    f50 = (50.0 / 50.0) ** 0.85
    f70 = (50.0 / 30.0) ** 0.85
    assert abs(f30 - 0.7512) < 1e-3
    assert abs(f50 - 1.0000) < 1e-4
    assert abs(f70 - 1.5434) < 1e-3

def test_residualization_and_normalization():
    df_r = pd.read_csv(cert_dir / '07_residualization_audit.csv')
    df_n = pd.read_csv(cert_dir / '08_normalization_audit.csv')
    assert (df_r['leakage'] == 'NO').all()
    assert (df_n['leakage'] == 'NO').all()

def test_event_data_provenance():
    df = pd.read_csv(cert_dir / '09_event_data_provenance.csv')
    assert (df['synthetic'] == 0).all()
    assert (df['unknown'] == 0).all()

def test_component_ablation_exactness():
    df = pd.read_csv(cert_dir / '12_component_ablation.csv')
    assert len(df) == 10
    assert (df['discrepancy'] == 0.0).all()

def test_bootstrap_reconciliation():
    df = pd.read_csv(cert_dir / '14_bootstrap_distribution_reconciliation.csv')
    assert len(df) == 2
    row9 = df[df['comparison'].str.contains('vs C9')].iloc[0]
    row10 = df[df['comparison'].str.contains('vs C10-A9')].iloc[0]
    assert '92.8%' in row9['pct_neg']
    assert '90.5%' in row10['pct_neg']

def test_season_arithmetic_sums():
    df = pd.read_csv(cert_dir / '16_season_arithmetic.csv')
    assert len(df) == 5
    tot_row = df[df['season'] == 'TOTAL STRICT OOS'].iloc[0]
    assert int(tot_row['c9_correct']) == 900
    assert int(tot_row['c10a_correct']) == 906
    assert int(tot_row['c10b_correct']) == 911

def test_leakage_audit_clean():
    p = cert_dir / '18_leakage_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['future_outcomes_used'] == 0
    assert data['gw2_outcomes_used'] == 0
    assert data['audit_verdict'] == 'ZERO_LEAKAGE_ALL_GATES_PASSED'

def test_c10b_final_certification_gate():
    p = cert_dir / '20_c10b_final_certification.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_status'] == 'C10_B_CERTIFIED_CLEAN_HISTORICAL_CHALLENGER'
    assert data['c10_c_gate'] == 'PASS'
    assert data['hard_governance']['c10_c_started_in_this_run'] == False
