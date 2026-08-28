"""Automated Test Suite for C10-B Explicit Midfield State Research V1.
Asserts C9 and C10-A9 reproductions, data inventory, duel/clean sheet audits, orthogonal latent states,
C9+MID_TOTAL superior performance (59.67% acc, 0.1716 RPS, 92.8% bootstrap support),
C10-A9+MID_TOTAL dual superior performance (59.93% acc, 0.1706 RPS, 90.5% bootstrap support), zero leakage, and governance lock.
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
c10b_dir = reports_dir / 'dry_run' / 'c10b_midfield'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_c9_and_c10a9_reproductions():
    p9 = c10b_dir / '01_c9_reproduction.json'
    p10 = c10b_dir / '02_c10a9_reproduction.json'
    assert p9.exists() and p10.exists()
    d9 = json.loads(p9.read_text(encoding='utf-8'))
    d10 = json.loads(p10.read_text(encoding='utf-8'))
    assert d9['metrics']['correct_picks'] == 900
    assert d9['metrics']['rps'] == 0.1730
    assert d10['metrics']['correct_picks'] == 906
    assert d10['metrics']['rps'] == 0.1718

def test_protected_baseline_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_data_inventory_and_coverage():
    df = pd.read_csv(c10b_dir / '03_midfield_data_inventory.csv')
    assert len(df) >= 10
    dims = df['dimension'].tolist()
    assert 'MID_CONTROL' in dims and 'MID_PROGRESSION' in dims and 'MID_DISRUPTION' in dims

def test_quality_vs_style_registry():
    df = pd.read_csv(c10b_dir / '05_quality_vs_style_registry.csv')
    assert len(df) == 5
    style_rows = df[df['classification'] == 'STYLE']
    assert len(style_rows) >= 2
    assert (style_rows['forward_to_c10c'] == True).all()

def test_duel_and_clean_sheet_audits():
    df_d = pd.read_csv(c10b_dir / '09_duel_analysis.csv')
    df_cs = pd.read_csv(c10b_dir / '10_clean_sheet_analysis.csv')
    raw_d = df_d[df_d['duel_category'].str.contains('Total Duels')].iloc[0]
    raw_cs = df_cs[df_cs['clean_sheet_metric'].str.contains('Raw Clean Sheet')].iloc[0]
    assert 'UNINFORMATIVE' in raw_d['verdict']
    assert 'NOT_A_MIDFIELD_FEATURE' in raw_cs['verdict']

def test_latent_definitions_and_correlations():
    p = c10b_dir / '13_midfield_latent_definitions.json'
    assert p.exists()
    df_c = pd.read_csv(c10b_dir / '14_feature_correlations.csv')
    atk_row = df_c[df_c['feature_pair'].str.contains('Attack')].iloc[0]
    form_row = df_c[df_c['feature_pair'].str.contains('OAF5')].iloc[0]
    assert float(atk_row['pearson_r']) < 0.60
    assert float(form_row['pearson_r']) < 0.40

def test_primary_and_secondary_challenger_ladders():
    df = pd.read_csv(c10b_dir / '15_challenger_results.csv')
    assert len(df) == 10
    c9_mid = df[df['model'] == 'C9 + MID_TOTAL'].iloc[0]
    c10_mid = df[df['model'] == 'C10-A9 + MID_TOTAL'].iloc[0]
    assert float(c9_mid['acc']) == 0.5967
    assert float(c9_mid['rps']) == 0.1716
    assert float(c10_mid['acc']) == 0.5993
    assert float(c10_mid['rps']) == 0.1706

def test_bootstrap_results():
    df = pd.read_csv(c10b_dir / '16_bootstrap_results.csv')
    assert len(df) == 2
    row1 = df.iloc[0]
    row2 = df.iloc[1]
    assert '92.8%' in row1['bootstrap_favored_rps']
    assert '90.5%' in row2['bootstrap_favored_rps']

def test_season_and_team_robustness():
    df_s = pd.read_csv(c10b_dir / '17_season_robustness.csv')
    df_t = pd.read_csv(c10b_dir / '18_team_robustness.csv')
    assert len(df_s) == 4
    assert len(df_t) == 4
    for idx, row in df_s.iterrows():
        assert float(row['c10b_full_rps']) < float(row['c9_rps'])
    assert (df_t['status'].str.contains('PASS')).all()

def test_leakage_audit_clean():
    p = c10b_dir / '19_leakage_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['future_data_used'] == 0
    assert data['gw2_outcomes_used'] == 0
    assert data['audit_verdict'] == 'ZERO_LEAKAGE_STRICTLY_TEMPORAL'

def test_style_and_setpiece_registries():
    p_style = c10b_dir / '21_c10c_style_candidate_registry.csv'
    p_sp = c10b_dir / '22_c10d_setpiece_candidate_registry.csv'
    assert p_style.exists() and p_sp.exists()
    assert len(pd.read_csv(p_style)) >= 5
    assert len(pd.read_csv(p_sp)) >= 4

def test_c10b_final_decision():
    p = c10b_dir / '23_c10b_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['status'] == 'C10_B_HISTORICAL_CHALLENGER_SUPPORTED'
    assert data['governance_invariants']['c9_me_modified'] == False
    assert data['governance_invariants']['c10_a9_modified'] == False
    assert data['governance_invariants']['gw2_snapshot_modified'] == False
