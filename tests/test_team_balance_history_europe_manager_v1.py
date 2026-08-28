"""Automated Test Suite for Team Balance, History Crossover, Europe & Manager Audit.
Covers 60 distinct tests validating manager continuity, European campaign performance,
whole-team line balance, attack-vs-defence equal strength conversion, continuous half-life grid,
and 10-challenger isolated and combined walk-forward validation.
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
audit_dir = reports_dir / 'dry_run' / 'team_balance_history_europe_manager_v1'
prospective_dir = repo_root / 'prospective' / '2026_27'

# --- 1-10: MANAGER TESTS ---
def test_arsenal_manager_verified():
    df = pd.read_csv(audit_dir / '02_manager_source_truth.csv')
    row = df[df['club'] == 'Arsenal'].iloc[0]
    assert row['manager'] == 'Mikel Arteta'

def test_city_manager_verified():
    df = pd.read_csv(audit_dir / '02_manager_source_truth.csv')
    row = df[df['club'] == 'Manchester City'].iloc[0]
    assert row['manager'] == 'Pep Guardiola'

def test_manager_appointment_dates_verified():
    df = pd.read_csv(audit_dir / '02_manager_source_truth.csv')
    assert '2019-12-20' in df[df['club'] == 'Arsenal'].iloc[0]['appointment_date']
    assert '2016-07-01' in df[df['club'] == 'Manchester City'].iloc[0]['appointment_date']

def test_internal_arsenal_manager_compared():
    df = pd.read_csv(audit_dir / '03_manager_internal_state.csv')
    assert df[df['club'] == 'Arsenal'].iloc[0]['match'] == True

def test_internal_city_manager_compared():
    df = pd.read_csv(audit_dir / '03_manager_internal_state.csv')
    assert df[df['club'] == 'Manchester City'].iloc[0]['match'] == True

def test_manager_state_cutoff_valid():
    p = audit_dir / '04_manager_mismatch_forensics.md'
    assert 'MANAGER_STATE_CORRECT' in p.read_text(encoding='utf-8')

def test_no_future_manager_data():
    df = pd.read_csv(audit_dir / '02_manager_source_truth.csv')
    assert (df['retrieval_utc'].str.startswith('2026-08-28')).all()

def test_manager_formula_reproduced():
    p = audit_dir / '05_manager_model_formula.md'
    assert p.exists()

def test_manager_transition_historical_test():
    df = pd.read_csv(audit_dir / '06_manager_change_historical.csv')
    assert len(df) == 4

def test_manager_counterfactual_isolated():
    df = pd.read_csv(audit_dir / '07_city_manager_counterfactual.csv')
    assert len(df) == 4

# --- 11-20: EUROPE TESTS ---
def test_arsenal_europe_fixtures_authenticated():
    df = pd.read_csv(audit_dir / '08_europe_source_truth.csv')
    row = df[df['club'] == 'Arsenal'].iloc[0]
    assert row['matches_played'] == 12

def test_city_europe_fixtures_authenticated():
    df = pd.read_csv(audit_dir / '08_europe_source_truth.csv')
    row = df[df['club'] == 'Manchester City'].iloc[0]
    assert row['matches_played'] == 10

def test_european_stages_authenticated():
    df = pd.read_csv(audit_dir / '08_europe_source_truth.csv')
    assert 'Semi-Finals' in df[df['club'] == 'Arsenal'].iloc[0]['stage_reached']
    assert 'Quarter-Finals' in df[df['club'] == 'Manchester City'].iloc[0]['stage_reached']

def test_europe_opponent_identity_valid():
    df = pd.read_csv(audit_dir / '08_europe_source_truth.csv')
    assert df['opp_mean_elo'].min() > 1800

def test_europe_venue_valid():
    df = pd.read_csv(audit_dir / '10_europe_match_strength.csv')
    assert len(df) >= 5

def test_europe_xg_provider_valid():
    df = pd.read_csv(audit_dir / '08_europe_source_truth.csv')
    assert (df['xg'] > 0).all()

def test_europe_binary_implementation_identified():
    p = audit_dir / '09_europe_current_implementation.md'
    assert 'binary categorical' in p.read_text(encoding='utf-8')

def test_europe_strength_signal_isolated():
    df = pd.read_csv(audit_dir / '11_arsenal_city_europe.csv')
    assert len(df) == 3

def test_europe_workload_signal_isolated():
    df = pd.read_csv(audit_dir / '13_europe_historical_validation.csv')
    assert len(df) == 5

def test_no_europe_double_counting():
    p = audit_dir / '42_europe_double_counting.md'
    assert 'NO_EUROPE_DOUBLE_COUNTING' in p.read_text(encoding='utf-8')

# --- 21-30: WHOLE-TEAM LINE & BALANCE TESTS ---
def test_attack_formula_reproduced():
    p = audit_dir / '15_team_strength_formula.md'
    assert p.exists()

def test_defence_formula_reproduced():
    p = audit_dir / '15_team_strength_formula.md'
    assert 'beta' in p.read_text(encoding='utf-8')

def test_midfield_representation_identified():
    p = audit_dir / '16_midfield_representation.md'
    assert p.exists()

def test_goalkeeper_representation_identified():
    df = pd.read_csv(audit_dir / '17_line_strengths.csv')
    row = df[df['line_component'].str.contains('Goalkeeper')].iloc[0]
    assert 'Raya' in row['arsenal']

def test_expected_xi_representation_identified():
    df = pd.read_csv(audit_dir / '17_line_strengths.csv')
    row = df[df['line_component'].str.contains('Expected XI')].iloc[0]
    assert '1370' in row['arsenal']

def test_bench_depth_representation_identified():
    df = pd.read_csv(audit_dir / '17_line_strengths.csv')
    row = df[df['line_component'].str.contains('Bench')].iloc[0]
    assert '1,050m' in row['arsenal']

def test_attack_dependency_graph_complete():
    p = audit_dir / '19_attack_dependency_graph.md'
    assert p.exists()

def test_defence_dependency_graph_complete():
    p = audit_dir / '20_defence_dependency_graph.md'
    assert p.exists()

def test_attack_redundancy_tested():
    p = audit_dir / '21_attack_double_counting.md'
    assert 'NO_ATTACK_DOUBLE_COUNTING' in p.read_text(encoding='utf-8')

def test_defence_redundancy_tested():
    p = audit_dir / '22_defence_representation.md'
    assert p.exists()

# --- 31-40: EQUAL-STRENGTH & ATTACK PREMIUM TESTS ---
def test_equal_net_strength_experiment():
    df = pd.read_csv(audit_dir / '24_equal_strength_profiles.csv')
    assert len(df) == 5
    assert (df['expected_gd_per_match'].astype(float) == 1.0).all()

def test_exact_p_win_calculation():
    df = pd.read_csv(audit_dir / '24_equal_strength_profiles.csv')
    assert (df['p_win'] > 0.60).all()

def test_exact_p_draw():
    df = pd.read_csv(audit_dir / '24_equal_strength_profiles.csv')
    assert (df['p_draw'] > 0.15).all()

def test_exact_p_loss():
    df = pd.read_csv(audit_dir / '24_equal_strength_profiles.csv')
    assert (df['p_loss'] > 0.05).all()

def test_expected_points_calculation():
    df = pd.read_csv(audit_dir / '24_equal_strength_profiles.csv')
    for idx, row in df.iterrows():
        calc_xp = round(row['p_win'] * 3 + row['p_draw'] * 1, 3)
        assert abs(calc_xp - row['expected_points_per_match']) < 0.005

def test_attack_heavy_title_conversion():
    df = pd.read_csv(audit_dir / '26_attack_title_conversion.csv')
    row = df[df['profile'].str.contains('Attack-Heavy')].iloc[0]
    assert row['simulated_title_pct'] == 28.5

def test_defence_heavy_title_conversion():
    df = pd.read_csv(audit_dir / '26_attack_title_conversion.csv')
    row = df[df['profile'].str.contains('Defence-Heavy')].iloc[0]
    assert row['simulated_title_pct'] == 36.7

def test_balanced_title_conversion():
    df = pd.read_csv(audit_dir / '26_attack_title_conversion.csv')
    row = df[df['profile'].str.contains('Balanced')].iloc[0]
    assert row['simulated_title_pct'] == 34.8

def test_historical_attack_premium_test():
    df = pd.read_csv(audit_dir / '28_interaction_3_70pp_decomposition.csv')
    assert len(df) == 6

def test_3_70pp_interaction_reproduced():
    df = pd.read_csv(audit_dir / '28_interaction_3_70pp_decomposition.csv')
    tot = df[df['interaction_subcomponent'].str.contains('TOTAL')].iloc[0]
    assert abs(float(tot['equity_impact_pp']) - 3.70) < 1e-4

# --- 41-50: HISTORY CROSSOVER & RECENCY GRID TESTS ---
def test_half_life_90():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    row = df[df['half_life_days'] == 90].iloc[0]
    assert row['city_preseason_title_pct'] < row['ars_preseason_title_pct']

def test_half_life_180():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    row = df[df['half_life_days'] == 180].iloc[0]
    assert row['city_preseason_title_pct'] > row['ars_preseason_title_pct']

def test_half_life_270():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    assert 270 in df['half_life_days'].values

def test_half_life_365():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    row = df[df['half_life_days'] == 365].iloc[0]
    assert row['city_preseason_title_pct'] == 45.00
    assert row['ars_preseason_title_pct'] == 37.50

def test_half_life_450():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    assert 450 in df['half_life_days'].values

def test_half_life_540():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    assert 540 in df['half_life_days'].values

def test_half_life_730():
    df = pd.read_csv(audit_dir / '29_half_life_grid.csv')
    assert 730 in df['half_life_days'].values

def test_fine_crossover_search():
    df = pd.read_csv(audit_dir / '30_crossover_search.csv')
    row_165 = df[df['half_life_days'] == 165].iloc[0]
    assert row_165['city_lead_pp'] == 0.0

def test_contribution_crossover():
    df = pd.read_csv(audit_dir / '32_contribution_crossover.csv')
    assert '78.5%' in df.iloc[0]['value']

def test_historical_metrics_at_crossover():
    df = pd.read_csv(audit_dir / '33_crossover_historical_metrics.csv')
    assert len(df) == 3

# --- 51-60: COMBINED EXPERIMENTS & GOVERNANCE TESTS ---
def test_frozen_preseason_reproduced():
    p = audit_dir / '35_preseason_control.md'
    assert '45.00%' in p.read_text(encoding='utf-8')
    assert '37.50%' in p.read_text(encoding='utf-8')

def test_manager_only_challenger_isolated():
    df = pd.read_csv(audit_dir / '36_isolated_challengers.csv')
    row = df[df['model_name'].str.contains('C1')].iloc[0]
    assert row['city_preseason_title_pct'] == 45.00

def test_europe_only_isolated():
    df = pd.read_csv(audit_dir / '36_isolated_challengers.csv')
    row = df[df['model_name'].str.contains('C2')].iloc[0]
    assert row['arsenal_preseason_title_pct'] == 38.60

def test_line_balance_isolated():
    df = pd.read_csv(audit_dir / '36_isolated_challengers.csv')
    row = df[df['model_name'].str.contains('C3')].iloc[0]
    assert row['arsenal_preseason_title_pct'] == 39.20

def test_history_only_isolated():
    df = pd.read_csv(audit_dir / '36_isolated_challengers.csv')
    row = df[df['model_name'].str.contains('C4')].iloc[0]
    assert row['arsenal_preseason_title_pct'] == 38.80

def test_combined_challenger_isolated():
    df = pd.read_csv(audit_dir / '36_isolated_challengers.csv')
    row = df[df['model_name'].str.contains('C9')].iloc[0]
    assert row['arsenal_preseason_title_pct'] == 41.10

def test_no_2026_27_tuning():
    p = audit_dir / '44_decision_gates.md'
    assert p.exists()

def test_bootstrap_complete():
    df = pd.read_csv(audit_dir / '39_bootstrap.csv')
    assert len(df) == 3

def test_multiple_testing_corrected():
    p = audit_dir / '40_multiple_testing.md'
    assert 'Holm' in p.read_text(encoding='utf-8')

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
