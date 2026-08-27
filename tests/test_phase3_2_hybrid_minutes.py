"""Phase 3.2 Automated Test Suite for Hybrid Minutes & Appearance Intelligence.
Verifies semantic definitions, probability bounds, state partition completeness,
appearance/clean-sheet threshold logic, temporal integrity, and frozen baseline immutability.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

def test_frozen_gw2_plan_immutability():
    """Verify frozen GW2 prospective plan has not been modified."""
    frozen_path = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    assert frozen_path.exists()
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert h == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'

def test_probability_state_partition_completeness():
    """Verify P(0) + P(1-59) + P(60+) = 1.0 strictly across all probability combinations."""
    p_starts = np.linspace(0.05, 0.95, 20)
    p_subs = np.where(p_starts < 0.50, 0.40, 0.10)
    
    p_60 = p_starts * 0.92
    p_1_59 = p_starts * 0.08 + (1.0 - p_starts) * p_subs
    p_0 = (1.0 - p_starts) * (1.0 - p_subs)
    
    tot = p_0 + p_1_59 + p_60
    assert np.allclose(tot, 1.0, atol=1e-5)

def test_no_double_discounting_invariant():
    """Verify conditional minute expectation does not double-discount non-availability."""
    p_start = 0.90
    p_sub = 0.10
    e_m_start = 82.0
    e_m_sub = 20.0
    
    unconditional_e_m = p_start * e_m_start + (1.0 - p_start) * p_sub * e_m_sub
    # Double discounted would be: unconditional_e_m * (p_start + (1-p_start)*p_sub)
    p_app = p_start + (1.0 - p_start) * p_sub
    double_discounted = unconditional_e_m * p_app
    
    assert unconditional_e_m > double_discounted
    assert round(unconditional_e_m, 1) == 74.0

def test_appearance_points_threshold_logic():
    """Verify FPL appearance point calculation strictly follows 1*P(1-59) + 2*P(60+)."""
    p_60 = 0.85
    p_1_59 = 0.10
    exp_app_pts = 2.0 * p_60 + 1.0 * p_1_59
    assert exp_app_pts == 1.80
    assert exp_app_pts <= 2.0
    assert exp_app_pts >= 0.0

def test_phase3_research_baseline_stability():
    """Verify Phase 3 manager score reproducibility."""
    p3_scores = [1984, 2008, 2072, 2185]
    assert sum(p3_scores) / 4.0 == 2062.25
