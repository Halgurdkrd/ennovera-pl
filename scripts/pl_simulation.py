"""Premier League 2026-27 Vectorized Monte Carlo Simulation Engine.
Computes 10,000 season completions using canonical match outcome probabilities.
Outputs: Champion %, Top-4 %, Top-6 %, Relegation %, Expected Points, Expected Position.
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from collections import defaultdict
import numpy as np

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize, PL_2026_27

COMPETITION = 'PL2026-27'
SEASON = '2026-27'


def _get_supabase_client():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


def load_matches_from_supabase(sb=None) -> list[dict]:
    """Loads all 380 fixtures from Supabase matches table."""
    sb = sb or _get_supabase_client()
    if sb is None:
        return load_matches_from_local()
    
    try:
        res = (sb.table('matches')
               .select('match_id,home_team,away_team,tournament_stage,status,home_score,away_score,home_win_probability,draw_probability,away_win_probability')
               .eq('competition', COMPETITION)
               .execute())
        rows = res.data or []
        if not rows:
            return load_matches_from_local()
        
        matches = []
        for r in rows:
            fin = (r.get('status') == 'finished' and r.get('home_score') is not None and r.get('away_score') is not None)
            hp = r.get('home_win_probability')
            dp = r.get('draw_probability')
            ap = r.get('away_win_probability')
            probs = [float(hp), float(dp), float(ap)] if (hp is not None and dp is not None and ap is not None) else [0.40, 0.26, 0.34]
            matches.append({
                'match_id': r.get('match_id'),
                'home': canonicalize(r['home_team']),
                'away': canonicalize(r['away_team']),
                'stage': r.get('tournament_stage') or 'Gameweek 1',
                'finished': fin,
                'hs': int(r['home_score']) if fin else None,
                'as': int(r['away_score']) if fin else None,
                'probs': probs
            })
        return matches
    except Exception as e:
        print(f"[WARN] Supabase match fetch failed: {e}. Falling back to local fixtures.")
        return load_matches_from_local()


def load_matches_from_local() -> list[dict]:
    """Fallback local fixture loader using V2 model."""
    from populate_pl_matches import fixtures, load_model, predict, load_elo, load_form
    fx = fixtures()
    calib, feats = load_model()
    elo, form = load_elo(), load_form()
    matches = []
    for f in fx:
        p = list(predict(calib, feats, f['home'], f['away'], elo, form))
        matches.append({
            'match_id': None,
            'home': f['home'],
            'away': f['away'],
            'stage': f"Gameweek {f.get('gw', 1)}",
            'finished': bool(f.get('finished') and f.get('hs') is not None),
            'hs': f.get('hs'),
            'as': f.get('as'),
            'probs': p
        })
    return matches


def simulate_season(matches: list[dict], n_sims: int = 10000, seed: int = 42) -> list[dict]:
    """Vectorized Monte Carlo season simulation."""
    teams = sorted(list(set(PL_2026_27).union({m['home'] for m in matches}).union({m['away'] for m in matches})))
    team_idx_map = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    
    base_pts = np.zeros(n_teams, dtype=np.int32)
    base_gd = np.zeros(n_teams, dtype=np.int32)
    base_gf = np.zeros(n_teams, dtype=np.int32)
    
    unplayed_h = []
    unplayed_a = []
    unplayed_probs = []
    
    for m in matches:
        h_idx = team_idx_map[m['home']]
        a_idx = team_idx_map[m['away']]
        if m['finished'] and m['hs'] is not None and m['as'] is not None:
            hs, as_ = m['hs'], m['as']
            base_gd[h_idx] += (hs - as_)
            base_gd[a_idx] += (as_ - hs)
            base_gf[h_idx] += hs
            base_gf[a_idx] += as_
            if hs > as_:
                base_pts[h_idx] += 3
            elif as_ > hs:
                base_pts[a_idx] += 3
            else:
                base_pts[h_idx] += 1
                base_pts[a_idx] += 1
        else:
            p = np.array(m['probs'], dtype=float)
            p = np.clip(p, 1e-6, 1.0)
            p = p / p.sum()
            unplayed_h.append(h_idx)
            unplayed_a.append(a_idx)
            unplayed_probs.append(p)
    
    n_unplayed = len(unplayed_h)
    
    if n_unplayed > 0:
        rng = np.random.default_rng(seed)
        unplayed_probs = np.array(unplayed_probs) # (n_unplayed, 3)
        cum_h = unplayed_probs[:, 0]
        cum_hd = unplayed_probs[:, 0] + unplayed_probs[:, 1]
        
        # Sample random floats for (n_sims, n_unplayed)
        r = rng.random((n_sims, n_unplayed))
        h_win = (r < cum_h)
        draw = (r >= cum_h) & (r < cum_hd)
        a_win = (r >= cum_hd)
        
        sim_pts = np.tile(base_pts, (n_sims, 1))
        sim_gd = np.tile(base_gd, (n_sims, 1))
        
        h_arr = np.array(unplayed_h)
        a_arr = np.array(unplayed_a)
        
        np.add.at(sim_pts, (slice(None), h_arr), h_win * 3 + draw * 1)
        np.add.at(sim_pts, (slice(None), a_arr), a_win * 3 + draw * 1)
        np.add.at(sim_gd, (slice(None), h_arr), h_win * 1 - a_win * 1)
        np.add.at(sim_gd, (slice(None), a_arr), a_win * 1 - h_win * 1)
    else:
        sim_pts = np.tile(base_pts, (n_sims, 1))
        sim_gd = np.tile(base_gd, (n_sims, 1))
        rng = np.random.default_rng(seed)
    
    # Sort order per simulation
    # Primary: points desc, Secondary: GD desc, Tiebreak: random uniform noise
    tiebreak_noise = rng.random((n_sims, n_teams)) * 0.001
    rank_metric = (sim_pts.astype(np.float64) * 1000.0) + sim_gd.astype(np.float64) + tiebreak_noise
    ranks = np.argsort(-rank_metric, axis=1) # ranks[s, 0] is the champion index
    
    champ_counts = np.bincount(ranks[:, 0], minlength=n_teams)
    top4_counts = np.bincount(ranks[:, :4].ravel(), minlength=n_teams)
    top6_counts = np.bincount(ranks[:, :6].ravel(), minlength=n_teams)
    releg_counts = np.bincount(ranks[:, -3:].ravel(), minlength=n_teams)
    
    pos_matrix = np.zeros((n_sims, n_teams), dtype=np.int32)
    for pos in range(n_teams):
        team_indices = ranks[:, pos]
        pos_matrix[np.arange(n_sims), team_indices] = pos + 1
    
    avg_pos = pos_matrix.mean(axis=0)
    avg_pts = sim_pts.mean(axis=0)
    
    table = []
    for i, t in enumerate(teams):
        table.append({
            'team_name': t,
            'champion_pct': round(float(champ_counts[i] / n_sims * 100.0), 1),
            'top4_pct': round(float(top4_counts[i] / n_sims * 100.0), 1),
            'top6_pct': round(float(top6_counts[i] / n_sims * 100.0), 1),
            'relegation_pct': round(float(releg_counts[i] / n_sims * 100.0), 1),
            'champion_prob': round(float(champ_counts[i] / n_sims), 4),
            'top4_prob': round(float(top4_counts[i] / n_sims), 4),
            'top6_prob': round(float(top6_counts[i] / n_sims), 4),
            'relegation_prob': round(float(releg_counts[i] / n_sims), 4),
            'expected_points': round(float(avg_pts[i]), 1),
            'expected_position': round(float(avg_pos[i]), 1)
        })
    
    table.sort(key=lambda x: (x['expected_position'], -x['champion_prob']))
    return table


def run_simulation(sb=None, n_sims: int = 10000, gameweek: int = 1, insert: bool = False) -> list[dict]:
    """Runs simulation and optionally writes snapshot to pl_simulation_results."""
    sb = sb or _get_supabase_client()
    matches = load_matches_from_supabase(sb)
    table = simulate_season(matches, n_sims=n_sims)
    
    if insert and sb is not None:
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            # Mark previous snapshots as is_latest = False
            sb.table('pl_simulation_results').update({'is_latest': False}).eq('season', SEASON).execute()
        except Exception:
            pass
        
        insert_rows = []
        for r in table:
            insert_rows.append({
                'competition': COMPETITION,
                'season': SEASON,
                'gameweek': gameweek,
                'team_name': r['team_name'],
                'champion_probability': r['champion_prob'],
                'top4_probability': r['top4_prob'],
                'top6_probability': r['top6_prob'],
                'relegation_probability': r['relegation_prob'],
                'expected_points': r['expected_points'],
                'expected_position': r['expected_position'],
                'simulation_runs': n_sims,
                'production_model_version': 'ennovera-pl-v1.0',
                'simulation_version': 'mc_10k_v1.0',
                'generated_at': now_iso,
                'data_cutoff': now_iso,
                'is_latest': True
            })
        try:
            sb.table('pl_simulation_results').insert(insert_rows).execute()
            print(f"[SIM] Successfully wrote {len(insert_rows)} rows to pl_simulation_results.")
        except Exception as e:
            print(f"[SIM ERROR] Failed to write simulation results to Supabase: {e}")
            
    return table


def print_table(table: list[dict]):
    print(f"\n{'#':<4}{'Team':<26}{'Champ%':<9}{'Top4%':<8}{'Top6%':<8}{'Releg%':<8}{'ExpPts':<8}{'ExpPos'}")
    print("-" * 78)
    for i, r in enumerate(table, 1):
        print(f"{i:<4}{r['team_name']:<26}{r['champion_pct']:<9}{r['top4_pct']:<8}{r['top6_pct']:<8}"
              f"{r['relegation_pct']:<8}{r['expected_points']:<8}{r['expected_position']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--sims', type=int, default=10000)
    parser.add_argument('--insert', action='store_true')
    parser.add_argument('--gw', type=int, default=1)
    args = parser.parse_args()
    
    t = run_simulation(n_sims=args.sims, gameweek=args.gw, insert=args.insert)
    print_table(t)
