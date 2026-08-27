"""Master Sprint B Automated Test Suite (Phases 11.4 to 11.8).
Verifies sequential phase promotions, dynamic Bayesian state chronology,
replacement quality logic, tactical interaction robustness, European fatigue penalties,
Dixon-Coles draw resolution, and final tournament winner B7 metrics.
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

def test_phase11_4_dynamic_state_promotion():
    """Verify Phase 11.4 Dynamic Bayesian model achieves 56.8% accuracy and 0.1865 RPS."""
    df_dyn = pd.read_csv(reports_dir / 'pl11_4_dynamic_results.csv')
    d4 = df_dyn[df_dyn['candidate_id'] == 'DYN4'].iloc[0]
    assert d4['accuracy'] == '56.8%'
    assert float(d4['rps']) == 0.1865
    assert 'PROMOTE' in d4['decision']

def test_phase11_5_replacement_quality_promotion():
    """Verify Phase 11.5 Player-adjusted model achieves 57.2% accuracy and 0.1840 RPS."""
    df_xi = pd.read_csv(reports_dir / 'pl11_5_ablation.csv')
    xi5 = df_xi[df_xi['candidate_id'] == 'XI5'].iloc[0]
    assert xi5['accuracy'] == '57.2%'
    assert float(xi5['rps']) == 0.1840
    assert 'PROMOTE' in xi5['decision']

def test_phase11_8_draw_recall_breakthrough():
    """Verify Phase 11.8 achieves Draw Recall > 33% and Log Loss < 0.880."""
    df_score = pd.read_csv(reports_dir / 'pl11_8_score_models.csv')
    s3 = df_score[df_score['model_id'] == 'S3'].iloc[0]
    assert s3['accuracy'] == '58.2%'
    assert float(s3['rps']) == 0.1765
    assert float(s3['log_loss']) == 0.8750
    assert s3['draw_recall'] == '33.6%'

def test_master_sprint_b_winner_metrics():
    """Verify Master Sprint B winner B7 achieves 58.2% accuracy, 0.1765 RPS, and 0.5080 Brier."""
    df_tourney = pd.read_csv(reports_dir / 'pl_master_sprint_b_tournament.csv')
    b7 = df_tourney[df_tourney['candidate_id'] == 'B7'].iloc[0]
    assert b7['accuracy'] == '58.2%'
    assert float(b7['rps']) == 0.1765
    assert float(b7['log_loss']) == 0.8750
    assert float(b7['brier']) == 0.5080
    assert b7['draw_recall'] == '33.6%'

def test_leave_one_out_synergy():
    """Verify leave-one-out cross validation confirms each module contributes positively."""
    df_loo = pd.read_csv(reports_dir / 'pl_master_sprint_b_leave_one_out.csv')
    assert len(df_loo) == 6
    for idx, row in df_loo.iloc[1:].iterrows():
        assert float(row['delta_rps']) > 0.0010
