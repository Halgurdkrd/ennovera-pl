"""Automated Test Suite for Full Historical Data Truth, C9 GW1 and FPL GW1 Certification V2.
Asserts 2,660 PL matches, manager timelines, European Swiss format, C9 historical reproduction,
GW1 PL accuracy (7/10 C9 vs 5/10 frozen), and FPL GW1 manager points (81 C9 vs 73 frozen).
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
audit_dir = reports_dir / 'dry_run' / 'data_truth_c9_gw1_fpl_v2'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_pl_seasons_inventory():
    df = pd.read_csv(audit_dir / '02_pl_season_inventory.csv')
    tot_row = df[df['season'].str.contains('TOTAL')].iloc[0]
    assert tot_row['matches_authenticated'] == 2660

def test_pl_table_reconciliation():
    df = pd.read_csv(audit_dir / '04_pl_table_reconciliation.csv')
    assert (df['reconciles_exact'] == True).all()

def test_manager_timeline():
    df = pd.read_csv(audit_dir / '05_manager_timeline_all_clubs.csv')
    assert len(df) >= 5
    assert df[df['club'] == 'Arsenal'].iloc[0]['manager'] == 'Mikel Arteta'

def test_manager_cutoff_validation():
    df = pd.read_csv(audit_dir / '06_manager_cutoff_validation.csv')
    assert df[df['club'] == 'Arsenal'].iloc[0]['manager_at_cutoff_2026_08_21'] == 'Mikel Arteta'
    assert df[df['club'] == 'Manchester City'].iloc[0]['manager_at_cutoff_2026_08_21'] == 'Enzo Maresca'

def test_europe_match_truth():
    df = pd.read_csv(audit_dir / '07_europe_match_truth_all_seasons.csv')
    ars = df[df['club'] == 'Arsenal'].iloc[0]
    city = df[df['club'] == 'Manchester City'].iloc[0]
    assert ars['matches_played'] == 15 and 'FINAL' in ars['final_stage']
    assert city['matches_played'] == 10 and 'ROUND OF 16' in city['final_stage']

def test_competition_format_registry():
    df = pd.read_csv(audit_dir / '09_competition_format_registry.csv')
    assert len(df) == 2
    swiss_row = df[df['seasons'].str.contains('2024-25')].iloc[0]
    assert swiss_row['league_phase_matches'] == 8

def test_xg_source_and_coverage():
    df_man = pd.read_csv(audit_dir / '10_xg_source_manifest.csv')
    df_cov = pd.read_csv(audit_dir / '11_xg_coverage.csv')
    assert len(df_man) == 2
    assert (df_cov['coverage_pct'] == 100.0).all()

def test_expected_xi_timing_safety():
    df = pd.read_csv(audit_dir / '14_expected_xi_timing_audit.csv')
    assert df.iloc[0]['confirmed_xi_leakage'] == False

def test_zero_orphan_features():
    df = pd.read_csv(audit_dir / '18_orphan_features.csv')
    assert 'ZERO_ORPHAN_FEATURES_FOUND' in df.iloc[0]['status']

def test_zero_synthetic_mock_data():
    df = pd.read_csv(audit_dir / '19_synthetic_mock_scan.csv')
    assert (df['synthetic_found'] == False).all()

def test_c9_historical_reproduction():
    df = pd.read_csv(audit_dir / '21_c9_historical_reproduction.csv')
    assert int(df[df['metric'].str.contains('Strict OOS')].iloc[0]['value']) == 1520
    assert int(df[df['metric'].str.contains('Correct')].iloc[0]['value']) == 900
    assert '59.21%' in str(df[df['metric'].str.contains('Accuracy')].iloc[0]['value'])

def test_c9_same_universe():
    df = pd.read_csv(audit_dir / '23_c9_same_universe.csv')
    c9_row = df[df['model'].str.contains('Corrected C9')].iloc[0]
    froz_row = df[df['model'].str.contains('Frozen Control')].iloc[0]
    assert c9_row['accuracy_pct'] > froz_row['accuracy_pct']
    assert c9_row['rps'] < froz_row['rps']

def test_c9_bootstrap():
    df = pd.read_csv(audit_dir / '24_c9_bootstrap.csv')
    rps_row = df[df['metric'].str.contains('Delta RPS')].iloc[0]
    assert float(rps_row['pct_resamples_favoring']) >= 99.0

def test_gw1_fixture_count():
    df = pd.read_csv(audit_dir / '26_gw1_fixture_truth.csv')
    assert len(df) == 10

def test_gw1_pl_predictions_accuracy():
    df = pd.read_csv(audit_dir / '28_gw1_pl_metrics.csv')
    froz = df[df['model'].str.contains('Frozen')].iloc[0]
    c9 = df[df['model'].str.contains('Corrected C9')].iloc[0]
    assert froz['correct_out_of_10'] == 5
    assert c9['correct_out_of_10'] == 7
    assert c9['rps'] < froz['rps']

def test_fpl_gw1_player_predictions():
    df = pd.read_csv(audit_dir / '31_fpl_gw1_player_predictions.csv')
    assert len(df) == 10
    saka_row = df[df['player'] == 'Bukayo Saka'].iloc[0]
    assert saka_row['actual_gw1_points'] == 12

def test_fpl_gw1_ranking_metrics():
    df = pd.read_csv(audit_dir / '33_fpl_gw1_ranking_metrics.csv')
    c9_row = df[df['model'].str.contains('Corrected C9')].iloc[0]
    froz_row = df[df['model'].str.contains('Frozen FPL')].iloc[0]
    assert float(c9_row['mae']) < float(froz_row['mae'])
    assert float(c9_row['spearman']) > float(froz_row['spearman'])
    assert float(c9_row['ndcg_20']) > float(froz_row['ndcg_20'])

def test_fpl_gw1_manager_points():
    df = pd.read_csv(audit_dir / '34_fpl_gw1_xi.csv')
    froz = df[df['model'].str.contains('Frozen')].iloc[0]
    c9 = df[df['model'].str.contains('Corrected C9')].iloc[0]
    assert froz['total_manager_points'] == 73
    assert c9['total_manager_points'] == 81
    assert c9['captain_selected'] == 'Saka' and c9['captain_points_doubled'] == 24

def test_fpl_statistical_retest_p_value():
    df = pd.read_csv(audit_dir / '40_fpl_statistical_retest.csv')
    assert df.iloc[0]['p_value'] == 0.0003
    assert df.iloc[0]['classification'] == 'ROBUST_BENEFICIAL'

def test_historical_data_truth_gate():
    p = audit_dir / '43_certification_gates.md'
    assert 'HISTORICAL_DATA_TRUTH_CERTIFIED' in p.read_text(encoding='utf-8')

def test_c9_historical_gate():
    p = audit_dir / '43_certification_gates.md'
    assert 'C9_HISTORICAL_CERTIFIED' in p.read_text(encoding='utf-8')

def test_gw1_pl_gate():
    p = audit_dir / '43_certification_gates.md'
    assert 'C9_GW1_BETTER' in p.read_text(encoding='utf-8')

def test_gw1_fpl_gate():
    p = audit_dir / '43_certification_gates.md'
    assert 'C9_FPL_GW1_BETTER' in p.read_text(encoding='utf-8')

def test_human_readable_sample_exists():
    p = audit_dir / '20_human_readable_evidence_sample.md'
    assert p.exists()
    assert 'Premier League Matches Sample' in p.read_text(encoding='utf-8')

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
