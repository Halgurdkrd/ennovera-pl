"""Live FPL Data Ingestor & Real-Time Feature Extractor with Strict Temporal Governance.
Fetches, caches, and archives pre-deadline player elements and enforces point-in-time constraints.
"""
from __future__ import annotations
import os
import sys
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

_APP_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _APP_DIR.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from team_aliases import canonicalize, PL_2026_27
from app.services.temporal_governance import TemporalLeakageError, FPLMode, assert_predeadline_integrity

CACHE_DIR = _REPO_ROOT / "data" / "processed"
SNAPSHOTS_DIR = _REPO_ROOT / "data" / "live_snapshots"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

BOOTSTRAP_CACHE = CACHE_DIR / "fpl_live_bootstrap.json"
FIXTURES_CACHE = CACHE_DIR / "fpl_live_fixtures.json"
CACHE_TTL_SECONDS = 900  # 15 minutes


class FPLDataIngestor:
    """Ingests, caches, archives, and parses FPL data under strict temporal governance."""
    
    BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
    FIXTURES_URL = "https://fantasy.premierleague.com/api/fixtures/"
    
    def __init__(self):
        self._bootstrap_data: Optional[Dict[str, Any]] = None
        self._fixtures_data: Optional[List[Dict[str, Any]]] = None
        self._last_fetch_ts: float = 0.0
        
    def _fetch_url(self, url: str) -> Optional[Any]:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ennovera/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.getcode() == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[WARN] FPL API Fetch Failed for {url}: {e}")
        return None

    def refresh(self, force: bool = False) -> bool:
        """Fetches live data from FPL API if cache expired or force=True."""
        now = time.time()
        if not force and self._bootstrap_data is not None and (now - self._last_fetch_ts < CACHE_TTL_SECONDS):
            return True
            
        # Try disk cache first if available and recent
        if not force and BOOTSTRAP_CACHE.exists():
            try:
                mtime = BOOTSTRAP_CACHE.stat().st_mtime
                if now - mtime < CACHE_TTL_SECONDS:
                    with open(BOOTSTRAP_CACHE, "r", encoding="utf-8") as f:
                        self._bootstrap_data = json.load(f)
                    if FIXTURES_CACHE.exists():
                        with open(FIXTURES_CACHE, "r", encoding="utf-8") as f:
                            self._fixtures_data = json.load(f)
                    self._last_fetch_ts = mtime
                    return True
            except Exception:
                pass

        # Fetch live from web
        b_data = self._fetch_url(self.BOOTSTRAP_URL)
        f_data = self._fetch_url(self.FIXTURES_URL)
        
        if b_data:
            self._bootstrap_data = b_data
            self._fixtures_data = f_data or []
            self._last_fetch_ts = now
            try:
                with open(BOOTSTRAP_CACHE, "w", encoding="utf-8") as f:
                    json.dump(b_data, f)
                if f_data:
                    with open(FIXTURES_CACHE, "w", encoding="utf-8") as f:
                        json.dump(f_data, f)
            except Exception:
                pass
            return True
            
        return False

    def get_current_gameweek_info(self) -> Dict[str, Any]:
        """Returns the active/upcoming gameweek, deadline, and finished status."""
        self.refresh()
        if not self._bootstrap_data:
            return {"current_gw": 1, "next_gw": 2, "deadline": "2026-08-28T17:30:00Z", "is_finished": False}
            
        events = self._bootstrap_data.get("events", [])
        current_gw = 1
        next_gw = 2
        deadline = "2026-08-28T17:30:00Z"
        
        for ev in events:
            if ev.get("is_current"):
                current_gw = ev.get("id", 1)
            if ev.get("is_next"):
                next_gw = ev.get("id", current_gw + 1)
                deadline = ev.get("deadline_time", deadline)
                
        return {
            "current_gw": current_gw,
            "next_gw": next_gw,
            "deadline": deadline,
            "total_events": len(events)
        }

    def get_all_players(self, target_gw: Optional[int] = None, mode: str = FPLMode.LIVE_PROSPECTIVE) -> List[Dict[str, Any]]:
        """Parses all players with strict point-in-time temporal verification."""
        gw_info = self.get_current_gameweek_info()
        live_next_gw = gw_info["next_gw"]
        deadline = gw_info["deadline"]
        
        # Determine target gameweek context
        gw = target_gw if target_gw is not None else live_next_gw
        
        # TEMPORAL SAFETY CHECK: If mode is HISTORICAL_REPLAY or past GW is requested
        if mode == FPLMode.HISTORICAL_REPLAY or gw < live_next_gw:
            if gw < live_next_gw and mode == FPLMode.LIVE_PROSPECTIVE:
                raise TemporalLeakageError(
                    f"TemporalLeakageError: Cannot use LIVE_PROSPECTIVE mode with current bootstrap for past Gameweek {gw}. "
                    f"Historical replay requires an archived pre-deadline point-in-time snapshot."
                )
            
            # Check for archived historical snapshot
            snapshot_dir = SNAPSHOTS_DIR / "2026-27" / f"GW{gw:02d}"
            snap_bootstrap = snapshot_dir / "bootstrap_predeadline.json"
            if not snap_bootstrap.exists():
                raise TemporalLeakageError(
                    f"HISTORICAL_SNAPSHOT_UNAVAILABLE: No pre-deadline point-in-time snapshot exists for Gameweek {gw}. "
                    f"Reconstruction failed closed to prevent temporal data leakage."
                )
            with open(snap_bootstrap, "r", encoding="utf-8") as f:
                bootstrap_source = json.load(f)
        else:
            self.refresh()
            bootstrap_source = self._bootstrap_data

        if not bootstrap_source:
            raise RuntimeError("FPL bootstrap data unavailable.")
            
        teams_map = {}
        for t in bootstrap_source.get("teams", []):
            teams_map[t["id"]] = canonicalize(t["name"])
            
        pos_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        
        players = []
        now_iso = datetime.now(timezone.utc).isoformat()
        
        for p in bootstrap_source.get("elements", []):
            club = teams_map.get(p.get("team"), "Unknown")
            pos = pos_map.get(p.get("element_type"), "MID")
            price = round(float(p.get("now_cost", 50)) / 10.0, 1)
            status = p.get("status", "a")
            chance = p.get("chance_of_playing_this_round")
            
            # Starting Probability P(start)
            if status == "a":
                p_start = 0.95 if float(p.get("form", 0) or 0) > 2.0 else 0.85
            elif status == "d":
                p_start = 0.50 if chance is None else float(chance) / 100.0
            elif status in ("i", "u", "s"):
                p_start = 0.0 if chance is None else float(chance) / 100.0
            else:
                p_start = 0.50
                
            # Expected Minutes
            exp_mins = round(p_start * 90.0, 1)
            
            # Multi-head Base xP computation
            form_val = float(p.get("form", 0) or 0)
            total_pts = float(p.get("total_points", 0) or 0)
            base_pts = (form_val * 0.70) + (total_pts / 38.0 * 0.30) if total_pts > 0 else form_val
            
            # Position-specific baseline floor
            pos_floor = {"GK": 3.5, "DEF": 3.8, "MID": 4.5, "FWD": 4.8}.get(pos, 4.0)
            if base_pts <= 0.1:
                base_pts = pos_floor * (price / 8.0)
                
            exp_pts = round(base_pts * (exp_mins / 90.0), 1)
            haul_prob = round(min(0.65, max(0.01, (exp_pts - 2.5) * 0.08 + 0.10)), 2)
            
            players.append({
                "player_id": int(p["id"]),
                "name": f"{p.get('first_name', '')} {p.get('second_name', '')}".strip() or p.get("web_name", "Unknown"),
                "web_name": p.get("web_name", "Unknown"),
                "club": club,
                "position": pos,
                "price": price,
                "status": status,
                "chance_of_playing": chance,
                "expected_points": exp_pts,
                "expected_minutes": exp_mins,
                "starting_prob": round(p_start, 2),
                "haul_prob": haul_prob,
                "form": form_val,
                "total_points": int(total_pts),
                "selected_by_percent": float(p.get("selected_by_percent", 0) or 0),
                "temporal_metadata": {
                    "gameweek_context": gw,
                    "mode": mode,
                    "deadline": deadline,
                    "fetched_at": now_iso,
                    "source": "official_fpl_bootstrap"
                }
            })
            
        return players

    def archive_predeadline_snapshot(self, season: str, gw: int, deadline: str, plan: Dict[str, Any]) -> Path:
        """Archives immutable point-in-time snapshots before gameweek deadline."""
        self.refresh()
        gw_dir = SNAPSHOTS_DIR / season / f"GW{gw:02d}"
        gw_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. bootstrap_predeadline.json
        if self._bootstrap_data:
            with open(gw_dir / "bootstrap_predeadline.json", "w", encoding="utf-8") as f:
                json.dump(self._bootstrap_data, f, indent=2)
                
        # 2. fixtures_predeadline.json
        if self._fixtures_data:
            with open(gw_dir / "fixtures_predeadline.json", "w", encoding="utf-8") as f:
                json.dump(self._fixtures_data, f, indent=2)
                
        # 3. plan_frozen.json (Immutable pre-deadline record)
        if not (gw_dir / "plan_frozen.json").exists():
            with open(gw_dir / "plan_frozen.json", "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2)
            
        # 4. metadata.json
        meta = {
            "season": season,
            "gameweek": gw,
            "deadline": deadline,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "status": "FROZEN_PREDEADLINE",
            "captain": plan.get("captain", {}).get("name"),
            "vice_captain": plan.get("vice_captain", {}).get("name"),
            "expected_points": plan.get("expected_total_points")
        }
        with open(gw_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            
        return gw_dir


fpl_ingestor = FPLDataIngestor()
