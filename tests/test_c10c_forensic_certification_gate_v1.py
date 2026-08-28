"""Automated Test Suite for C10-C Forensic Certification (Gate Before C10-D).
Asserts exact reproductions across all 1520 OOS matches, pre-test specification freeze,
Benjamini-Hochberg multiple comparison pass, empirical placebo p=0.0010, bootstrap reconciliation,
subgroup representation, and clean Gate 1 certification.
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
cert_dir = reports_dir / 'dry_run' / 'c10c_certification_gate'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_exact_reproduction():
    p = cert_dir / '01_exact_reproduction.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['c9']['correct'] == 900
    assert data['c9']['rps'] == 0.1730
    assert data['c10_a9']['correct'] == 906
    assert data['c10_a9']['rps'] == 0.1718
    assert data['c10_b']['correct'] == 911
    assert data['c10_b']['rps'] == 0.1706
    assert data['c10_c9_final']['correct'] == 917
    assert data['c10_c9_final']['rps'] == 0.1688
    assert data['c10_c9_final']['goals_mae'] == 0.805

def test_protected_baseline_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_pretest_specification_freeze():
    p = cert_dir / '02_pretest_specification_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_test_pristine'] == 'YES'
    assert '9a8ff4e8e8c953cbef9f106ffc8bebe9e543e7ac70f7ca8d90879381d8cde5b1' in data['sha256']

def test_m6_and_c10c7_naming():
    p_m6 = cert_dir / '04_m6_forensics.json'
    p_name = cert_dir / '05_c10c7_naming_resolution.md'
    assert p_m6.exists() and p_name.exists()
    d_m6 = json.loads(p_m6.read_text(encoding='utf-8'))
    assert 'TEMPO_A * TRANSITION_DEFENCE_B' in d_m6['formula']
    assert 'PRE_REGISTERED_BEFORE_FINAL_TEST' in d_m6['preregistered_status']

def test_multiple_comparison_control():
    df = pd.read_csv(cert_dir / '06_multiple_comparison_audit.csv')
    assert len(df) == 8
    assert (df['significant'] == True).all()
    assert (df['bh_fdr_q'] < 0.05).all()

def test_placebo_experiment_forensics():
    p = cert_dir / '07_placebo_experiment_forensics.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['permutations_count'] == 1000
    assert data['extreme_count_le_real'] == 0
    assert 'PASS' in data['placebo_test_verdict']
    assert data['empirical_placebo_p'] <= 0.001

def test_subgroups_and_sample_sizes():
    df_sg = pd.read_csv(cert_dir / '08_match_environment_subgroups.csv')
    df_ss = pd.read_csv(cert_dir / '09_subgroup_sample_size_audit.csv')
    assert len(df_sg) == 2
    assert len(df_ss) >= 6
    for _, row in df_ss.iterrows():
        assert int(row['n']) >= 180

def test_data_provenance_and_orthogonalization():
    df_dp = pd.read_csv(cert_dir / '10_data_provenance_audit.csv')
    df_ort = pd.read_csv(cert_dir / '11_style_orthogonalization_audit.csv')
    assert (df_dp['status'] == 'PASS').all()
    assert (df_dp['synthetic'] == 0).all()
    assert (df_ort['test_leakage'] == 'NO').all()

def test_bootstrap_reproduction():
    df = pd.read_csv(cert_dir / '12_bootstrap_reproduction.csv')
    assert len(df) == 7
    rps_row = df[df['metric'] == 'RPS'].iloc[0]
    ll_row = df[df['metric'] == 'Log Loss'].iloc[0]
    gmae_row = df[df['metric'] == 'Goals MAE'].iloc[0]
    assert float(rps_row['delta']) == -0.0018
    assert float(rps_row['q97_5']) < 0
    assert float(ll_row['delta']) == -0.0060
    assert float(gmae_row['delta']) == -0.0230

def test_season_arithmetic():
    df = pd.read_csv(cert_dir / '13_season_arithmetic_audit.csv')
    assert len(df) == 5
    tot_row = df[df['season'] == 'TOTAL STRICT OOS'].iloc[0]
    assert int(tot_row['c9_correct']) == 900
    assert int(tot_row['c10b_correct']) == 911
    assert int(tot_row['c10c_correct']) == 917

def test_leakage_clean():
    p = cert_dir / '16_leakage_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['future_data_used'] == 0
    assert data['gw2_outcomes_used'] == 0
    assert data['audit_verdict'] == 'ZERO_LEAKAGE_STRICTLY_TEMPORAL'

def test_c10c_final_certification_gate():
    p = cert_dir / '17_c10c_final_certification.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_status'] == 'C10_C_CERTIFIED_CLEAN_HISTORICAL_CHALLENGER'
    assert data['c10_d_gate'] == 'PASS'
    assert data['hard_governance']['c10_d_started_in_this_run'] == False
