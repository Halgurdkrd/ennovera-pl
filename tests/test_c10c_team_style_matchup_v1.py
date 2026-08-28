"""Automated Test Suite for C10-C Team Style and Matchup Interaction Research V1.
Asserts exact baseline reproductions, quality vs style separation, pretest freeze,
C10-C9 superior performance (60.33% acc, 0.1688 RPS, Goals MAE 0.805, 99.80% bootstrap support),
placebo falsification pass, zero leakage, and clean decision gate.
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
c10c_dir = reports_dir / 'dry_run' / 'c10c_matchup'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_baseline_reproductions():
    p = c10c_dir / '01_baseline_reproduction.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['c9']['correct'] == 900
    assert data['c9']['rps'] == 0.1730
    assert data['c10_a9']['correct'] == 906
    assert data['c10_a9']['rps'] == 0.1718
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

def test_c10b_bootstrap_supersession_record():
    p = c10c_dir / '02_c10b_bootstrap_supersession_record.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert '99.75%' in data['c10b_vs_c9']['favorable_draws']
    assert '99.35%' in data['c10b_vs_c10a9']['favorable_draws']
    assert 'FAVOR_PERCENTAGE_FROM_DIFFERENT_DISTRIBUTION' in data['superseded_draft_values']['supersession_classification']

def test_style_data_inventory():
    df = pd.read_csv(c10c_dir / '03_style_data_inventory.csv')
    assert len(df) == 10
    assert (df['usable'] == 'FULL_UNIVERSE_USABLE').all()
    assert (df['synthetic'] == 0).all()

def test_quality_vs_style_separation():
    df = pd.read_csv(c10c_dir / '04_quality_style_classification.csv')
    assert (df['final_classification'] == 'STYLE').all()
    mixed = df[df['raw_classification'] == 'MIXED']
    assert (mixed['residualized'] == True).all()

def test_game_state_and_stability():
    df_g = pd.read_csv(c10c_dir / '05_game_state_adjustment.csv')
    df_s = pd.read_csv(c10c_dir / '06_style_stability.csv')
    assert (df_g['status'] == 'GAME_STATE_ADJUSTED_PREFERRED').all()
    assert len(df_s) >= 8

def test_matchup_registry_and_pretest_freeze():
    df_m = pd.read_csv(c10c_dir / '08_matchup_registry.csv')
    p_spec = c10c_dir / '10_pretest_specification.json'
    assert len(df_m) >= 8
    assert p_spec.exists()
    data = json.loads(p_spec.read_text(encoding='utf-8'))
    assert data['status'] == 'FROZEN_BEFORE_TEST_EVALUATION'

def test_challenger_results_c10c9():
    df = pd.read_csv(c10c_dir / '11_challenger_results.csv')
    c10c9 = df[df['model'].str.contains('C10-C9')].iloc[0]
    assert float(c10c9['acc']) == 0.6033
    assert int(c10c9['correct_picks']) == 917
    assert float(c10c9['rps']) == 0.1688
    assert float(c10c9['log_loss']) == 0.8492
    assert float(c10c9['goals_mae']) == 0.805

def test_goal_environment_improvements():
    df = pd.read_csv(c10c_dir / '12_goal_environment_results.csv')
    assert len(df) == 5
    for _, row in df.iterrows():
        assert row['status'] == 'SIGNIFICANT_IMPROVEMENT'

def test_placebo_and_negative_control():
    df_p = pd.read_csv(c10c_dir / '14_placebo_results.csv')
    df_n = pd.read_csv(c10c_dir / '15_negative_control_results.csv')
    real_p = df_p[df_p['experiment'].str.contains('Real')].iloc[0]
    assert '99.9%' in real_p['percentile']
    assert 'SHRUNK_TO_ZERO' in df_n.iloc[0]['shrinkage_status']

def test_bootstrap_results():
    df = pd.read_csv(c10c_dir / '18_bootstrap_results.csv')
    rps_row = df[df['metric'] == 'RPS'].iloc[0]
    ll_row = df[df['metric'] == 'Log Loss'].iloc[0]
    gmae_row = df[df['metric'] == 'Goals MAE'].iloc[0]
    assert float(rps_row['point_delta']) == -0.0018
    assert float(rps_row['q97_5']) < 0
    assert float(ll_row['point_delta']) == -0.0060
    assert float(gmae_row['point_delta']) == -0.0230

def test_season_robustness():
    df = pd.read_csv(c10c_dir / '17_season_robustness.csv')
    assert len(df) == 5
    for _, row in df.iloc[:4].iterrows():
        assert float(row['c10c_rps']) < float(row['c10b_rps'])

def test_leakage_clean():
    p = c10c_dir / '20_leakage_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['future_data_used'] == 0
    assert data['gw2_outcomes_used'] == 0
    assert data['audit_verdict'] == 'ZERO_LEAKAGE_STRICTLY_TEMPORAL'

def test_c10c_final_decision():
    p = c10c_dir / '24_final_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['final_status'] == 'C10_C_HISTORICAL_CHALLENGER_SUPPORTED'
    assert data['improves_c10b'] == 'YES'
    assert data['c10_d_recommended'] == 'YES'
    assert data['governance_invariants']['c9_me_modified'] == False
    assert data['governance_invariants']['c10_a9_modified'] == False
    assert data['governance_invariants']['c10_b_modified'] == False
    assert data['governance_invariants']['gw2_prospective_snapshot_modified'] == False
