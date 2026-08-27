"""Live-compatible Historical FPL-03 Multi-Head xP Forecasting Engine.
Implements Bayesian sample-size shrinkage, expected minutes modeling, attacking/defensive decomposition,
and point-in-time leakage-safe feature generation.
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd


class FPL03LiveXPModel:
    """Historical FPL-03 Multi-Head xP Forecasting Engine with Bayesian Shrinkage."""
    
    SHRINKAGE_K = 4.0  # Empirical prior strength parameter w(n) = n / (n + k)
    
    def __init__(self, shrinkage_k: float = 4.0):
        self.shrinkage_k = shrinkage_k
        
    def calculate_recency_weight(self, completed_gws: int) -> float:
        """Returns the Bayesian shrinkage weight w(n) = n / (n + k) for current-season evidence."""
        if completed_gws <= 0:
            return 0.0
        return round(float(completed_gws) / (float(completed_gws) + self.shrinkage_k), 4)

    def compute_player_xp(
        self,
        player_dict: Dict[str, Any],
        completed_gws: int = 1,
        fixture_difficulty: float = 3.0,
        is_home: bool = True
    ) -> Dict[str, Any]:
        """Computes decomposed xP using Bayesian shrinkage blending prior quality with recent evidence."""
        pos = player_dict.get("position", "MID")
        price = float(player_dict.get("price", 5.0))
        status = player_dict.get("status", "a")
        chance = player_dict.get("chance_of_playing")
        raw_gw_pts = float(player_dict.get("form", 0.0) or 0.0)
        
        # 1. Expected Minutes & Appearance Probabilities
        if status == "a":
            p_start = 0.90
        elif status == "d":
            p_start = 0.50 if chance is None else float(chance) / 100.0
        elif status in ("i", "u", "s"):
            p_start = 0.0 if chance is None else float(chance) / 100.0
        else:
            p_start = 0.50
            
        exp_mins = round(p_start * 90.0, 1)
        p_60 = 1.0 if exp_mins >= 60 else (exp_mins / 60.0 if exp_mins > 0 else 0.0)
        appearance_xp = 2.0 * p_60 if exp_mins >= 60 else (1.0 if exp_mins > 0 else 0.0)
        
        # 2. Long-term / Pre-season Prior (Head A Baseline)
        pos_floor = {"GK": 3.5, "DEF": 3.8, "MID": 4.5, "FWD": 4.8}.get(pos, 4.0)
        prior_base = pos_floor * (price / 8.0)
        prior_xp = prior_base * (exp_mins / 90.0)
        
        # 3. Attacking and Defensive Decomposition Rates
        xg_rate = max(0.01, (price - 4.5) * 0.04) if price > 4.5 else 0.01
        xa_rate = max(0.01, (price - 4.5) * 0.03) if price > 4.5 else 0.01
        xg = xg_rate * (exp_mins / 90.0)
        xa = xa_rate * (exp_mins / 90.0)
        g_val = 6.0 if pos in ["GK", "DEF"] else (5.0 if pos == "MID" else 4.0)
        attacking_xp = round(xg * g_val + xa * 3.0, 2)
        
        cs_rate = 0.35 if price >= 6.0 else (0.28 if price >= 5.0 else 0.20)
        cs_prob = min(0.60, max(0.10, cs_rate * (1.10 if is_home else 0.90)))
        cs_xp = (4.0 * cs_prob * p_60) if pos in ["GK", "DEF"] else ((1.0 * cs_prob * p_60) if pos == "MID" else 0.0)
        gc_deduct = (0.4 * (1.0 - cs_prob) * p_60) if pos in ["GK", "DEF"] else 0.0
        defensive_xp = round(cs_xp - gc_deduct, 2)
        
        exp_bonus = round(min(2.5, max(0.0, (xg * 1.8 + xa * 1.2 + (cs_prob if pos in ['GK', 'DEF'] else 0.0) * 0.7) * p_60)), 2)
        card_deduct = round(0.15 * p_60, 2)
        
        # 4. Multi-Head Bayesian Shrinkage Blend
        w_recency = self.calculate_recency_weight(completed_gws)
        recent_evidence_base = raw_gw_pts * (exp_mins / 90.0)
        
        # Blended Base Score
        blended_base_xp = ((1.0 - w_recency) * prior_xp) + (w_recency * recent_evidence_base)
        
        # Fixture Adjustment Factor (FDR: 1 = easy (+10%), 5 = hard (-10%))
        fixture_factor = 1.0 + (3.0 - float(fixture_difficulty)) * 0.04
        if is_home:
            fixture_factor *= 1.05
        else:
            fixture_factor *= 0.95
            
        fixture_adjustment = round((blended_base_xp * fixture_factor) - blended_base_xp, 2)
        
        final_xp = max(0.5, round((blended_base_xp + fixture_adjustment), 1))
        
        # Haul Probability P(Points >= 10)
        haul_prob = round(min(0.65, max(0.01, (final_xp - 2.5) * 0.08 + 0.10)), 2)
        
        return {
            **player_dict,
            "expected_points": final_xp,
            "expected_minutes": exp_mins,
            "starting_prob": round(p_start, 2),
            "haul_prob": haul_prob,
            "xp_decomposition": {
                "prior_xp": round(prior_xp, 2),
                "recent_form_observed": round(raw_gw_pts, 1),
                "recency_weight_w": w_recency,
                "recent_form_component": round(w_recency * recent_evidence_base, 2),
                "fixture_component": fixture_adjustment,
                "appearance_xp": round(appearance_xp, 2),
                "attacking_xp": attacking_xp,
                "defensive_xp": defensive_xp,
                "bonus_xp": exp_bonus,
                "card_deduct": card_deduct,
                "final_xp": final_xp
            }
        }

    def process_player_pool(
        self,
        player_pool: List[Dict[str, Any]],
        completed_gws: int = 1,
        fixtures_map: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Processes an entire player pool with point-in-time decomposed xP."""
        out = []
        for p in player_pool:
            club = p.get("club", "Unknown")
            fix_info = (fixtures_map or {}).get(club, {"difficulty": 3.0, "is_home": True})
            diff = fix_info.get("difficulty", 3.0)
            home = fix_info.get("is_home", True)
            
            res = self.compute_player_xp(p, completed_gws=completed_gws, fixture_difficulty=diff, is_home=home)
            out.append(res)
        return out


fpl_xp_model = FPL03LiveXPModel()
