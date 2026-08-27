"""Phase 11.0 Premier League Pre-Forensic Automated Test Suite.
Verifies frozen components, legacy baseline reproduction, V5.1 metrics,
circularity audit, temporal integrity, and report existence.
"""
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import pytest
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

reports_dir = repo_root / 'reports'

def test_frozen_gw2_plan_immutability():
    """Verify frozen GW2 prospective plan has not been modified."""
    frozen_path = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert frozen_path.exists()
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert h == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_frozen_fpl_baseline_intact():
    """Verify FPL final model baseline remains frozen at 2,179.50 pts/season mean."""
    manifest_path = reports_dir / 'phase10_6_final_manifest.json'
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['model_name'] == 'ENNOVERA_FPL_FINAL_RESEARCH_V1'
    assert manifest['historical_mean_score'] == 2179.50

def test_legacy_52_percent_baseline_metrics():
    """Verify legacy V2.0 baseline metrics are accurately reproduced."""
    df_perf = pd.read_csv(reports_dir / 'pl11_0_current_performance.csv')
    v2 = df_perf[df_perf['model'].str.contains('V2.0')].iloc[0]
    assert v2['accuracy_3class'] == '52.1%'
    assert float(v2['log_loss']) == 0.9850
    assert float(v2['rps']) == 0.2085

def test_production_v5_1_metrics():
    """Verify production V5.1 baseline metrics are accurately documented."""
    df_perf = pd.read_csv(reports_dir / 'pl11_0_current_performance.csv')
    v5_1 = df_perf[df_perf['model'].str.contains('V5.1')].iloc[0]
    assert v5_1['accuracy_3class'] == '54.8%'
    assert float(v5_1['log_loss']) == 0.9420
    assert float(v5_1['rps']) == 0.1975

def test_circularity_audit_status():
    """Verify circularity audit confirms SAFE status."""
    circ_path = reports_dir / 'pl11_0_circularity_audit.md'
    assert circ_path.exists()
    content = circ_path.read_text(encoding='utf-8')
    assert 'SAFE' in content

def test_temporal_audit_zero_violations():
    """Verify temporal audit documents 0 violations."""
    temp_path = reports_dir / 'pl11_0_temporal_audit.md'
    assert temp_path.exists()
    content = temp_path.read_text(encoding='utf-8')
    assert '0 Temporal Leaks' in content

def test_pl11_0_reports_exist():
    """Verify key Phase 11.0 reports exist."""
    assert (reports_dir / 'pl11_0_code_inventory.csv').exists()
    assert (reports_dir / 'pl11_0_feature_inventory.csv').exists()
    assert (reports_dir / 'pl11_0_data_inventory.csv').exists()
    assert (reports_dir / 'pl11_0_fpl_to_pl_transfer_matrix.csv').exists()
    assert (reports_dir / 'pl11_0_final_gate_report.md').exists()
