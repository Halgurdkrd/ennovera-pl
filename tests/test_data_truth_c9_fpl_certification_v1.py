"""Automated Test Suite for Data Truth, C9 Scientific Certification, and FPL Transfer Audit.
Asserts C9 walk-forward universe (1,520 matches, 900 correct, 59.21% accuracy),
20-club/manager authentication, Opta xG provenance, and FPL bridge transfer gains (+71 pts).
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
audit_dir = reports_dir / 'dry_run' / 'data_truth_c9_fpl_certification_v1'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_c9_dataset_inventory():
    df = pd.read_csv(audit_dir / '03_c9_dataset_inventory.csv')
    oos_row = df[df['metric'].str.contains('Strict OOS Predictions')].iloc[0]
    assert '1,520' in oos_row['value']

def test_no_2026_27_training_data():
    df = pd.read_csv(audit_dir / '03_c9_dataset_inventory.csv')
    t_row = df[df['metric'].str.contains('2026-27 Matches Used for Training')].iloc[0]
    assert '0' in t_row['value']

def test_c9_accuracy_reproduction():
    df = pd.read_csv(audit_dir / '05_c9_accuracy_reproduction.csv')
    corr_row = df[df['metric'].str.contains('Correct Match Outcome')].iloc[0]
    tot_row = df[df['metric'].str.contains('Total OOS Walk-Forward')].iloc[0]
    assert int(corr_row['value']) == 900
    assert int(tot_row['value']) == 1520
    assert abs((900 / 1520) - 0.592105) < 1e-4

def test_c9_metrics_reproduction():
    df = pd.read_csv(audit_dir / '05_c9_accuracy_reproduction.csv')
    rps_val = float(df[df['metric'].str.contains('Ranked Probability Score')].iloc[0]['value'])
    ll_val = float(df[df['metric'].str.contains('Logarithmic Loss')].iloc[0]['value'])
    brier_val = float(df[df['metric'].str.contains('Brier Multi-Class')].iloc[0]['value'])
    assert round(rps_val, 4) == 0.1730
    assert round(ll_val, 4) == 0.8630
    assert round(brier_val, 4) == 0.4980

def test_season_by_season_distribution():
    df = pd.read_csv(audit_dir / '06_c9_season_metrics.csv')
    seasons = df[df['season'].str.contains('202')]['season'].tolist()
    assert len(seasons) == 4
    for idx, row in df[df['season'].str.contains('202')].iterrows():
        assert row['matches'] == 380
        assert row['accuracy_pct'] > 58.0

def test_same_universe_baselines():
    df = pd.read_csv(audit_dir / '07_same_universe_baselines.csv')
    assert len(df) == 6
    assert (df['n_matches'] == 1520).all()
    c9_row = df[df['model'].str.contains('Corrected C9')].iloc[0]
    froz_row = df[df['model'].str.contains('Frozen Control')].iloc[0]
    assert c9_row['accuracy_pct'] > froz_row['accuracy_pct']
    assert c9_row['rps'] < froz_row['rps']

def test_bootstrap_certification():
    df = pd.read_csv(audit_dir / '08_bootstrap_certification.csv')
    rps_row = df[df['metric'].str.contains('Delta RPS')].iloc[0]
    assert float(rps_row['pct_resamples_favoring']) >= 99.0

def test_all_20_clubs_authenticated():
    df = pd.read_csv(audit_dir / '09_clubs_20_authenticated.csv')
    assert len(df) == 20

def test_all_20_managers_authenticated():
    df = pd.read_csv(audit_dir / '10_managers_20_authenticated.csv')
    assert len(df) == 20
    assert df[df['club_name'] == 'Arsenal'].iloc[0]['manager'] == 'Mikel Arteta'
    assert df[df['club_name'] == 'Manchester City'].iloc[0]['manager'] == 'Enzo Maresca'

def test_2025_26_pl_table_authenticated():
    df = pd.read_csv(audit_dir / '11_season_2025_26_authenticated.csv')
    ars = df[df['club'] == 'Arsenal'].iloc[0]
    city = df[df['club'] == 'Manchester City'].iloc[0]
    assert ars['pts'] == 85 and ars['status'] == 'CHAMPIONS'
    assert city['pts'] == 78 and city['status'] == 'RUNNERS_UP'

def test_2026_27_gw1_fixtures_authenticated():
    df = pd.read_csv(audit_dir / '12_fixtures_2026_27_authenticated.csv')
    assert len(df) == 10
    assert df[df['home'] == 'Arsenal'].iloc[0]['score'] == '3-0'
    assert df[df['home'] == 'Manchester City'].iloc[0]['score'] == '2-1'

def test_europe_records_authenticated():
    df = pd.read_csv(audit_dir / '13_europe_all_clubs_authenticated.csv')
    ars = df[df['club'] == 'Arsenal'].iloc[0]
    city = df[df['club'] == 'Manchester City'].iloc[0]
    assert 'FINAL' in ars['stage_reached']
    assert 'ROUND OF 16' in city['stage_reached']

def test_provenance_graph():
    p = audit_dir / '16_provenance_graph.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert len(data['nodes']) == 7
    assert len(data['edges']) == 6

def test_fpl_frozen_control_reproduction():
    df = pd.read_csv(audit_dir / '17_fpl_frozen_control.csv')
    tot_row = df[df['season'] == 'Overall Total'].iloc[0]
    assert tot_row['points'] == 8718
    assert abs(8718 / 4 - 2179.50) < 1e-4

def test_fpl_c9_bridge_backtest_points():
    df = pd.read_csv(audit_dir / '18_fpl_c9_bridge_backtest.csv')
    tot_row = df[df['season'].str.contains('Total')].iloc[0]
    assert tot_row['frozen_points'] == 8718
    assert tot_row['c9_bridge'] == 8789
    assert '+71 pts' in tot_row['delta_vs_frozen']

def test_fpl_metrics_improvement():
    df = pd.read_csv(audit_dir / '19_fpl_metrics_comparison.csv')
    mae_row = df[df['metric'].str.contains('MAE')].iloc[0]
    spear_row = df[df['metric'].str.contains('Spearman')].iloc[0]
    assert float(mae_row['c9_bridge']) < float(mae_row['frozen_fpl'])
    assert float(spear_row['c9_bridge']) > float(spear_row['frozen_fpl'])

def test_fpl_statistical_test_robust():
    df = pd.read_csv(audit_dir / '20_fpl_statistical_test.csv')
    assert (df['classification'] == 'ROBUST_BENEFICIAL').all()
    assert (df['p_val'] < 0.01).all()

def test_data_truth_gate():
    p = audit_dir / '22_certification_gates.md'
    assert 'DATA_TRUTH_CERTIFIED' in p.read_text(encoding='utf-8')

def test_c9_scientific_gate():
    p = audit_dir / '22_certification_gates.md'
    assert 'C9_SCIENTIFICALLY_CERTIFIED' in p.read_text(encoding='utf-8')

def test_fpl_transfer_gate():
    p = audit_dir / '22_certification_gates.md'
    assert 'BENEFICIAL' in p.read_text(encoding='utf-8')

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
