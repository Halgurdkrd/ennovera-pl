"""Automated Test Suite for C10-E GW1 + GW2 Retrospective Replay V1.
Asserts authenticated fixture registries (10/10 for GW1 and GW2),
preseason and post-GW1 title simulations (100k runs),
C10-E PL match predictions, FPL squad optimization, captaincy selections,
data integrity (0 leakage, 0 synthetic), and strict governance.
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
replay_dir = reports_dir / 'dry_run' / 'c10e_gw1_gw2_replay'
live_gw2_dir = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_protected_hashes():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = live_gw2_dir / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_c10e_model_and_bridge_identity():
    p_m = replay_dir / '01_model_identity.json'
    p_b = replay_dir / '02_fpl_bridge_identity.json'
    assert p_m.exists() and p_b.exists()
    d_m = json.loads(p_m.read_text(encoding='utf-8'))
    d_b = json.loads(p_b.read_text(encoding='utf-8'))
    assert 'C10-E' in d_m['model_name']
    assert d_m['metrics_1520_strict_oos']['rps'] == 0.1670
    assert float(d_b['historical_mean_manager_pts']) == 2234.50

def test_gw1_gw2_fixture_registries():
    df1 = pd.read_csv(replay_dir / '04_gw1_fixture_registry.csv')
    df2 = pd.read_csv(replay_dir / '13_gw2_fixture_registry.csv')
    assert len(df1) == 10 and len(df2) == 10
    assert (df1['status'] == 'AUTHENTICATED').all()
    assert (df2['status'] == 'AUTHENTICATED').all()

def test_gw1_gw2_pl_predictions():
    df1 = pd.read_csv(replay_dir / '06_gw1_pl_predictions.csv')
    df2 = pd.read_csv(replay_dir / '16_gw2_pl_predictions.csv')
    assert len(df1) == 10 and len(df2) == 10
    for df in [df1, df2]:
        for _, row in df.iterrows():
            prob_sum = float(row['p_home']) + float(row['p_draw']) + float(row['p_away'])
            assert abs(prob_sum - 1.0) < 0.005

def test_title_simulations():
    df1 = pd.read_csv(replay_dir / '07_gw1_title_simulation.csv')
    df2 = pd.read_csv(replay_dir / '17_gw2_title_simulation.csv')
    assert len(df1) == 20 and len(df2) == 10
    ars1 = df1[df1['team'] == 'Arsenal'].iloc[0]
    ars2 = df2[df2['team'] == 'Arsenal'].iloc[0]
    assert '42.6%' in ars1['title_pct']
    assert '44.1%' in ars2['pre_gw2_title']

def test_gw1_gw2_fpl_decisions():
    df_squad = pd.read_csv(replay_dir / '09_gw1_fpl_squad.csv')
    df_cap1 = pd.read_csv(replay_dir / '11_gw1_captain_ranking.csv')
    df_gw2_squad = pd.read_csv(replay_dir / '20_gw2_fpl_realistic_path.csv')
    df_cap2 = pd.read_csv(replay_dir / '22_gw2_captain_ranking.csv')
    assert len(df_squad) == 15 and len(df_gw2_squad) == 15
    assert df_cap1.iloc[0]['player'] == 'Haaland' and df_cap1.iloc[0]['selection'] == 'CAPTAIN'
    assert df_cap2.iloc[0]['player'] == 'Haaland' and df_cap2.iloc[1]['player'] == 'Salah'

def test_data_integrity():
    p = replay_dir / '24_data_integrity.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['gw1_outcome_leakage_into_gw1'] == 0
    assert data['gw2_outcome_leakage_into_gw2'] == 0
    assert data['synthetic_data'] == 0
    assert data['status'] == 'DATA_INTEGRITY_PRISTINE'
