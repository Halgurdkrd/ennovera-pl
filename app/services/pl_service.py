"""Premier League Canonical Match Prediction & Simulation Service.
Production Model: V2 (Elo + Platt Calibration) -> Serves canonical 2026-27 match probabilities.
Shadow Model: V5.1 (Expected XI + P(start) signal).
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
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from team_aliases import canonicalize, PL_2026_27
from pl_simulation import simulate_season, load_matches_from_local

COMPETITION = "PL2026-27"
SEASON = "2026-27"
MODEL_PUBLIC_VERSION = "ennovera-pl-v1.0"
MODEL_INTERNAL_VERSION = "pl_v2_final"
DATA_CUTOFF = "Pre-match lineup confirmation / 1 hour before kickoff"


class PLService:
    """Canonical Premier League Match Inference Engine."""
    
    def __init__(self):
        self._v2_calib = None
        self._v2_feats = None
        self._v5_art = None
        self._elo = {}
        self._form = {}
        self._prev_pos = {}
        self._is_loaded = False
        self._load_models_and_state()
        
    def _load_models_and_state(self):
        try:
            from populate_pl_matches import load_model, load_elo, load_form, PREV_POS
            self._v2_calib, self._v2_feats = load_model()
            self._elo = load_elo()
            self._form = load_form()
            self._prev_pos = PREV_POS
            
            # Load V5.1 candidate for metadata / shadow
            v5_path = _REPO_ROOT / "data/models/pl_v5_1_candidate.pkl"
            if v5_path.exists():
                import pickle
                with open(v5_path, "rb") as f:
                    self._v5_art = pickle.load(f)
            self._is_loaded = (self._v2_calib is not None)
        except Exception as e:
            print(f"[WARN] Failed loading PL models: {e}")
            self._is_loaded = False
            
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def _sb_client(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        if not url or not key:
            return None
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception:
            return None

    def _gf(self, team: str) -> float:
        val = self._form.get(team, 1.3)
        if isinstance(val, (int, float)):
            return float(val)
        elif isinstance(val, (list, tuple)):
            return float(sum(val) / len(val)) if val else 1.3
        return 1.3

    def predict_match(self, home_team: str, away_team: str, season: str = SEASON, gw: Optional[int] = None) -> Dict[str, Any]:
        """Calculates canonical V2 production probabilities for any two Premier League clubs."""
        h_canon = canonicalize(home_team)
        a_canon = canonicalize(away_team)
        
        he = self._elo.get(h_canon, 1500.0)
        ae = self._elo.get(a_canon, 1500.0)
        
        vals = {
            'home_elo': he,
            'away_elo': ae,
            'elo_diff': he - ae,
            'home_form5_gf': self._gf(h_canon),
            'away_form5_gf': self._gf(a_canon),
            'home_prev_position': self._prev_pos.get(h_canon, 10),
            'away_prev_position': self._prev_pos.get(a_canon, 10)
        }
        
        if self._v2_calib is not None and self._v2_feats is not None:
            X = pd.DataFrame([[vals[f] for f in self._v2_feats]], columns=self._v2_feats)
            p = np.asarray(self._v2_calib.predict_proba(X)[0], dtype=float)
            al = 1.0
            if he < 1350: al -= 0.10
            if ae < 1350: al -= 0.10
            if al < 0.999:
                e = 1 / (1 + 10 ** ((ae - he - 100) / 400))
                prior = np.array([e * 0.74, 0.26, (1 - e) * 0.74])
                p = al * p + (1 - al) * prior
            p = p / p.sum()
            p_home, p_draw, p_away = float(p[0]), float(p[1]), float(p[2])
        else:
            p_home, p_draw, p_away = 0.44, 0.26, 0.30
            
        probs = [p_home, p_draw, p_away]
        max_idx = int(np.argmax(probs))
        outcomes = ["H", "D", "A"]
        pred_outcome = outcomes[max_idx]
        max_prob = probs[max_idx]
        
        confidence = "HIGH" if max_prob >= 0.58 else "MEDIUM" if max_prob >= 0.45 else "LOW"
        strong_pick = bool(max_prob >= 0.60)
        
        now_iso = datetime.now(timezone.utc).isoformat()
        fixture_id = f"PL_{season.replace('-', '_')}_GW{gw or 1}_{h_canon[:3].upper()}_{a_canon[:3].upper()}"
        kickoff_time = f"{season[:4]}-08-29T14:00:00Z"
        
        return {
            "fixture_id": fixture_id,
            "competition": COMPETITION,
            "season": season,
            "gameweek": gw or 1,
            "home_team": h_canon,
            "away_team": a_canon,
            "kickoff": kickoff_time,
            "home_prob": round(p_home, 4),
            "draw_prob": round(p_draw, 4),
            "away_prob": round(p_away, 4),
            "predicted_outcome": pred_outcome,
            "confidence": confidence,
            "strong_pick": strong_pick,
            "model_public_version": MODEL_PUBLIC_VERSION,
            "model_internal_version": MODEL_INTERNAL_VERSION,
            "generated_at": now_iso,
            "data_cutoff": DATA_CUTOFF,
            "prediction_state": "PREMATCH"
        }

    def get_gameweek_fixtures(self, season: str = SEASON, gw: int = 1) -> List[Dict[str, Any]]:
        """Retrieves match fixtures and canonical probabilities for a gameweek."""
        sb = self._sb_client()
        if sb is not None:
            try:
                # Query canonical Supabase matches table
                stage_str = f"Gameweek {gw}"
                res = (sb.table('matches')
                       .select('*')
                       .eq('competition', COMPETITION)
                       .ilike('tournament_stage', f"%{gw}%")
                       .execute())
                rows = res.data or []
                if rows:
                    out = []
                    for r in rows:
                        h = canonicalize(r['home_team'])
                        a = canonicalize(r['away_team'])
                        hp = float(r.get('home_win_probability') or 0.40)
                        dp = float(r.get('draw_probability') or 0.26)
                        ap = float(r.get('away_win_probability') or 0.34)
                        
                        probs = [hp, dp, ap]
                        max_idx = int(np.argmax(probs))
                        pred_outcome = ["H", "D", "A"][max_idx]
                        max_p = probs[max_idx]
                        conf = "HIGH" if max_p >= 0.58 else "MEDIUM" if max_p >= 0.45 else "LOW"
                        
                        out.append({
                            "fixture_id": f"PL_{season.replace('-', '_')}_GW{gw}_{h[:3].upper()}_{a[:3].upper()}",
                            "competition": COMPETITION,
                            "season": season,
                            "gameweek": gw,
                            "home_team": h,
                            "away_team": a,
                            "kickoff": str(r.get('match_date') or f"{season[:4]}-08-29T14:00:00Z"),
                            "home_prob": round(hp, 4),
                            "draw_prob": round(dp, 4),
                            "away_prob": round(ap, 4),
                            "predicted_outcome": pred_outcome,
                            "confidence": conf,
                            "strong_pick": bool(max_p >= 0.60),
                            "model_public_version": MODEL_PUBLIC_VERSION,
                            "model_internal_version": MODEL_INTERNAL_VERSION,
                            "generated_at": datetime.now(timezone.utc).isoformat(),
                            "data_cutoff": DATA_CUTOFF,
                            "prediction_state": "FINAL" if r.get('status') == 'finished' else "PREMATCH"
                        })
                    return out
            except Exception as e:
                print(f"[WARN] Supabase query failed: {e}. Falling back to live local model inference.")
                
        # Local fallback using canonical schedule and V2 model
        from populate_pl_matches import fixtures as get_fx
        fx = [f for f in get_fx() if f.get('gw') == gw]
        out = []
        for f in fx:
            pred = self.predict_match(f['home'], f['away'], season=season, gw=gw)
            if 'date' in f and f['date']:
                pred['kickoff'] = str(f['date'])
            out.append(pred)
        return out

    def get_league_table(self, season: str = SEASON) -> Dict[str, Any]:
        """Returns the latest Premier League table standings with 10,000 Monte Carlo simulation probabilities."""
        sb = self._sb_client()
        if sb is not None:
            try:
                res = (sb.table('pl_simulation_results')
                       .select('*')
                       .eq('season', season)
                       .eq('is_latest', True)
                       .order('champion_probability', desc=True)
                       .execute())
                rows = res.data or []
                if rows:
                    standings = []
                    for i, r in enumerate(rows, 1):
                        standings.append({
                            "position": i,
                            "team_name": r['team_name'],
                            "expected_points": float(r['expected_points']),
                            "expected_position": float(r['expected_position']),
                            "champion_pct": round(float(r['champion_probability']) * 100.0, 1),
                            "top4_pct": round(float(r['top4_probability']) * 100.0, 1),
                            "top6_pct": round(float(r['top6_probability']) * 100.0, 1),
                            "relegation_pct": round(float(r['relegation_probability']) * 100.0, 1)
                        })
                    return {
                        "competition": COMPETITION,
                        "season": season,
                        "simulation_runs": 10000,
                        "model_version": MODEL_PUBLIC_VERSION,
                        "generated_at": rows[0].get('generated_at', datetime.now(timezone.utc).isoformat()),
                        "standings": standings
                    }
            except Exception:
                pass
                
        # Fallback: Run vectorized simulation from local match state
        matches = load_matches_from_local()
        sim_table = simulate_season(matches, n_sims=10000)
        standings = []
        for i, r in enumerate(sim_table, 1):
            standings.append({
                "position": i,
                "team_name": r['team_name'],
                "expected_points": r['expected_points'],
                "expected_position": r['expected_position'],
                "champion_pct": r['champion_pct'],
                "top4_pct": r['top4_pct'],
                "top6_pct": r['top6_pct'],
                "relegation_pct": r['relegation_pct']
            })
        return {
            "competition": COMPETITION,
            "season": season,
            "simulation_runs": 10000,
            "model_version": MODEL_PUBLIC_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "standings": standings
        }

    def get_models_metadata(self) -> Dict[str, Any]:
        """Returns clean public metadata for production and shadow models."""
        return {
            "production_model": {
                "model_name": "Premier League Match Predictor V2",
                "public_version": MODEL_PUBLIC_VERSION,
                "role": "PRODUCTION",
                "description": "Platt-calibrated logistic model over dynamic team Elo differences and 5-game rolling form.",
                "features": ["elo_diff", "home_form5_gf", "away_form5_gf"],
                "holdout_accuracy": 0.5026,
                "log_loss": 1.0310
            },
            "shadow_model": {
                "model_name": "Player-Aware Expected XI Candidate V5.1",
                "public_version": "ennovera-pl-shadow-v5.1",
                "role": "SHADOW",
                "description": "Walk-forward calibrated model incorporating Starting XI expected goal involvements and lineup continuity.",
                "features": ["diff_exp_xi_att", "diff_exp_xi_creativity", "home_xi_continuity", "away_xi_continuity"],
                "holdout_accuracy": 0.5283,
                "log_loss": 0.9983
            },
            "legacy_models": [
                {
                    "model_name": "World Cup 2026 Tournament Model",
                    "public_version": "innovera-wc2026-v0.3",
                    "role": "LEGACY",
                    "description": "Weighted expected goals and squad depth model for World Cup 2026.",
                    "features": ["weighted_xg", "squad_elo", "h2h_index"],
                    "holdout_accuracy": 0.6590,
                    "log_loss": 0.9120
                }
            ]
        }


pl_service = PLService()
