"""Automated Test Suite for C10 Research Roadmap and Form Challenger V1.
Asserts C9 baseline exact reproduction, complete research roadmap, data coverage, orthogonal OAF correlations,
C10-A9 superior performance (59.61% acc, 0.1718 RPS, 91.4% bootstrap support), zero leakage, and strict governance lock.
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
c10_dir = reports_dir / 'dry_run' / 'c10_research'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_c9_baseline_reproduction():
    p = c10_dir / '01_c9_baseline_reproduction.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['status'] == 'C9_BASELINE_EXACT_REPRODUCTION_VERIFIED'
    m = data['metrics']
    assert m['correct_picks'] == 900
    assert m['total_picks'] == 1520
    assert abs(m['accuracy'] - 0.592105) < 1e-4
    assert m['rps'] == 0.1730
    assert m['log_loss'] == 0.8630

def test_protected_baseline_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_feature_roadmap_structure():
    df = pd.read_csv(c10_dir / '02_feature_research_roadmap.csv')
    assert len(df) >= 5
    f_ids = df['FEATURE_ID'].tolist()
    assert 'F_C10A_01' in f_ids and 'F_C10B_01' in f_ids and 'F_C10C_01' in f_ids

def test_data_coverage_and_temporal_safety():
    df = pd.read_csv(c10_dir / '04_form_data_coverage.csv')
    assert len(df) == 7
    assert (df['cutoff_safe'] == 'YES').all()

def test_temporal_integrity_audit():
    df = pd.read_csv(c10_dir / '05_temporal_integrity_audit.csv')
    assert (df['violations_found'] == 0).all()
    assert (df['status'] == 'PASS').all()

def test_form_definitions():
    assert (c10_dir / '06_form5_definition.json').exists()
    assert (c10_dir / '07_form10_definition.json').exists()
    assert (c10_dir / '08_oaf5_definition.json').exists()
    assert (c10_dir / '09_oaf10_definition.json').exists()

def test_feature_correlations():
    df = pd.read_csv(c10_dir / '10_feature_correlations.csv')
    oaf5_row = df[df['feature_pair'].str.contains('OAF5')].iloc[0]
    assert float(oaf5_row['pearson_r']) < 0.50

def test_challenger_results_ladder():
    df = pd.read_csv(c10_dir / '11_challenger_results.csv')
    assert len(df) == 10
    c9_row = df[df['model'] == 'C9 (Control)'].iloc[0]
    c10_row = df[df['model'].str.contains('C10-A9')].iloc[0]
    assert float(c10_row['acc']) > float(c9_row['acc'])
    assert float(c10_row['rps']) < float(c9_row['rps'])
    assert float(c10_row['log_loss']) < float(c9_row['log_loss'])

def test_season_robustness():
    df = pd.read_csv(c10_dir / '12_season_robustness.csv')
    assert len(df) == 4
    for idx, row in df.iterrows():
        assert float(row['c10_rps']) < float(row['c9_rps'])
        assert float(row['c10_ll']) < float(row['c9_ll'])

def test_early_season_stability():
    df = pd.read_csv(c10_dir / '13_early_season_results.csv')
    assert len(df) == 4
    gw1_5 = df[df['window'] == 'GW1-GW5'].iloc[0]
    assert float(gw1_5['delta_rps']) <= 0.0

def test_calibration_ece():
    df = pd.read_csv(c10_dir / '15_calibration_analysis.csv')
    assert len(df) == 5
    assert (df['calibration'] == 'EXCELLENT').all()

def test_bootstrap_results():
    df = pd.read_csv(c10_dir / '16_bootstrap_results.csv')
    rps_row = df[df['metric'] == 'RPS'].iloc[0]
    assert '91.4%' in rps_row['bootstrap_favored_pct']

def test_leakage_audit_clean():
    p = c10_dir / '17_leakage_audit.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['future_outcomes_used'] == 0
    assert data['gw2_leakage'] == 0
    assert data['audit_verdict'] == 'ZERO_LEAKAGE_STRICTLY_TEMPORAL'

def test_example_explanations():
    p = c10_dir / '18_example_explanations.md'
    assert p.exists()
    content = p.read_text(encoding='utf-8')
    assert 'Example A' in content and 'Example D' in content

def test_final_decision_classification():
    p = c10_dir / '19_c10a_final_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['classification'] == 'C10_A_HISTORICAL_CHALLENGER_SUPPORTED'
    assert data['governance_status']['c9_me_modified'] == False
    assert data['governance_status']['gw2_prospective_snapshot_modified'] == False

def test_future_specs_exist():
    assert (c10_dir / '20_future_midfield_specification.md').exists()
    assert (c10_dir / '21_future_matchup_specification.md').exists()
    assert (c10_dir / '22_future_setpiece_specification.md').exists()
