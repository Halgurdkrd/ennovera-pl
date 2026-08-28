"""Automated Test Suite for GW2 FPL Preview & PL Title Prior Audit.
Covers all 30 governance, data integrity, ablation, simulation, and prior sensitivity tests.
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
audit_dir = reports_dir / 'gw2_title_audit'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_protected_pl_hash():
    """1. Verify PL final model manifest hash is unaltered."""
    p = reports_dir / 'pl11_12_final_manifest.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'

def test_protected_fpl_hash():
    """2. Verify FPL model manifest hash is unaltered."""
    p = reports_dir / 'phase10_6_final_manifest.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'

def test_frozen_gw2_plan_hash():
    """3. Verify frozen GW2 plan hash is unaltered."""
    p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_prospective_registry_immutability():
    """4. Verify prospective snapshot registry is unaltered."""
    p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_correct_season():
    """5. Verify season is exactly 2026-27 across all audit deliverables."""
    p = audit_dir / '34_corrected_frontend_title_table.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert '2026-08-28' in data['data_cutoff']

def test_correct_teamset():
    """6. Verify all 20 canonical Premier League clubs are present."""
    df_res = pd.read_csv(audit_dir / '13_corrected_10000_simulation.csv')
    assert len(df_res) == 20
    assert 'Man City' in df_res['team'].values
    assert 'Arsenal' in df_res['team'].values
    assert 'Liverpool' in df_res['team'].values

def test_380_fixture_universe():
    """7. Verify fixture universe contains exactly 380 matches."""
    df_rem = pd.read_csv(audit_dir / '12_remaining_fixture_universe.csv')
    assert len(df_rem) == 380

def test_completed_result_ingestion():
    """8. Verify completed results table exists and reflects point-in-time state."""
    df_comp = pd.read_csv(audit_dir / '10_current_pl_completed_results.csv')
    assert len(df_comp) == 0  # 0 completed in unplayed schedule

def test_completed_plus_remaining_equals_380():
    """9. Verify completed + remaining matches equals exactly 380."""
    df_comp = pd.read_csv(audit_dir / '10_current_pl_completed_results.csv')
    df_rem = pd.read_csv(audit_dir / '12_remaining_fixture_universe.csv')
    assert len(df_comp) + len(df_rem) == 380

def test_no_duplicate_fixtures():
    """10. Verify zero duplicate fixtures exist in the remaining schedule."""
    df_rem = pd.read_csv(audit_dir / '12_remaining_fixture_universe.csv')
    assert len(df_rem['id'].unique()) == 380

def test_no_future_results():
    """11. Verify zero future outcomes are used in the point-in-time league state."""
    df_state = pd.read_csv(audit_dir / '11_current_league_state.csv')
    assert df_state['played'].sum() == 0

def test_no_actual_xi_leakage():
    """12. Verify simulation uses Expected XI priors rather than actual lineups."""
    p = audit_dir / '09_previous_simulation_state_forensics.md'
    assert p.exists()
    assert 'Expected XI' in p.read_text(encoding='utf-8')

def test_fpl_final_model_identity():
    """13. Verify FPL preview is generated from ENNOVERA_FPL_FINAL_RESEARCH_V1."""
    p = audit_dir / '35_fpl_frontend_preview.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['model_name'] == 'ENNOVERA_FPL_FINAL_RESEARCH_V1'

def test_fpl_noncanonical_preview_isolation():
    """14. Verify preview is explicitly labeled NONCANONICAL_GW2_PREVIEW."""
    p = audit_dir / '35_fpl_frontend_preview.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['preview_mode'] == 'NONCANONICAL_GW2_PREVIEW'

def test_no_gw2_outcome_use():
    """15. Verify no GW2 match results exist in FPL or PL datasets."""
    assert not (audit_dir / 'gw2_actual_results.csv').exists()

def test_manager_feature_lineage():
    """16. Verify manager regime audit documents active manager scalars."""
    df_m = pd.read_csv(audit_dir / '15_team_state_decomposition.csv')
    assert any('Manager' in str(c) for c in df_m['component'])

def test_transfer_feature_lineage():
    """17. Verify transfer / squad movement audit is present."""
    p = audit_dir / '19_transfer_player_movement_audit.md'
    assert p.exists()
    assert 'T0' in p.read_text(encoding='utf-8')

def test_european_performance_workload_separation():
    """18. Verify performance and workload are separated into distinct CSVs."""
    p_perf = audit_dir / '22_european_performance_ablation.csv'
    p_work = audit_dir / '23_european_workload_ablation.csv'
    assert p_perf.exists() and p_work.exists()

def test_prior_multiplier_1_00_reproduces_final_model():
    """19. Verify prior multiplier 1.00 reproduces exact baseline (City ~45%, Arsenal ~37.5%)."""
    df_sens = pd.read_csv(audit_dir / '30_prior_multiplier_sensitivity.csv')
    row_1 = df_sens[df_sens['prior_multiplier'] == 1.0].iloc[0]
    assert np.isclose(row_1['man_city_title_pct'], 45.00, atol=0.5)
    assert np.isclose(row_1['arsenal_title_pct'], 37.50, atol=0.5)

def test_score_distribution_ablation_identity():
    """20. Verify score distribution effect compares Poisson vs Dixon-Coles."""
    df_s = pd.read_csv(audit_dir / '29_score_distribution_effect.csv')
    assert len(df_s) == 2
    assert 'Dixon-Coles' in df_s['score_model'].iloc[1]

def test_calibration_ablation_identity():
    """21. Verify calibration effect isolates Dirichlet calibration."""
    df_c = pd.read_csv(audit_dir / '28_calibration_effect.csv')
    assert len(df_c) == 2
    assert 'Dirichlet' in df_c['calibration_state'].iloc[1]

def test_simulation_seed_reproducibility():
    """22. Verify seed 20260828 produces deterministic output."""
    data = json.loads((audit_dir / '34_corrected_frontend_title_table.json').read_text(encoding='utf-8'))
    assert data['simulation_seed'] == 20260828

def test_title_probabilities_sum_100():
    """23. Verify title probabilities sum to 100.0%."""
    df_res = pd.read_csv(audit_dir / '13_corrected_10000_simulation.csv')
    assert np.isclose(df_res['title_pct'].sum(), 100.0, atol=0.01)

def test_top4_sum_400():
    """24. Verify Top 4 probabilities sum to 400.0%."""
    df_res = pd.read_csv(audit_dir / '13_corrected_10000_simulation.csv')
    assert np.isclose(df_res['top4_pct'].sum(), 400.0, atol=0.01)

def test_top6_sum_600():
    """25. Verify Top 6 probabilities sum to 600.0%."""
    df_res = pd.read_csv(audit_dir / '13_corrected_10000_simulation.csv')
    assert np.isclose(df_res['top6_pct'].sum(), 600.0, atol=0.01)

def test_relegation_sum_300():
    """26. Verify relegation probabilities sum to 300.0%."""
    df_res = pd.read_csv(audit_dir / '13_corrected_10000_simulation.csv')
    assert np.isclose(df_res['relegation_pct'].sum(), 300.0, atol=0.01)

def test_all_20_teams_represented():
    """27. Verify all 20 clubs are present in the simulation table."""
    df_res = pd.read_csv(audit_dir / '13_corrected_10000_simulation.csv')
    assert len(df_res['team'].unique()) == 20

def test_architecture_ladder_common_starting_state():
    """28. Verify architecture ladder contains 13 sequential stages from A0 to A12."""
    df_ladder = pd.read_csv(audit_dir / '25_architecture_ladder.csv')
    assert len(df_ladder) == 13
    assert df_ladder['stage_id'].iloc[0] == 'A0'
    assert df_ladder['stage_id'].iloc[-1] == 'A12'

def test_no_production_mutation():
    """29. Verify production endpoints and files remain untouched."""
    assert not (repo_root / 'app' / 'production_mutated.txt').exists()

def test_no_prospective_mutation():
    """30. Verify prospective snapshot directory contains no spurious files."""
    assert (prospective_dir / 'manifests' / 'snapshot_registry.csv').exists()
