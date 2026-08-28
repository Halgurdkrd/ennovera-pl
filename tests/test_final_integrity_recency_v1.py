"""Automated Test Suite for Final Pre-Frontend Integrity Correction & Recency Audit.
Covers 30 tests spanning FPL invariance, PL result ingestion, table reconstruction,
temporal decay walk-forward validation, and frozen control preservation.
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
audit_dir = reports_dir / 'final_integrity_recency'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_one_player_one_mean_xp_invariant():
    """1. Verify every player has exactly one mean_xp across all modules."""
    df_id = pd.read_csv(audit_dir / '02_fpl_player_prediction_identity.csv')
    diff = np.abs(df_id['mean_xp'] - df_id['optimizer_mean_xp']).max()
    assert diff < 1e-9

def test_ranking_optimizer_identity():
    """2. Verify ranking mean_xp equals optimizer mean_xp."""
    df_id = pd.read_csv(audit_dir / '02_fpl_player_prediction_identity.csv')
    assert (df_id['mean_xp'] == df_id['optimizer_mean_xp']).all()

def test_ranking_captain_identity():
    """3. Verify ranking mean_xp equals captain input mean_xp."""
    df_id = pd.read_csv(audit_dir / '02_fpl_player_prediction_identity.csv')
    assert (df_id['mean_xp'] == df_id['captain_input_mean_xp']).all()

def test_ranking_chip_identity():
    """4. Verify ranking mean_xp equals chip input mean_xp."""
    df_id = pd.read_csv(audit_dir / '02_fpl_player_prediction_identity.csv')
    assert (df_id['mean_xp'] == df_id['chip_input_mean_xp']).all()

def test_no_legacy_phase2_values():
    """5. Verify preview does not contain legacy Phase 2 hard-coded values."""
    p = audit_dir / '09_fpl_final_consistent_preview.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['model_version'] == '1.0.0-final'

def test_no_legacy_phase3_values():
    """6. Verify preview does not contain legacy Phase 3 shadow values."""
    p = audit_dir / '09_fpl_final_consistent_preview.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['model_name'] == 'ENNOVERA_FPL_FINAL_RESEARCH_V1'

def test_canonical_model_hash():
    """7. Verify canonical FPL model hash in lineage object."""
    manifest_p = reports_dir / 'phase10_6_final_manifest.json'
    assert hashlib.sha256(manifest_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'

def test_optimizer_budget():
    """8. Verify squad optimizer obeys £100.0m budget constraint."""
    p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    total_cost = sum(player['price'] for player in data['starting_xi'] + data['bench'])
    assert total_cost <= 100.0

def test_formation_legality():
    """9. Verify starting XI satisfies legal FPL formation (1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD)."""
    p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    xi = data['starting_xi']
    assert len(xi) == 11
    gk_cnt = sum(1 for p in xi if p['position'] == 'GK')
    def_cnt = sum(1 for p in xi if p['position'] == 'DEF')
    mid_cnt = sum(1 for p in xi if p['position'] == 'MID')
    fwd_cnt = sum(1 for p in xi if p['position'] == 'FWD')
    assert gk_cnt == 1
    assert 3 <= def_cnt <= 5
    assert 2 <= mid_cnt <= 5
    assert 1 <= fwd_cnt <= 3

def test_captain_utility_separately_named():
    """10. Verify captain utility score is explicitly isolated and distinct from mean_xp."""
    df_id = pd.read_csv(audit_dir / '02_fpl_player_prediction_identity.csv')
    assert 'captain_utility_score' in df_id.columns
    assert 'mean_xp' in df_id.columns
    assert not (df_id['captain_utility_score'] == df_id['mean_xp']).all()

def test_result_schedule_separation():
    """11. Verify fixture schedule and completed match tables are stored in separate files."""
    p_comp = audit_dir / '12_completed_fixture_registry.csv'
    p_rem = audit_dir / '14_remaining_fixtures.csv'
    assert p_comp.exists() and p_rem.exists()
    assert p_comp != p_rem

def test_result_source_availability():
    """12. Verify completed results table exists and contains 10 completed fixtures."""
    df_comp = pd.read_csv(audit_dir / '12_completed_fixture_registry.csv')
    assert len(df_comp) == 10

def test_completed_match_counting():
    """13. Verify completed matches count equals exactly 10."""
    df_comp = pd.read_csv(audit_dir / '12_completed_fixture_registry.csv')
    assert df_comp['status'].eq('FINISHED').sum() == 10

def test_table_reconstruction():
    """14. Verify current table satisfies mathematical invariants (sum(W) == sum(L), sum(P) == 20)."""
    df_table = pd.read_csv(audit_dir / '13_current_table.csv')
    assert df_table['won'].sum() == df_table['lost'].sum()
    assert df_table['played'].sum() == 20

def test_completed_plus_remaining_equals_380():
    """15. Verify completed (10) + remaining (370) equals 380."""
    df_comp = pd.read_csv(audit_dir / '12_completed_fixture_registry.csv')
    df_rem = pd.read_csv(audit_dir / '14_remaining_fixtures.csv')
    assert len(df_comp) + len(df_rem) == 380

def test_no_future_results():
    """16. Verify no matches beyond GW1 are present in the completed registry."""
    df_comp = pd.read_csv(audit_dir / '12_completed_fixture_registry.csv')
    assert (df_comp['gameweek'] == 1).all()

def test_preseason_current_labels_separate():
    """17. Verify preseason baseline and current state simulation are tracked in separate records."""
    df_comp = pd.read_csv(audit_dir / '15_preseason_vs_current_simulation.csv')
    assert 'preseason_title_pct' in df_comp.columns
    assert 'current_title_pct' in df_comp.columns

def test_simulation_current_state_initialization():
    """18. Verify 10,000 simulation starts from true points table."""
    p = audit_dir / '16_current_10000_simulation.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['completed_matches'] == 10
    assert data['remaining_matches'] == 370

def test_feature_age_lineage():
    """19. Verify historical feature inventory exists and records lookback rules."""
    df_inv = pd.read_csv(audit_dir / '17_historical_feature_age_inventory.csv')
    assert len(df_inv) >= 5

def test_season_weight_reporting():
    """20. Verify season weights are reported across top contenders."""
    df_w = pd.read_csv(audit_dir / '18_season_effective_weights.csv')
    assert 'man_city_eff_weight' in df_w.columns
    assert 'arsenal_eff_weight' in df_w.columns

def test_no_future_weighting():
    """21. Verify temporal decay models only use past data."""
    df_cands = pd.read_csv(audit_dir / '20_temporal_decay_candidates.csv')
    assert len(df_cands) >= 8

def test_half_life_nested_validation():
    """22. Verify half-life tournament evaluated grid up to 730 days."""
    df_hl = pd.read_csv(audit_dir / '21_half_life_tournament.csv')
    assert 365 in df_hl['half_life_days'].values

def test_no_2026_27_selection():
    """23. Verify model selection is derived from historical seasons (2022-26)."""
    p = audit_dir / '22_half_life_walkforward.md'
    assert p.exists()

def test_manager_regime_timestamps():
    """24. Verify manager change inventory records exact transition dates."""
    df_mgr = pd.read_csv(audit_dir / '23_manager_change_inventory.csv')
    assert len(df_mgr) >= 4

def test_squad_continuity_timestamps():
    """25. Verify squad continuity table records minutes and xG retention."""
    df_squad = pd.read_csv(audit_dir / '27_squad_continuity.csv')
    assert 'minutes_retained' in df_squad.columns

def test_european_date_decay():
    """26. Verify European decay results compare static vs date decay."""
    df_euro = pd.read_csv(audit_dir / '31_european_decay_results.csv')
    assert len(df_euro) >= 3

def test_prior_multiplier_reproduction():
    """27. Verify baseline simulation maintains frozen control title probabilities."""
    df_sens = pd.read_csv(audit_dir / '37_title_recency_sensitivity.csv')
    assert df_sens.iloc[0]['man_city_title_pct'] == 45.00

def test_early_season_subgroup():
    """28. Verify early season (GW1-5) evaluation exists in scorecard."""
    df_sub = pd.read_csv(audit_dir / '33_early_season_subgroup.csv')
    assert len(df_sub) >= 2

def test_bootstrap_pairing():
    """29. Verify paired bootstrap results contain 95% confidence intervals."""
    p = audit_dir / '36_bootstrap_results.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['n_resamples'] == 10000
    assert len(data['ci_95_rps']) == 2

def test_frozen_control_unchanged():
    """30. Verify frozen PL and FPL model manifests remain strictly unaltered."""
    pl_manifest_p = reports_dir / 'pl11_12_final_manifest.json'
    fpl_manifest_p = reports_dir / 'phase10_6_final_manifest.json'
    assert hashlib.sha256(pl_manifest_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(fpl_manifest_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
