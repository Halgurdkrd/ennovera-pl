"""Automated Test Suite for C9 Authenticated Manager and European Correction.
Asserts ground-truth manifest records, Enzo Maresca appointment, Arsenal UCL Final run,
City R16 exit vs Real Madrid, and recomputed C9 shadow title probabilities.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

reports_dir = repo_root / 'reports'
audit_dir = reports_dir / 'dry_run' / 'c9_authenticated_correction_v1'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_manifest_exists_and_valid():
    p = audit_dir / '01_source_truth_manifest.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert len(data['records']) == 4

def test_arsenal_manager_is_arteta():
    df = pd.read_csv(audit_dir / '02_manager_verified.csv')
    row = df[df['club'] == 'Arsenal'].iloc[0]
    assert row['manager'] == 'Mikel Arteta'
    assert 'Continuity' in row['regime_type']

def test_city_manager_is_maresca():
    df = pd.read_csv(audit_dir / '02_manager_verified.csv')
    row = df[df['club'] == 'Manchester City'].iloc[0]
    assert row['manager'] == 'Enzo Maresca'
    assert 'Transition' in row['regime_type']

def test_city_appointment_date():
    df = pd.read_csv(audit_dir / '02_manager_verified.csv')
    row = df[df['club'] == 'Manchester City'].iloc[0]
    assert '2026-06-29' in row['appointment_date']

def test_manager_transition_effect():
    df = pd.read_csv(audit_dir / '04_manager_transition_effect.csv')
    row_net = df[df['dimension'] == 'Net Manager Contribution'].iloc[0]
    assert row_net['authenticated_maresca_state'] == '-0.0100'

def test_arsenal_ucl_is_final():
    p = audit_dir / '01_source_truth_manifest.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    rec = next(r for r in data['records'] if r['entity'] == 'Arsenal FC' and 'Champions League' in r['field'])
    assert 'FINAL' in rec['final_stage']
    assert 'Paris Saint-Germain' in rec['final_opponent']

def test_arsenal_ucl_matches_count():
    df = pd.read_csv(audit_dir / '05_uefa_verified_arsenal.csv')
    assert len(df) == 15
    assert 'FINAL' in df.iloc[-1]['stage']

def test_city_ucl_is_r16():
    p = audit_dir / '01_source_truth_manifest.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    rec = next(r for r in data['records'] if r['entity'] == 'Manchester City FC' and 'Champions League' in r['field'])
    assert 'ROUND OF 16' in rec['final_stage']
    assert 'Real Madrid' in rec['elimination_opponent']

def test_city_ucl_matches_count():
    df = pd.read_csv(audit_dir / '06_uefa_verified_city.csv')
    assert len(df) == 10
    assert 'Real Madrid' in df.iloc[-1]['opponent']

def test_city_r16_aggregate_score():
    p = audit_dir / '01_source_truth_manifest.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    rec = next(r for r in data['records'] if r['entity'] == 'Manchester City FC' and 'Champions League' in r['field'])
    assert '5-1' in rec['elimination_aggregate']

def test_c9_old_reproduction():
    df = pd.read_csv(audit_dir / '11_c9_old_reproduction.csv')
    assert df.iloc[0]['city_title_pct'] == 42.40
    assert df.iloc[0]['arsenal_title_pct'] == 41.10

def test_c9_manager_corrected():
    df = pd.read_csv(audit_dir / '12_c9_manager_corrected.csv')
    assert df.iloc[0]['arsenal_title_pct'] == 41.80
    assert df.iloc[0]['city_title_pct'] == 39.60

def test_c9_europe_corrected():
    df = pd.read_csv(audit_dir / '13_c9_europe_corrected.csv')
    assert df.iloc[0]['arsenal_title_pct'] == 42.05
    assert df.iloc[0]['city_title_pct'] == 41.75

def test_c9_fully_corrected():
    df = pd.read_csv(audit_dir / '14_c9_fully_corrected.csv')
    row = df[df['model'].str.contains('Fully Corrected')].iloc[0]
    assert row['arsenal_title_pct'] == 42.80
    assert row['city_title_pct'] == 38.95
    assert 'Arsenal +3.85 pp' in row['leader']

def test_c9_attribution_reconciles():
    df = pd.read_csv(audit_dir / '15_c9_attribution.csv')
    assert len(df) == 5
    assert 'Arsenal +3.85 pp' in df.iloc[-1]['direction']

def test_historical_validation_c9():
    df = pd.read_csv(audit_dir / '16_historical_validation.csv')
    row_corr = df[df['model'].str.contains('Corrected')].iloc[0]
    assert row_corr['rps'] == 0.1730
    assert row_corr['accuracy_pct'] == 59.2

def test_bootstrap_results():
    df = pd.read_csv(audit_dir / '17_bootstrap.csv')
    assert df.iloc[0]['resamples_favoring_pct'] > 99.0

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
