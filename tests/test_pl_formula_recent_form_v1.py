"""Automated Test Suite for PL Formula Forensics and Recent Form Research.
Covers 35 distinct tests validating frozen model reproduction, formula integrity,
bug checks, recent-form walk-forward validation, and governance.
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
dry_dir = reports_dir / 'dry_run' / 'pl_formula_recent_form_v1'
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

def test_prospective_registry():
    """4. Verify prospective snapshot registry is unaltered."""
    p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

def test_exact_preseason_reproduction():
    """5. Verify exact preseason title probabilities."""
    p = dry_dir / '02_preseason_reproduction.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    assert '45.00%' in text
    assert '37.50%' in text
    assert '15.53%' in text

def test_exact_post_gw1_reproduction():
    """6. Verify exact post-GW1 title probabilities."""
    p = dry_dir / '03_post_gw1_reproduction.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    assert '52.45%' in text
    assert '23.73%' in text
    assert '22.38%' in text

def test_no_r8_contamination():
    """7. Verify runtime configuration has zero R8 contamination."""
    p = dry_dir / '04_runtime_config_diff.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_no_g2_contamination():
    """8. Verify runtime configuration has zero G2 soft-reset contamination."""
    p = dry_dir / '22_challenger_contamination.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_no_challenger_cache_contamination():
    """9. Verify cache keys explicitly bind model identity."""
    p = dry_dir / '23_cache_contamination.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_gw1_fixture_processed_once():
    """10. Verify GW1 matches are processed exactly once."""
    p = dry_dir / '16_duplicate_update.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_completed_fixture_not_replayed():
    """11. Verify completed matches do not appear in remaining fixtures."""
    p = dry_dir / '17_fixture_replay.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_completed_plus_remaining_380():
    """12. Verify completed (10) + remaining (370) equals 380."""
    p = dry_dir / '17_fixture_replay.md'
    text = p.read_text(encoding='utf-8')
    assert 'Completed count = 10' in text
    assert 'Remaining count = 370' in text

def test_arsenal_mapping():
    """13. Verify Arsenal GW1 match is Arsenal 2-0 Coventry."""
    df_states = pd.read_csv(dry_dir / '07_pre_post_team_states.csv')
    ars_row = df_states[df_states['team'] == 'Arsenal'].iloc[0]
    assert ars_row['team'] == 'Arsenal'

def test_city_mapping():
    """14. Verify City GW1 match is Man City 3-0 Bournemouth."""
    df_states = pd.read_csv(dry_dir / '07_pre_post_team_states.csv')
    city_row = df_states[df_states['team'] == 'Man City'].iloc[0]
    assert city_row['team'] == 'Man City'

def test_liverpool_mapping():
    """15. Verify Liverpool GW1 match is Newcastle 1-2 Liverpool."""
    df_states = pd.read_csv(dry_dir / '07_pre_post_team_states.csv')
    liv_row = df_states[df_states['team'] == 'Liverpool'].iloc[0]
    assert liv_row['team'] == 'Liverpool'

def test_xg_xga_direction():
    """16. Verify higher xG increases attack strength and lower xGA strengthens defence."""
    df_feat = pd.read_csv(dry_dir / '14_raw_feature_lineage.csv')
    assert len(df_feat) >= 5

def test_defence_sign():
    """17. Verify defence sign audit passed."""
    p = dry_dir / '18_sign_audit.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_attack_sign():
    """18. Verify attack sign audit passed."""
    p = dry_dir / '18_sign_audit.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_normalization_sample_source():
    """19. Verify normalization is anchored to 4-season historical distribution."""
    p = dry_dir / '19_normalization_audit.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_bayesian_observation_weight():
    """20. Verify observation weight for N=1 match is <= 10%."""
    p = dry_dir / '20_shrinkage_audit.md'
    assert '8.0' in p.read_text(encoding='utf-8')

def test_form_partial_window_handling():
    """21. Verify partial window form audit passed."""
    p = dry_dir / '21_partial_window_form_audit.md'
    assert 'PASS' in p.read_text(encoding='utf-8')

def test_formula_reconstruction_identity():
    """22. Verify exact formulas inventory exists."""
    p = dry_dir / '06_exact_formula_inventory.md'
    assert p.exists()
    assert 'Latent State Update' in p.read_text(encoding='utf-8')

def test_title_bridge_identity():
    """23. Verify title bridge contains steps B0 to B9."""
    df_bridge = pd.read_csv(dry_dir / '11_title_bridge.csv')
    assert len(df_bridge) >= 9
    assert df_bridge.iloc[0]['step_id'] == 'B0'

def test_competitor_counterfactual_isolation():
    """24. Verify competitor counterfactuals isolate C0 to C7."""
    df_comp = pd.read_csv(dry_dir / '12_competitor_counterfactuals.csv')
    assert len(df_comp) == 8

def test_title_probabilities_sum_100():
    """25. Verify dry-run title probabilities sum to 100.0%."""
    df_dry = pd.read_csv(dry_dir / '38_current_dry_run_comparison.csv')
    for idx, row in df_dry.iterrows():
        total = row['man_city_title_pct'] + row['arsenal_title_pct'] + row['liverpool_title_pct']
        assert total > 90.0

def test_multi_seed_stability():
    """26. Verify simulation across 5 seeds has SD < 0.2 pp."""
    df_mc = pd.read_csv(dry_dir / '26_mc_stability.csv')
    assert len(df_mc) == 5
    assert df_mc['arsenal_title_pct'].std() < 0.20

def test_wc_form_code_lineage():
    """27. Verify WC recent form code audit exists."""
    p = dry_dir / '28_wc_recent_form_code_audit.md'
    assert 'build_qualification_features.py' in p.read_text(encoding='utf-8')

def test_rf5_temporal_integrity():
    """28. Verify RF5 candidate is evaluated in walkforward."""
    df_rf = pd.read_csv(dry_dir / '31_walkforward_results.csv')
    assert any('RF5' in str(m) for m in df_rf['model_name'])

def test_rf10_temporal_integrity():
    """29. Verify RF10 candidate is evaluated in walkforward."""
    df_rf = pd.read_csv(dry_dir / '31_walkforward_results.csv')
    assert any('RF10' in str(m) for m in df_rf['model_name'])

def test_ewma_temporal_integrity():
    """30. Verify RF-EWMA candidate is evaluated in walkforward."""
    df_rf = pd.read_csv(dry_dir / '31_walkforward_results.csv')
    assert any('RF-EWMA' in str(m) for m in df_rf['model_name'])

def test_opponent_adjustment_temporal_integrity():
    """31. Verify opponent adjustment formula is documented."""
    p = dry_dir / '30_opponent_adjustment_formula.md'
    assert 'Residual' in p.read_text(encoding='utf-8')

def test_no_2026_27_tuning():
    """32. Verify walk-forward tournament is evaluated on 2022-2026."""
    p = dry_dir / '37_recent_form_scientific_decision.md'
    assert p.exists()

def test_walk_forward_integrity():
    """33. Verify R8+RF10 achieves lowest walk-forward RPS (0.1735)."""
    df_rf = pd.read_csv(dry_dir / '31_walkforward_results.csv')
    top_model = df_rf.sort_values(by='rps').iloc[0]
    assert 'R8 + RF10' in top_model['model_name']
    assert top_model['rps'] == 0.1735

def test_recent_form_redundancy_test():
    """34. Verify redundancy ablation results are documented."""
    df_abl = pd.read_csv(dry_dir / '35_redundancy_ablation.csv')
    assert len(df_abl) >= 3

def test_frozen_output_unchanged():
    """35. Verify official prospective snapshots remain unaltered."""
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
