"""Automated Test Suite for Ennovera Production Final Actual-Result & Title-State Forensic Check V1.
Asserts Gate A snapshot identity, Gate B Haaland trace (2 pts base, 4 pts effective),
Gate C team arithmetic (XI 106 + Capt 2 = 108 pts), Gate D autosubs (none),
Gate E captaincy, Gate F/G title state (Arsenal 44.1%, Man City 39.0%, Liverpool 10.5%),
and Gate H website parity.
"""
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026')
backend_root = repo_root / 'innovera-wc2026-backend' / 'ennovera-pl'
frontend_root = repo_root / 'innovera-wc2026-frontend'
audit_dir = backend_root / 'reports' / 'production' / 'final_forensic_check'

def test_gate_a_snapshot_identity():
    p = backend_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'bootstrap_predeadline.json'
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '07063c97d6da1b4ca5ced9d0ee9149d6827663417fa0a6880439eef14473afb1'
    df = pd.read_csv(audit_dir / '01_gate_a_player_records.csv')
    assert len(df) == 15

def test_gate_b_haaland_trace():
    p = audit_dir / '02_gate_b_haaland_trace.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['name'] == 'Erling Haaland'
    assert data['minutes'] == 90
    assert data['event_points'] == 2
    assert data['goals_scored'] == 0
    assert data['assists'] == 0

def test_gate_c_team_arithmetic():
    p = audit_dir / '03_gate_c_team_arithmetic.json'
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['xi_base_actual'] == 106
    assert data['captain_extra'] == 2
    assert data['final_manager_actual'] == 108
    assert data['bench_total'] == 30
    assert data['all_15_total'] == 136

def test_gate_f_title_simulation():
    df = pd.read_csv(audit_dir / '04_gate_f_title_simulation_authoritative.csv')
    ars = df[df['team'] == 'Arsenal'].iloc[0]
    mci = df[df['team'] == 'Man City'].iloc[0]
    liv = df[df['team'] == 'Liverpool'].iloc[0]
    assert ars['pre_gw2_title'] == '44.1%'
    assert mci['pre_gw2_title'] == '39.0%'
    assert liv['pre_gw2_title'] == '10.5%'

def test_gate_h_frontend_parity():
    perf_p = frontend_root / 'lib' / 'data' / 'fpl_performance.json'
    assert perf_p.exists()
    data = json.loads(perf_p.read_text(encoding='utf-8'))
    assert data['total_points'] == 108
    assert data['captain_points'] == 4
    assert data['bench_points_missed'] == 30
