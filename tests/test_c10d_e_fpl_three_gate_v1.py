"""Automated Test Suite for Three-Gate Master Run:
Gate 1: C10-D Forensic Certification
Gate 2: C10-E Integration Freeze
Gate 3: C10-E -> FPL Historical Bridge

Program: ENNOVERA_C10D_E_FPL_THREE_GATE_V1
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
dry_gate1_dir = reports_dir / 'dry_run' / 'c10d_certification_gate2'
dry_gate2_dir = reports_dir / 'dry_run' / 'c10e_freeze'
dry_gate3_dir = reports_dir / 'dry_run' / 'c10e_fpl_bridge'

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

# --- GATE 1 TESTS ---
def test_gate1_c10d_certification():
    p = dry_gate1_dir / '01_c10d_certification_report.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['c10_c']['correct'] == 917
    assert data['c10_d9']['correct'] == 923
    assert data['c10_d9']['rps'] == 0.1670
    assert data['final_test_pristine'] == 'YES'
    assert data['d7_naming'] == 'BEST_VALIDATED_CORNER_AERIAL_FAMILY'
    assert data['bh_fdr_forensics']['all_q_lt_0_05'] == True
    assert data['bh_fdr_forensics']['total_hypotheses_in_family'] == 5
    assert data['data_provenance_synthetic_count'] == 0
    assert data['penalty_quarantine'] == 'VERIFIED_EXCLUDED'
    assert data['placebo_empirical_p'] == 0.0010
    assert data['gate_1_status'] == 'C10_D_CERTIFIED_CLEAN_HISTORICAL_CHALLENGER'
    assert data['gate_1_pass'] == True

# --- GATE 2 TESTS ---
def test_gate2_c10e_integration_freeze():
    p_spec = dry_gate2_dir / 'C10E_FINAL_INTEGRATED_MODEL_SPEC.json'
    p_preds = dry_gate2_dir / 'C10E_FINAL_PREDICTIONS.csv'
    p_hashes = dry_gate2_dir / '04_c10e_hashes.json'
    assert p_spec.exists() and p_preds.exists() and p_hashes.exists()
    spec = json.loads(p_spec.read_text(encoding='utf-8'))
    assert spec['prediction_byte_equivalent_to_d9'] == True
    assert spec['metrics_1520_strict_oos']['correct_picks'] == 923
    assert spec['metrics_1520_strict_oos']['rps'] == 0.1670
    assert spec['gate_2_status'] == 'C10_E_INTEGRATED_HISTORICAL_MODEL_FROZEN'

def test_gate2_module_attribution_and_ablation():
    df_attr = pd.read_csv(dry_gate2_dir / '02_module_attribution.csv')
    df_abl = pd.read_csv(dry_gate2_dir / '03_full_ablation.csv')
    assert len(df_attr) == 6
    assert len(df_abl) == 5
    tot_row = df_attr[df_attr['model'].str.contains('TOTAL')].iloc[0]
    assert '+23' in tot_row['delta_picks_vs_prev']
    assert '-0.0060' in tot_row['delta_rps_vs_prev']

# --- GATE 3 TESTS ---
def test_gate3_fpl_controls_and_ladder():
    df = pd.read_csv(dry_gate3_dir / '01_fpl_bridge_ladder.csv')
    assert len(df) == 6
    f0 = df[df['bridge_model'].str.contains('Frozen')].iloc[0]
    f1 = df[df['bridge_model'].str.contains('C9')].iloc[0]
    f5 = df[df['bridge_model'].str.contains('C10-E')].iloc[0]
    assert int(f0['total_points']) == 8718
    assert int(f1['total_points']) == 8789
    assert int(f5['total_points']) == 8938
    assert float(f5['points_per_season']) == 2234.50
    assert float(f5['mae']) == 1.424
    assert float(f5['spearman']) == 0.575

def test_gate3_fpl_point_attribution():
    df = pd.read_csv(dry_gate3_dir / '02_fpl_point_attribution.csv')
    assert len(df) == 7
    tot_frozen = df[df['increment'].str.contains('TOTAL C10-E vs Frozen')].iloc[0]
    tot_c9 = df[df['increment'].str.contains('TOTAL C10-E vs C9')].iloc[0]
    assert '+220 pts' in tot_frozen['total_points_added']
    assert '+149 pts' in tot_c9['total_points_added']

def test_gate3_position_effects():
    df = pd.read_csv(dry_gate3_dir / '03_position_effects.csv')
    assert len(df) == 4
    for _, row in df.iterrows():
        assert float(row['delta_mae']) < 0

def test_gate3_bootstrap_and_season_robustness():
    df_boot = pd.read_csv(dry_gate3_dir / '04_fpl_bootstrap_results.csv')
    df_seas = pd.read_csv(dry_gate3_dir / '05_season_robustness.csv')
    assert len(df_boot) == 3
    assert len(df_seas) == 5
    boot_f0 = df_boot[df_boot['comparison'].str.contains('Frozen')].iloc[0]
    assert '152 / 152' in boot_f0['favorable_gws']

def test_gate3_final_decision():
    p = dry_gate3_dir / '06_final_decision.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['gate_1_status'] == 'C10_D_CERTIFIED_CLEAN_HISTORICAL_CHALLENGER'
    assert data['gate_2_status'] == 'C10_E_INTEGRATED_HISTORICAL_MODEL_FROZEN'
    assert data['gate_3_status'] == 'C10E_FPL_BRIDGE_HISTORICALLY_SUPPORTED'
    assert data['governance_invariants']['c9_me_modified'] == False
    assert data['governance_invariants']['c10_e_deployed'] == False
    assert data['governance_invariants']['production_modified'] == False
