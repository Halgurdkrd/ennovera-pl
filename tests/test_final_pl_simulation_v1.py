"""Automated Test Suite for Final PL 10,000-Run Season Simulation.
Verifies model integrity, simulation convergence, probability sanity constraints,
and report generation across all 20 Premier League clubs.
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
sim_dir = reports_dir / 'final_pl_simulation'

def test_frozen_pl_model_manifest_immutability():
    """1. Verify PL final model manifest hash is unaltered."""
    manifest_p = reports_dir / 'pl11_12_final_manifest.json'
    assert manifest_p.exists()
    h = hashlib.sha256(manifest_p.read_bytes()).hexdigest()
    assert h == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'

def test_frozen_fpl_model_manifest_immutability():
    """2. Verify FPL model manifest hash is unaltered."""
    manifest_p = reports_dir / 'phase10_6_final_manifest.json'
    assert manifest_p.exists()
    h = hashlib.sha256(manifest_p.read_bytes()).hexdigest()
    assert h == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'

def test_frozen_gw2_plan_immutability():
    """3. Verify GW2 plan has not been modified."""
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert gw2_p.exists()
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_prospective_registry_immutability():
    """4. Verify prospective registry is unaltered."""
    reg_p = repo_root / 'prospective' / '2026_27' / 'manifests' / 'snapshot_registry.csv'
    assert reg_p.exists()
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_simulation_deliverables_presence():
    """5. Verify all 10 required simulation deliverables exist."""
    required_files = [
        '00_pre_simulation_integrity.md',
        '01_current_league_state.csv',
        '02_remaining_fixture_probabilities.csv',
        '03_simulation_results_all_teams.csv',
        '04_title_race_summary.md',
        '05_position_distribution.csv',
        '06_old_vs_final_model_comparison.csv',
        '07_simulation_sanity_checks.md',
        '08_frontend_ready_table.json',
        '09_final_report.md'
    ]
    for fn in required_files:
        assert (sim_dir / fn).exists(), f"Missing deliverable {fn}"

def test_teamset_completeness_and_uniqueness():
    """6. Verify all 20 Premier League clubs are represented without duplicates."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    assert len(df_res) == 20
    assert len(df_res['team'].unique()) == 20

def test_title_probability_sum():
    """7. Verify sum of title probabilities equals exactly 100.0%."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    assert np.isclose(df_res['title_pct'].sum(), 100.0, atol=0.01)

def test_top4_probability_sum():
    """8. Verify sum of Top 4 probabilities equals exactly 400.0%."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    assert np.isclose(df_res['top4_pct'].sum(), 400.0, atol=0.01)

def test_top6_probability_sum():
    """9. Verify sum of Top 6 probabilities equals exactly 600.0%."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    assert np.isclose(df_res['top6_pct'].sum(), 600.0, atol=0.01)

def test_relegation_probability_sum():
    """10. Verify sum of relegation probabilities equals exactly 300.0%."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    assert np.isclose(df_res['relegation_pct'].sum(), 300.0, atol=0.01)

def test_man_city_championship_favorite():
    """11. Verify Manchester City is the #1 title favorite."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    top_team = df_res.iloc[0]
    assert top_team['team'] == 'Man City'
    assert top_team['title_pct'] > 40.0

def test_top_three_contenders_ordered():
    """12. Verify Top 3 title contenders are Man City, Arsenal, and Liverpool."""
    df_res = pd.read_csv(sim_dir / '03_simulation_results_all_teams.csv')
    top3 = df_res.iloc[:3]['team'].tolist()
    assert top3 == ['Man City', 'Arsenal', 'Liverpool']

def test_liverpool_corrected_from_old_model():
    """13. Verify Liverpool title probability is realistic (>10%) vs old model (1.9%)."""
    df_comp = pd.read_csv(sim_dir / '06_old_vs_final_model_comparison.csv')
    liv_row = df_comp[df_comp['team'] == 'Liverpool'].iloc[0]
    assert liv_row['final_title_pct'] > 10.0
    assert liv_row['delta'] > 10.0

def test_frontend_json_structure():
    """14. Verify frontend ready table JSON contains required schema."""
    json_data = json.loads((sim_dir / '08_frontend_ready_table.json').read_text(encoding='utf-8'))
    assert json_data['model_name'] == 'ENNOVERA_PL_FINAL_RESEARCH_V1'
    assert json_data['simulation_runs'] == 10000
    assert len(json_data['table']) == 20
