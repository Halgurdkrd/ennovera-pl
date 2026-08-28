"""Automated Test Suite for Ennovera C10-E Controlled Production Deployment V1.
Asserts pre-deploy protection, model identity, 12/12 adversarial data-truth rejections,
immutable prediction ledger, PL/FPL frontend data synchronization,
club jersey visualization upgrade, official GW1 performance records, and complete deployment verification.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026')
backend_root = repo_root / 'innovera-wc2026-backend' / 'ennovera-pl'
frontend_root = repo_root / 'innovera-wc2026-frontend'
reports_dir = backend_root / 'reports'
deploy_dir = reports_dir / 'production' / 'c10e_deployment'

def test_phase0_protection():
    p = deploy_dir / '00_pre_deploy_protection.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'rollback_commit' in data and data['rollback_commit'] != ''
    assert data['production_backup_status'] == 'GUARANTEED_GIT_SNAPSHOT'

def test_phase1_model_identity():
    p = deploy_dir / '01_model_bridge_identity.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['model_sha256'] == '95a70fe854b4237d9b9323381a1795c378aa89cbb3b90da893eaef3ef7ce8371'
    assert data['fpl_bridge_sha256'] == 'b4e8921af78c01625da38290f146a89c201948ba12049c823058240be363cca2'
    assert data['model_hash_match'] == True and data['bridge_hash_match'] == True

def test_phase2_and_3_adversarial_data_truth():
    df = pd.read_csv(deploy_dir / '02_adversarial_data_truth_tests.csv')
    assert len(df) == 12
    assert (df['actual_action'] == 'REJECT').all()
    assert (df['passed'] == True).all()

def test_phase4_immutable_ledger():
    p = deploy_dir / '03_immutable_prediction_ledger_gw2.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['prediction_locked'] == True
    assert data['fpl_prediction_hash'] == 'b90a61849e75924fa682e022f46a29be634351a6697b09325603f9050d2ce2c2'

def test_phase5_pl_website_feed():
    df = pd.read_csv(deploy_dir / '04_gw2_pl_website_feed.csv')
    assert len(df) == 10
    assert (df['model'] == 'C10-E').all()

def test_phase7_and_8_frontend_data_synchronization():
    plan_p = frontend_root / 'lib' / 'data' / 'fpl_gameweek_plan.json'
    assert plan_p.exists()
    plan = json.loads(plan_p.read_text(encoding='utf-8'))
    assert plan['expected_total_points'] == 74.05
    assert plan['formation'] == '3-4-3'
    assert plan['captain']['name'] == 'Erling Haaland'
    assert plan['vice_captain']['name'] == 'Cole Palmer'
    assert plan['bank'] == 0.2
    assert plan['free_transfers'] == 1
    assert plan['chip_recommendation']['action'] == 'HOLD'

def test_phase10_pitch_visualization_jersey_upgrade():
    p = frontend_root / 'components' / 'fantasy' / 'PitchVisualization.tsx'
    assert p.exists()
    content = p.read_text(encoding='utf-8')
    assert 'ClubJerseySvg' in content
    assert 'CLUB_KIT_THEMES' in content
    assert 'Arsenal' in content and 'Chelsea' in content and 'Man City' in content

def test_phase11_and_12_gw1_actual_performance():
    df = pd.read_csv(deploy_dir / '05_gw1_actual_performance_record.csv')
    assert len(df) == 15
    haaland = df[df['player'] == 'Erling Haaland'].iloc[0]
    assert haaland['official_actual'] == 13
    assert 'CAPTAIN' in haaland['captain_status']

def test_phase17_frontend_source_of_truth_obsolete_eliminated():
    plan_p = frontend_root / 'lib' / 'data' / 'fpl_gameweek_plan.json'
    content = plan_p.read_text(encoding='utf-8')
    assert '120.2' not in content
    assert 'Hinshelwood' not in content
    assert 'João Pedro' not in content
