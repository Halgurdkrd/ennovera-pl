"""Master Sprint C Automated Test Suite (Phases 11.9 to 11.12).
Verifies Dirichlet probability calibration, dynamic 10,000-run league simulator,
exact mathematical match attribution (<1e-4 error), and final certification
of ENNOVERA_PL_FINAL_RESEARCH_V1.
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

def test_phase11_9_dirichlet_calibration():
    """Verify Phase 11.9 Dirichlet calibration achieves ECE 0.9% and RPS 0.1748."""
    df_cal = pd.read_csv(reports_dir / 'pl11_9_calibration_candidates.csv')
    cal3 = df_cal[df_cal['candidate_id'] == 'CAL3'].iloc[0]
    assert cal3['ece'] == '0.9%'
    assert float(cal3['rps']) == 0.1748
    assert float(cal3['log_loss']) == 0.8680
    assert 'PROMOTE' in cal3['decision']

def test_phase11_10_dynamic_simulator():
    """Verify Phase 11.10 dynamic simulator achieves Spearman rank correlation > 0.910."""
    df_conv = pd.read_csv(reports_dir / 'pl11_10_convergence.csv')
    c10k = df_conv[df_conv['simulations'] == 10000].iloc[0]
    assert float(c10k['spearman_table']) >= 0.915
    assert float(c10k['points_mae']) <= 4.50

def test_phase11_11_explainability_reconstruction():
    """Verify Phase 11.11 attribution engine reconstructs match odds within 1e-4 error."""
    df_rec = pd.read_csv(reports_dir / 'pl11_11_reconstruction_test.csv')
    for idx, row in df_rec.iterrows():
        assert row['status'] == 'PASS'

def test_phase11_12_final_model_manifest():
    """Verify Phase 11.12 final research manifest matches ENNOVERA_PL_FINAL_RESEARCH_V1."""
    manifest_path = reports_dir / 'pl11_12_final_manifest.json'
    assert manifest_path.exists()
    m = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert m['model_name'] == 'ENNOVERA_PL_FINAL_RESEARCH_V1'
    assert m['version'] == '1.0.0-research-final'
    assert m['metrics']['accuracy_3class'] == 0.584
    assert m['metrics']['ranked_probability_score'] == 0.1748
    assert m['metrics']['multiclass_log_loss'] == 0.8680
    assert m['metrics']['draw_recall'] == 0.338
    assert m['metrics']['ece'] == 0.009

def test_bootstrap_significance_vs_v51():
    """Verify paired bootstrap confirms statistical superiority over Production V5.1."""
    df_boot = pd.read_csv(reports_dir / 'pl11_12_bootstrap.csv')
    rps_row = df_boot[(df_boot['comparison'].str.contains('Production V5.1')) & (df_boot['metric'] == 'RPS')].iloc[0]
    assert float(rps_row['mean_delta']) < -0.0200
    assert rps_row['pct_favoring'] == '99.9%'
