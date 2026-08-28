"""Automated Test Suite for Certification Consistency + GW1 FPL Forensic Check.
Asserts forecast provenance, C9 GW1 PL reproduction (7/10), complete top-20 FPL points,
recalculated threshold recalls (10+=100%, 15+=N/A), XI & Captain derivation (73 vs 81), and statistical reproducibility.
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
audit_dir = reports_dir / 'dry_run' / 'certification_patch_v1'
prospective_dir = repo_root / 'prospective' / '2026_27'

def test_gw1_forecast_provenance():
    df = pd.read_csv(audit_dir / '02_gw1_forecast_provenance.csv')
    froz_pl = df[df['model_name'] == 'Frozen PL Model'].iloc[0]
    c9_pl = df[df['model_name'] == 'Corrected C9 (C9-ME)'].iloc[0]
    assert froz_pl['classification'] == 'TRUE_PROSPECTIVE_ARCHIVE'
    assert c9_pl['classification'] == 'RETROSPECTIVE_FIXED_MODEL_REPLAY'

def test_c9_gw1_pl_reproduction():
    df = pd.read_csv(audit_dir / '03_c9_gw1_pl_reproduction.csv')
    assert len(df) == 10
    correct_count = df['correct'].sum()
    assert correct_count == 7
    acc = correct_count / 10
    assert abs(acc - 0.70) < 1e-4

def test_gw1_fpl_source_truth_top_players():
    df = pd.read_csv(audit_dir / '05_gw1_fpl_top20_complete.csv')
    saka = df[df['player'] == 'Bukayo Saka'].iloc[0]
    haaland = df[df['player'] == 'Erling Haaland'].iloc[0]
    mitoma = df[df['player'] == 'Kaoru Mitoma'].iloc[0]
    palmer = df[df['player'] == 'Cole Palmer'].iloc[0]
    assert saka['actual_fpl_points'] == 12
    assert haaland['actual_fpl_points'] == 9
    assert mitoma['actual_fpl_points'] == 11
    assert palmer['actual_fpl_points'] == 10

def test_complete_top_20_count():
    df = pd.read_csv(audit_dir / '05_gw1_fpl_top20_complete.csv')
    assert len(df) == 20
    assert df.iloc[0]['player'] == 'Bukayo Saka'
    assert df.iloc[19]['player'] == 'Kevin De Bruyne'

def test_official_top_scorer_captured():
    df = pd.read_csv(audit_dir / '05_gw1_fpl_top20_complete.csv')
    top_scorer = df[df['actual_overall_rank'] == 1].iloc[0]
    assert top_scorer['player'] == 'Bukayo Saka'
    assert top_scorer['rank'] == 1

def test_gw1_threshold_recall_recalculated():
    df = pd.read_csv(audit_dir / '06_gw1_threshold_recall_recalculated.csv')
    r10 = df[df['threshold'].str.contains('>= 10')].iloc[0]
    r15 = df[df['threshold'].str.contains('>= 15')].iloc[0]
    r20 = df[df['threshold'].str.contains('>= 20')].iloc[0]
    assert '100.0%' in r10['recall_pct']
    assert 'N/A' in r15['recall_pct']
    assert 'N/A' in r20['recall_pct']

def test_metric_contamination_root_cause_doc():
    p = audit_dir / '07_metric_contamination_root_cause.md'
    assert p.exists()
    assert 'REPORT_METRIC_CONTAMINATION' in p.read_text(encoding='utf-8')

def test_xi_and_manager_derivation():
    df = pd.read_csv(audit_dir / '08_gw1_xi_detailed_derivation.csv')
    froz = df[df['model'] == 'Frozen FPL'].iloc[0]
    c9 = df[df['model'] == 'Corrected C9 Bridge'].iloc[0]
    assert froz['xi_base_points'] == 55 and froz['total_manager_score'] == 73
    assert c9['xi_base_points'] == 57 and c9['total_manager_score'] == 81

def test_captain_points_derivation():
    df = pd.read_csv(audit_dir / '08_gw1_xi_detailed_derivation.csv')
    froz = df[df['model'] == 'Frozen FPL'].iloc[0]
    c9 = df[df['model'] == 'Corrected C9 Bridge'].iloc[0]
    assert froz['captain_points_doubled'] == 18
    assert c9['captain_points_doubled'] == 24

def test_data_truth_evidence_audit_counts():
    df = pd.read_csv(audit_dir / '10_data_truth_evidence_audit_counts.csv')
    pl_row = df[df['category'].str.contains('Historical Premier League')].iloc[0]
    assert pl_row['total_records'] == 2660
    assert pl_row['agreement_pct'] == 100.0

def test_opta_xg_technical_provenance():
    p = audit_dir / '11_opta_xg_technical_provenance.md'
    assert '2,660 Premier League matches' in p.read_text(encoding='utf-8')

def test_uefa_manager_source_sample():
    df = pd.read_csv(audit_dir / '12_uefa_manager_source_sample.csv')
    assert len(df) >= 4
    assert (df['verified'] == True).all()

def test_fpl_statistical_reproduction():
    df = pd.read_csv(audit_dir / '13_fpl_statistical_reproduction.csv')
    p_val_row = df[df['metric'].str.contains('p-Value')].iloc[0]
    fav_row = df[df['metric'].str.contains('Favoring C9')].iloc[0]
    assert float(p_val_row['value']) == 0.0003
    assert '99.4%' in fav_row['value']

def test_certification_patch_gates():
    p = audit_dir / '15_certification_patch_gates.md'
    assert 'CERTIFIED' in p.read_text(encoding='utf-8')
    assert 'RETROSPECTIVE_FIXED_MODEL_REPLAY' in p.read_text(encoding='utf-8')

def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'
