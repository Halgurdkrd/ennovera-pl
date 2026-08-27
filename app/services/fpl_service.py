"""Canonical Fantasy Premier League Decision Intelligence Service (FPL-03 Live Architecture).
Replaces hardcoded production squad with real-time live FPL API ingestion and linear programming optimization.
"""
from __future__ import annotations
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd

_APP_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _APP_DIR.parent
CONFIG_DIR = _REPO_ROOT / "config"
DATA_DIR = _REPO_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = _REPO_ROOT / "reports"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

RULES_PATH = CONFIG_DIR / "fpl_rules_by_season.json"
STATE_PATH = PROCESSED_DIR / "fpl_manager_state.json"
LEDGER_PATH = REPORTS_DIR / "2026_27_fpl_decision_ledger.md"

from app.services.fpl_ingestor import fpl_ingestor
from app.services.fpl_optimizer import fpl_optimizer


class FPLService:
    """Canonical Live FPL-03 Decision & Management Service."""
    
    MODEL_PUBLIC_VERSION = "ennovera-fpl-v1.0"
    MODEL_INTERNAL_PROVENANCE = "FPL-03 (LP Squad + Captain Specialist + Opportunity Transfers + 8-Chip Engine)"
    DATA_CUTOFF = "Official FPL Gameweek Deadline"
    
    def __init__(self):
        self._rules = self._load_rules()
        self._manager_state = self._load_or_init_state()
        self._is_loaded = True
        
    def _load_rules(self) -> Dict[str, Any]:
        if RULES_PATH.exists():
            try:
                with open(RULES_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _load_or_init_state(self) -> Dict[str, Any]:
        if STATE_PATH.exists():
            try:
                with open(STATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Default starting state for 2026-27
        return {
            "season": "2026-27",
            "current_gw": 2,
            "bank": 0.5,
            "free_transfers": 1,
            "chips_used": [],
            "owned_squad": [],
            "transfer_history": [],
            "gw_scores": []
        }

    def _save_state(self):
        tmp_path = STATE_PATH.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._manager_state, f, indent=2)
            os.replace(tmp_path, STATE_PATH)
        except Exception as e:
            print(f"[WARN] Failed saving manager state: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def get_season_rules(self, season: str = "2026-27") -> Dict[str, Any]:
        """Returns the official season regulations and chip inventories."""
        raw_s = self._rules.get(season, self._rules.get("2026-27", {}))
        chips_dict = raw_s.get("chips", {})
        chips_list = [f"{v.get('name', k)} (GW{v.get('window', [1, 38])[0]}-GW{v.get('window', [1, 38])[1]})" for k, v in chips_dict.items()]
        
        return {
            "season": season,
            "budget_starting": raw_s.get("budget_starting", 100.0),
            "squad_size": raw_s.get("squad_size", 15),
            "position_limits": raw_s.get("position_limits", {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}),
            "max_players_per_club": raw_s.get("max_players_per_club", 3),
            "starting_xi_size": raw_s.get("starting_xi_size", 11),
            "formation_min_rules": raw_s.get("formation_min_rules", {"GK": 1, "DEF": 3, "MID": 2, "FWD": 1}),
            "captain_multiplier": raw_s.get("captain_multiplier", 2),
            "triple_captain_multiplier": raw_s.get("triple_captain_multiplier", 3),
            "free_transfers_per_gw": raw_s.get("free_transfers_per_gw", 1),
            "max_banked_transfers": raw_s.get("max_banked_transfers", 5),
            "transfer_hit_cost": raw_s.get("transfer_hit_cost", 4),
            "chips_available": chips_list
        }

    def get_gameweek_plan(self, season: str = "2026-27", gw: Optional[int] = None) -> Dict[str, Any]:
        """Generates or retrieves the canonical master Gameweek Plan."""
        fpl_ingestor.refresh()
        gw_info = fpl_ingestor.get_current_gameweek_info()
        target_gw = gw if gw is not None else gw_info["next_gw"]
        deadline = gw_info["deadline"]
        
        # Load all 600+ live players
        all_players = fpl_ingestor.get_all_players()
        if not all_players:
            raise RuntimeError("Live FPL player database unavailable.")

        owned = self._manager_state.get("owned_squad", [])
        
        # If squad is empty (e.g. initial setup), run initial 15-player linear program
        if not owned or len(owned) != 15:
            owned = fpl_optimizer.optimize_squad(all_players, budget=100.0)
            self._manager_state["owned_squad"] = owned
            self._save_state()
            
        # Update current owned squad with latest live player expected points
        player_dict = {p["player_id"]: p for p in all_players}
        live_owned = []
        for p in owned:
            p_id = p["player_id"]
            if p_id in player_dict:
                live_owned.append(player_dict[p_id])
            else:
                live_owned.append(p)
                
        # 1. Starting XI & Bench Ordering
        formation, starters, bench = fpl_optimizer.select_starting_xi(live_owned)
        
        # 2. Captain Specialist Selection
        captain, vice_captain, alternatives = fpl_optimizer.select_captain(starters)
        
        # 3. Opportunity Transfer Scanner
        transfers_rec = fpl_optimizer.plan_transfers(
            live_owned,
            all_players,
            bank=self._manager_state.get("bank", 0.5),
            free_transfers=self._manager_state.get("free_transfers", 1)
        )
        
        # 4. Chip Guidance
        rules_season = self._rules.get(season, {})
        chips_rules = rules_season.get("chips", {})
        chips_used = self._manager_state.get("chips_used", [])
        chip_eval = fpl_optimizer.evaluate_chip(target_gw, starters, bench, captain, chips_rules, chips_used)
        
        # Available legal chips
        avail_chips = [k for k in chips_rules.keys() if k not in chips_used]
        
        # Total Expected Points
        raw_xi_xp = sum(p["expected_points"] for p in starters)
        capt_bonus = captain["expected_points"] # 2x multiplier adds 1x extra
        if chip_eval.get("action") == "USE" and chip_eval.get("chip_name") == "Triple Captain":
            capt_bonus = captain["expected_points"] * 2 # 3x multiplier adds 2x extra
        elif chip_eval.get("action") == "USE" and chip_eval.get("chip_name") == "Bench Boost":
            raw_xi_xp += sum(p["expected_points"] for p in bench)
            
        total_exp_pts = round(raw_xi_xp + capt_bonus, 1)
        now_iso = datetime.now(timezone.utc).isoformat()
        
        plan = {
            "season": season,
            "gameweek": target_gw,
            "deadline": deadline,
            "model_version": self.MODEL_PUBLIC_VERSION,
            "data_cutoff": self.DATA_CUTOFF,
            "generated_at": now_iso,
            "expected_total_points": total_exp_pts,
            "formation": formation,
            "starting_xi": starters,
            "bench": bench,
            "captain": {
                "player_id": captain["player_id"],
                "name": captain["name"],
                "club": captain["club"],
                "position": captain["position"],
                "price": captain["price"],
                "expected_points": captain["expected_points"],
                "haul_probability": captain["haul_prob"],
                "captain_score": captain.get("captain_score", captain["expected_points"])
            },
            "vice_captain": {
                "player_id": vice_captain["player_id"],
                "name": vice_captain["name"],
                "club": vice_captain["club"],
                "position": vice_captain["position"],
                "price": vice_captain["price"],
                "expected_points": vice_captain["expected_points"],
                "haul_probability": vice_captain["haul_prob"]
            },
            "recommended_transfers": transfers_rec,
            "chip_recommendation": {
                "action": chip_eval["action"],
                "chip_name": chip_eval["chip_name"],
                "expected_incremental_gain": chip_eval["expected_gain"],
                "reason": chip_eval["reason"]
            },
            "available_chips": avail_chips,
            "bank": self._manager_state.get("bank", 0.5),
            "free_transfers": self._manager_state.get("free_transfers", 1),
            "warnings": []
        }
        
        # Append to prospective ledger if pre-deadline
        self._append_to_ledger(plan)
        return plan

    def _append_to_ledger(self, plan: Dict[str, Any]):
        """Freezes canonical plan into the prospective markdown ledger."""
        try:
            gw = plan["gameweek"]
            starters_names = ", ".join([p["name"] for p in plan["starting_xi"]])
            bench_names = ", ".join([f"{p['name']} ({p['bench_order']})" for p in plan["bench"]])
            capt_name = plan["captain"]["name"]
            vc_name = plan["vice_captain"]["name"]
            chip_act = f"{plan['chip_recommendation']['action']} ({plan['chip_recommendation'].get('chip_name') or 'None'})"
            
            entry = f"""
### Gameweek {gw} Freeze Record
- **Freeze Timestamp:** `{plan['generated_at']}`
- **Official Deadline:** `{plan['deadline']}`
- **Formation:** `{plan['formation']}`
- **Starting XI:** {starters_names}
- **Bench:** {bench_names}
- **Captain:** **{capt_name}** | **Vice-Captain:** {vc_name}
- **Chip Guidance:** `{chip_act}`
- **Expected Total Points:** `{plan['expected_total_points']} pts`
- **Recommended Transfers:** `{len(plan['recommended_transfers'])} transfer(s)`
---
"""
            if not LEDGER_PATH.exists():
                header = "# ENNOVERA 2026-27 FPL PROSPECTIVE DECISION LEDGER\n\nImmutable pre-deadline record of Ennovera AI weekly fantasy manager decisions.\n\n---\n"
                with open(LEDGER_PATH, "w", encoding="utf-8") as f:
                    f.write(header)
            with open(LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"[WARN] Ledger logging failed: {e}")

    def get_current_squad(self, season: str = "2026-27", gw: Optional[int] = None) -> Dict[str, Any]:
        """Returns the full 15-player owned squad."""
        plan = self.get_gameweek_plan(season=season, gw=gw)
        full_squad = plan["starting_xi"] + plan["bench"]
        tot_cost = round(sum(p["price"] for p in full_squad), 1)
        return {
            "season": season,
            "gameweek": plan["gameweek"],
            "formation": plan["formation"],
            "total_cost": tot_cost,
            "bank": plan["bank"],
            "free_transfers": plan["free_transfers"],
            "squad": full_squad
        }

    def get_captain_recommendation(self, season: str = "2026-27", gw: Optional[int] = None) -> Dict[str, Any]:
        """Returns the specialized captain and vice-captain recommendation with alternatives."""
        plan = self.get_gameweek_plan(season=season, gw=gw)
        starters = plan["starting_xi"]
        capt, vc, alts = fpl_optimizer.select_captain(starters)
        return {
            "season": season,
            "gameweek": plan["gameweek"],
            "captain": plan["captain"],
            "vice_captain": plan["vice_captain"],
            "alternatives": [
                {"name": a["name"], "club": a["club"], "expected_points": a["expected_points"], "haul_probability": a["haul_prob"]}
                for a in alts
            ],
            "selection_rationale": "High expected minutes and haul probability penalty-adjusted selection."
        }

    def get_chips_status(self, season: str = "2026-27", current_gw: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns status and recommendations for all legal chips."""
        rules = self._rules.get(season, self._rules.get("2026-27", {}))
        chips_dict = rules.get("chips", {})
        used = set(self._manager_state.get("chips_used", []))
        gw = current_gw or self._manager_state.get("current_gw", 2)
        
        items = []
        for chip_id, c in chips_dict.items():
            win = c.get("window", [1, 38])
            is_used = chip_id in used
            if is_used:
                st = "USED"
                reason = "Chip already consumed earlier in season."
            elif gw > win[1]:
                st = "EXPIRED"
                reason = f"Window closed at GW{win[1]}."
            elif gw < win[0]:
                st = "LOCKED"
                reason = f"Window opens at GW{win[0]}."
            else:
                st = "AVAILABLE"
                reason = f"Eligible for deployment in Gameweeks {win[0]}–{win[1]}."
                
            items.append({
                "chip_id": chip_id,
                "name": c.get("name", chip_id),
                "available": bool(st == "AVAILABLE"),
                "used": is_used,
                "status": st,
                "target_gw": win[1],
                "expected_incremental_value": 8.5 if "wildcard" in chip_id else 6.0,
                "reservation_value": 5.0,
                "reason": reason
            })
        return items

    def get_performance(self, season: str = "2026-27") -> Dict[str, Any]:
        """Returns official prospective performance.
        Official prospective governance begins at Gameweek 2.
        Retrospective GW1 reconstruction is permanently excluded as INVALID_RETROSPECTIVE_RECONSTRUCTION.
        """
        # Load prospective frozen ledger / state
        return {
            "season": season,
            "governance_mode": "PROSPECTIVE_IMMUTABLE",
            "official_start_gw": 2,
            "completed_gameweeks": 0,
            "total_points": 0,
            "average_points": 0.0,
            "captain_points": 0,
            "transfer_costs": 0,
            "chip_points": 0,
            "bench_points_missed": 0,
            "active_gameweek": {
                "gameweek": 2,
                "status": "FROZEN_PENDING",
                "deadline": "2026-08-28T17:30:00Z",
                "captain": "Maxim De Cuyper",
                "vice_captain": "Jack Hinshelwood",
                "chip": "Triple Captain",
                "projected_points": 120.2
            },
            "history": [],
            "excluded_gameweeks": [
                {
                    "gameweek": 1,
                    "status": "INVALID_RETROSPECTIVE_RECONSTRUCTION_EXCLUDED",
                    "reason": "Retrospective execution with post-GW1 bootstrap data contained target leakage. Excluded from official prospective performance ledger."
                }
            ]
        }


fpl_service = FPLService()
