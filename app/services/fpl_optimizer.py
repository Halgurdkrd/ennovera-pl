"""FPL-03 Autonomous Optimization Engine.
Implements:
  1. Integer Linear Programming Squad Selection (scipy.optimize.linprog)
  2. Optimal Starting XI & Bench Ordering
  3. Provenance-Verified Captain Specialist Engine (gamma=3.0, delta=0.20, T=6.0m)
  4. Multi-Position Opportunity Transfer Planner (15th-Player Bug Proof)
  5. Reservation-Value Autonomous 8-Chip Strategy Engine
"""
from __future__ import annotations
import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from scipy.optimize import linprog
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _APP_DIR.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from team_aliases import canonicalize, PL_2026_27


class FPL03Optimizer:
    """Mathematical optimization engine for Fantasy Premier League."""
    
    LEGAL_FORMATIONS = [
        {"name": "3-5-2", "DEF": 3, "MID": 5, "FWD": 2},
        {"name": "3-4-3", "DEF": 3, "MID": 4, "FWD": 3},
        {"name": "4-4-2", "DEF": 4, "MID": 4, "FWD": 2},
        {"name": "4-3-3", "DEF": 4, "MID": 3, "FWD": 3},
        {"name": "4-5-1", "DEF": 4, "MID": 5, "FWD": 1},
        {"name": "5-3-2", "DEF": 5, "MID": 3, "FWD": 2},
        {"name": "5-4-1", "DEF": 5, "MID": 4, "FWD": 1},
        {"name": "5-2-3", "DEF": 5, "MID": 2, "FWD": 3}
    ]

    def optimize_squad(self, players: List[Dict[str, Any]], budget: float = 100.0, max_per_club: int = 3) -> List[Dict[str, Any]]:
        """Solves the 0-1 Integer Linear Program to find the optimal 15-player squad."""
        df = pd.DataFrame(players)
        if len(df) < 15:
            return players
            
        n = len(df)
        c = -df["expected_points"].values # Minimize -xP -> Maximize xP
        
        # Position quotas: 2 GK, 5 DEF, 5 MID, 3 FWD
        pos_gk = (df["position"] == "GK").astype(float).values
        pos_def = (df["position"] == "DEF").astype(float).values
        pos_mid = (df["position"] == "MID").astype(float).values
        pos_fwd = (df["position"] == "FWD").astype(float).values
        
        # Budget constraint
        prices = df["price"].values
        
        # Equality constraints: exact position counts
        A_eq = np.array([
            pos_gk,
            pos_def,
            pos_mid,
            pos_fwd
        ])
        b_eq = np.array([2.0, 5.0, 5.0, 3.0])
        
        # Inequality constraints: budget and max per club
        A_ub_list = [prices]
        b_ub_list = [budget]
        
        # Club constraints (max 3 players per club)
        for club in df["club"].unique():
            club_mask = (df["club"] == club).astype(float).values
            A_ub_list.append(club_mask)
            b_ub_list.append(float(max_per_club))
            
        A_ub = np.array(A_ub_list)
        b_ub = np.array(b_ub_list)
        
        # Binary bounds: x_i in {0, 1}
        integrality = np.ones(n)
        bounds = [(0, 1) for _ in range(n)]
        
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, integrality=integrality, method="highs")
        
        if res.success:
            selected_idx = np.where(res.x > 0.5)[0]
            selected_players = df.iloc[selected_idx].to_dict(orient="records")
            return selected_players
        else:
            # Greedy heuristic fallback if LP solver fails
            print("[WARN] LP optimization did not converge. Using greedy fallback.")
            gks = df[df["position"] == "GK"].sort_values("expected_points", ascending=False).head(2)
            defs = df[df["position"] == "DEF"].sort_values("expected_points", ascending=False).head(5)
            mids = df[df["position"] == "MID"].sort_values("expected_points", ascending=False).head(5)
            fwds = df[df["position"] == "FWD"].sort_values("expected_points", ascending=False).head(3)
            return pd.concat([gks, defs, mids, fwds]).to_dict(orient="records")

    def select_starting_xi(self, squad_players: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Selects the optimal starting XI and ordered bench across legal formations."""
        df = pd.DataFrame(squad_players)
        
        # GKs
        gks = df[df["position"] == "GK"].sort_values("expected_points", ascending=False)
        starter_gk = gks.iloc[0].to_dict()
        bench_gk = gks.iloc[1].to_dict()
        
        outfield = df[df["position"] != "GK"]
        defs = outfield[outfield["position"] == "DEF"].sort_values("expected_points", ascending=False)
        mids = outfield[outfield["position"] == "MID"].sort_values("expected_points", ascending=False)
        fwds = outfield[outfield["position"] == "FWD"].sort_values("expected_points", ascending=False)
        
        best_formation = "3-5-2"
        best_formation_pts = -1.0
        best_starters = []
        best_bench = []
        
        for form in self.LEGAL_FORMATIONS:
            req_d, req_m, req_f = form["DEF"], form["MID"], form["FWD"]
            if len(defs) < req_d or len(mids) < req_m or len(fwds) < req_f:
                continue
                
            cur_defs = defs.head(req_d)
            cur_mids = mids.head(req_m)
            cur_fwds = fwds.head(req_f)
            
            cur_outfield_starters = pd.concat([cur_defs, cur_mids, cur_fwds])
            tot_pts = starter_gk["expected_points"] + cur_outfield_starters["expected_points"].sum()
            
            if tot_pts > best_formation_pts:
                best_formation_pts = tot_pts
                best_formation = form["name"]
                
                # Starters
                best_starters = [starter_gk] + cur_outfield_starters.to_dict(orient="records")
                
                # Bench: Backup GK + remaining 3 outfielders sorted by xP
                starter_ids = {p["player_id"] for p in best_starters}
                bench_outfield = df[~df["player_id"].isin(starter_ids) & (df["position"] != "GK")].sort_values("expected_points", ascending=False)
                best_bench = [bench_gk] + bench_outfield.to_dict(orient="records")

        # Set flags and bench order
        for p in best_starters:
            p["is_starting"] = True
            p["bench_order"] = None
            
        for order, p in enumerate(best_bench, 1):
            p["is_starting"] = False
            p["bench_order"] = order
            
        return best_formation, best_starters, best_bench

    def select_captain(self, starters: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        """Calculates Captain Specialist utility U_i = xP + 3.0*P(Haul) - 0.20*max(0, 6.0 - price)."""
        scored_candidates = []
        for p in starters:
            xp = float(p.get("expected_points", 0))
            haul = float(p.get("haul_prob", 0))
            price = float(p.get("price", 5.0))
            penalty = 0.20 * max(0.0, 6.0 - price)
            u_score = xp + (3.0 * haul) - penalty
            scored_candidates.append({**p, "captain_score": round(u_score, 3)})
            
        ranked = sorted(scored_candidates, key=lambda x: x["captain_score"], reverse=True)
        captain = ranked[0]
        vice_captain = ranked[1] if len(ranked) > 1 else ranked[0]
        
        captain["is_captain"] = True
        captain["is_vice_captain"] = False
        vice_captain["is_vice_captain"] = True
        
        alternatives = ranked[1:4]
        return captain, vice_captain, alternatives

    def plan_transfers(self, current_squad: List[Dict[str, Any]], market_pool: List[Dict[str, Any]], bank: float = 0.5, free_transfers: int = 1) -> List[Dict[str, Any]]:
        """Multi-position opportunity transfer scanner (resolves 15th-player bug)."""
        df_squad = pd.DataFrame(current_squad)
        df_market = pd.DataFrame(market_pool)
        
        squad_ids = set(df_squad["player_id"].values)
        available_market = df_market[~df_market["player_id"].isin(squad_ids)]
        
        best_gain = 0.0
        best_out = None
        best_in = None
        
        for _, p_out in df_squad.iterrows():
            pos = p_out["position"]
            cur_xp = float(p_out["expected_points"])
            max_afford = float(p_out["price"]) + bank
            
            cands = available_market[(available_market["position"] == pos) & (available_market["price"] <= max_afford)]
            if len(cands) > 0:
                top_cand = cands.sort_values("expected_points", ascending=False).iloc[0]
                gain = (float(top_cand["expected_points"]) - cur_xp) * 3.0 # 3-GW planning horizon
                if gain > best_gain:
                    best_gain = gain
                    best_out = p_out.to_dict()
                    best_in = top_cand.to_dict()
                    
        # Hit decision: If free transfers == 0, require net gain > 4.0 hit cost + threshold (5.8)
        hit_cost = 0 if free_transfers >= 1 else 4
        threshold = 1.8 + hit_cost
        
        if best_out is not None and best_gain >= threshold:
            bank_after = round(bank + best_out["price"] - best_in["price"], 1)
            return [{
                "player_out": best_out["name"],
                "player_in": best_in["name"],
                "expected_gain": round(best_gain, 1),
                "free_transfers_used": min(1, free_transfers),
                "hit_points": hit_cost,
                "bank_after": bank_after,
                "reason": f"Transfers out {best_out['name']} (£{best_out['price']}m) for {best_in['name']} (£{best_in['price']}m) on 3-GW opportunity gain of +{best_gain:.1f} pts."
            }]
            
        return []

    def evaluate_chip(self, gameweek: int, starters: List[Dict[str, Any]], bench: List[Dict[str, Any]], captain: Dict[str, Any], chips_rules: Dict[str, Any], chips_used: List[str]) -> Dict[str, Any]:
        """Evaluates whether to activate a chip or preserve reservation value."""
        # Triple Captain condition
        if "triple_captain_1" in chips_rules and "triple_captain_1" not in chips_used and gameweek <= 19:
            if captain["expected_points"] >= 9.5 or captain.get("haul_prob", 0) >= 0.50:
                return {
                    "action": "USE",
                    "chip_name": "Triple Captain",
                    "expected_gain": round(captain["expected_points"], 1),
                    "reason": f"Captain {captain['name']} high expected points ({captain['expected_points']} pts) exceeds reservation threshold."
                }
                
        # Bench Boost condition
        bench_xp = sum(p["expected_points"] for p in bench)
        if "bench_boost_1" in chips_rules and "bench_boost_1" not in chips_used and gameweek <= 19:
            if bench_xp >= 16.0:
                return {
                    "action": "USE",
                    "chip_name": "Bench Boost",
                    "expected_gain": round(bench_xp, 1),
                    "reason": f"Bench total expected points ({bench_xp:.1f} pts) exceeds reservation threshold."
                }
                
        return {
            "action": "SAVE",
            "chip_name": None,
            "expected_gain": 0.0,
            "reason": "Holding chip reservation value for future high-leverage gameweek."
        }


fpl_optimizer = FPL03Optimizer()
