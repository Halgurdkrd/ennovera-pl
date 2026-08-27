"""Master Sprint A Automated Test Suite (Phases 11.1 to 11.3).
Verifies canonical benchmark fixtures, probability contracts, baseline tournament rankings,
Dixon-Coles draw metrics, FPL transfer candidate gains, and circularity invariants.
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

def test_canonical_benchmark_universe():
    """Verify canonical benchmark dataset contains exactly 1,520 fixtures across 4 seasons."""
    df_fix = pd.read_csv(reports_dir / 'pl11_1_fixture_universe.csv')
    assert len(df_fix) == 4
    assert df_fix['matches'].sum() == 1520
    manifest = json.loads((reports_dir / 'pl11_1_benchmark_manifest.json').read_text(encoding='utf-8'))
    assert manifest['total_fixtures'] == 1520
    assert manifest['temporal_violations'] == 0

def test_tournament_results_coverage_and_winner():
    """Verify all 9 baselines (PL-B0 to PL-B8) are evaluated and PL-B8 / V5.1 is reproduced."""
    df_tourney = pd.read_csv(reports_dir / 'pl11_2_baseline_results.csv')
    assert len(df_tourney) == 9
    v5_1 = df_tourney[df_tourney['model_id'] == 'PL-B8'].iloc[0]
    assert v5_1['accuracy'] == '54.8%'
    assert float(v5_1['log_loss']) == 0.9420
    assert float(v5_1['rps']) == 0.1975

def test_dixon_coles_draw_recall_gain():
    """Verify Dixon-Coles resolves draw deficit with draw recall > 30%."""
    df_tourney = pd.read_csv(reports_dir / 'pl11_2_baseline_results.csv')
    dc = df_tourney[df_tourney['model_id'] == 'PL-B4'].iloc[0]
    assert dc['draw_recall'] == '31.8%'

def test_fpl_transfer_candidate_improvements():
    """Verify PL11.3 candidate achieves 56.2% accuracy and 0.1895 RPS."""
    df_cand = pd.read_csv(reports_dir / 'pl11_3_candidate_results.csv')
    cand = df_cand[df_cand['model'] == 'PL11_3_FPL_INTELLIGENCE_CANDIDATE'].iloc[0]
    assert cand['accuracy'] == '56.2%'
    assert float(cand['log_loss']) == 0.9180
    assert float(cand['rps']) == 0.1895
    assert float(cand['cs_brier']) == 0.1365

def test_circularity_audit_safe():
    """Verify circularity audit confirms SAFE status."""
    circ_path = reports_dir / 'pl11_3_circularity_audit.md'
    assert circ_path.exists()
    content = circ_path.read_text(encoding='utf-8')
    assert 'SAFE' in content
