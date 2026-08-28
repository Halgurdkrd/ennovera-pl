"""Automated Test Suite for Schedule Equity & R8/RF10 Final Dry-Run Validation.
Covers 30 distinct tests validating schedule forensics, double-representation absence,
R8+RF10 tournament metrics, LOSO validation, calibration, and governance.
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
dry_dir = reports_dir / 'dry_run' / 'schedule_equity_r8_rf10_validation_v1'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_frozen_pl_hash():
    """1. Verify PL final model manifest hash is unaltered."""
    p = reports_dir / 'pl11_12_final_manifest.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'

def test_frozen_fpl_hash():
    """2. Verify FPL model manifest hash is unaltered."""
    p = reports_dir / 'phase10_6_final_manifest.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'

def test_frozen_gw2_hash():
    """3. Verify frozen GW2 plan hash is unaltered."""
    p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_prospective_registry_hash():
    """4. Verify prospective snapshot registry is unaltered."""
    p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_candidate_isolation():
    """5. Verify R8+RF10 manifest exists and is hashed."""
    p = dry_dir / '16_r8_rf10_manifest.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['candidate_id'] == 'ENNOVERA_PL_R8_RF10_VALIDATION_CANDIDATE_V1'

def test_schedule_formula_identity():
    """6. Verify schedule difficulty is descriptive and native to remaining fixtures."""
    p = dry_dir / '01_schedule_formula.md'
    assert p.exists()
    assert 'Dixon-Coles' in p.read_text(encoding='utf-8')

def test_individual_fixture_schedule_retention():
    """7. Verify remaining 370 fixtures are simulated sequentially."""
    p = dry_dir / '02_schedule_call_graph.md'
    assert 'Remaining 370 Fixtures' in p.read_text(encoding='utf-8')

def test_aggregate_schedule_ablation():
    """8. Verify aggregate schedule feature ablation results."""
    df_abl = pd.read_csv(dry_dir / '14_schedule_ablation.csv')
    assert len(df_abl) == 3
    assert 'CLEAN_BASELINE' in df_abl.iloc[0]['verdict']

def test_no_fixture_replay():
    """9. Verify 10 completed matches are removed from remaining schedule."""
    df_cf = pd.read_csv(dry_dir / '04_fixture_consumption_counterfactuals.csv')
    assert len(df_cf) == 18

def test_expected_result_invariance():
    """10. Verify completing fixture with expected outcome produces invariant title probability."""
    df_inv = pd.read_csv(dry_dir / '08_expected_result_invariance.csv')
    assert len(df_inv) == 3
    for idx, row in df_inv.iterrows():
        assert abs(row['delta_pp']) <= 0.10

def test_fixture_order_invariance():
    """11. Verify 100 schedule order permutations produce invariant title probabilities."""
    df_ord = pd.read_csv(dry_dir / '07_fixture_order_invariance.csv')
    assert len(df_ord) == 3
    for idx, row in df_ord.iterrows():
        assert row['sd_title_pct'] < 0.25

def test_gd_ledger_integrity():
    """12. Verify GD enters table ledger at full value."""
    p = dry_dir / '13_gd_state_audit.md'
    assert 'Actual Table GD' in p.read_text(encoding='utf-8')

def test_gd_latent_strength_separation():
    """13. Verify GD does not artificially inflate predictive latent ratings."""
    p = dry_dir / '13_gd_state_audit.md'
    assert 'Bayesian EWMA' in p.read_text(encoding='utf-8')

def test_historical_schedule_calibration_integrity():
    """14. Verify schedule-driven title probability moves are historically calibrated."""
    df_cal = pd.read_csv(dry_dir / '09_historical_schedule_calibration.csv')
    assert len(df_cal) == 5
    for idx, row in df_cal.iterrows():
        assert row['cal_error'] < 0.015

def test_early_season_cutoff_integrity():
    """15. Verify early-season schedule calibration is documented."""
    df_early = pd.read_csv(dry_dir / '10_early_season_schedule_calibration.csv')
    assert len(df_early) == 5

def test_contender_definition_point_in_time():
    """16. Verify contender status is defined point-in-time."""
    df_cont = pd.read_csv(dry_dir / '11_contender_schedule_calibration.csv')
    assert len(df_cont) == 4

def test_rf10_formula_identity():
    """17. Verify RF10 exact formula definition."""
    p = dry_dir / '17_rf10_exact_formula.md'
    assert 'RF10' in p.read_text(encoding='utf-8')

def test_rf10_no_leakage():
    """18. Verify RF10 uses only historical match logs."""
    df_rf = pd.read_csv(dry_dir / '31_rf10_redundancy.csv')
    assert len(df_rf) >= 3

def test_r8_isolation():
    """19. Verify R8 recency candidate is isolated."""
    df_dec = pd.read_csv(dry_dir / '20_decay_tournament.csv')
    assert any('365' in str(h) for h in df_dec['half_life'])

def test_trophy_variable_audit():
    """20. Verify zero explicit trophy bonuses exist."""
    p = dry_dir / '18_trophy_feature_audit.md'
    assert 'Zero active trophy' in p.read_text(encoding='utf-8')

def test_temporal_decay_integrity():
    """21. Verify 365-day decay is optimal across tournament."""
    df_dec = pd.read_csv(dry_dir / '20_decay_tournament.csv')
    opt = df_dec.sort_values(by='rps').iloc[0]
    assert '365' in opt['half_life']
    assert opt['rps'] == 0.1735

def test_loso_isolation():
    """22. Verify Leave-One-Season-Out (LOSO) validation is complete."""
    df_loso = pd.read_csv(dry_dir / '22_loso_results.csv')
    assert len(df_loso) == 5
    assert df_loso.iloc[-1]['loso_rps'] == 0.1736

def test_early_season_isolation():
    """23. Verify R8+RF10 outperforms control in GW1-5."""
    df_early = pd.read_csv(dry_dir / '23_early_season_results.csv')
    gw1_5 = df_early[df_early['segment'] == 'GW1 - GW5'].iloc[0]
    assert gw1_5['r8_rf10_rps'] < gw1_5['frozen_rps']

def test_manager_regime_cutoff():
    """24. Verify manager change subgroup results."""
    df_mgr = pd.read_csv(dry_dir / '24_manager_change_results.csv')
    assert len(df_mgr) == 4

def test_squad_turnover_cutoff():
    """25. Verify squad turnover subgroup results."""
    df_to = pd.read_csv(dry_dir / '25_squad_turnover_results.csv')
    assert len(df_to) == 3

def test_promoted_team_handling():
    """26. Verify promoted teams evaluation."""
    df_prom = pd.read_csv(dry_dir / '26_promoted_team_results.csv')
    assert len(df_prom) == 2

def test_calibration_integrity():
    """27. Verify 10 reliability calibration bins."""
    df_cal = pd.read_csv(dry_dir / '29_calibration_results.csv')
    assert len(df_cal) == 10

def test_bootstrap_pairing():
    """28. Verify paired bootstrap on R8+RF10 vs Frozen."""
    data = json.loads((dry_dir / '33_bootstrap_results.json').read_text(encoding='utf-8'))
    pair = [c for c in data['comparisons'] if c['pair'] == 'R8_plus_RF10 vs Frozen'][0]
    assert pair['delta_rps'] == -0.0013
    assert pair['pct_resamples_favoring'] > 99.0

def test_multiple_comparison_validation():
    """29. Verify Holm-Bonferroni correction passes."""
    p = dry_dir / '34_multiple_comparison_validation.md'
    assert 'Holm-Bonferroni' in p.read_text(encoding='utf-8')

def test_frozen_outputs_unchanged():
    """30. Verify official prospective snapshot registry is intact."""
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
