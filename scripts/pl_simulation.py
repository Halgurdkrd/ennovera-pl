"""Monte Carlo simulation of the remaining PL 2026-27 season -> champion / top-4 / top-6 /
relegation probabilities + predicted table. Reads matches from Supabase (falls back to FPL+
model locally for --preview when no DB). Self-contained.

    python3 scripts/pl_simulation.py --preview   # print table (Supabase, or local fallback)
    python3 scripts/pl_simulation.py --insert     # write to pl_simulation_results
"""
import argparse, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv; load_dotenv()
import numpy as np
from team_aliases import canonicalize

COMPETITION = 'PL2026-27'


def _sb():
    from supabase import create_client
    return create_client(os.environ['SUPABASE_URL'], os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_KEY'])


def load_matches_supabase(sb) -> list[dict]:
    rows = (sb.table('matches').select(
        'home_team,away_team,status,home_score,away_score,home_win_probability,draw_probability,away_win_probability')
        .eq('competition', COMPETITION).execute().data) or []
    out = []
    for r in rows:
        fin = r['status'] == 'finished' and r.get('home_score') is not None
        p = [r.get('home_win_probability'), r.get('draw_probability'), r.get('away_win_probability')]
        p = [float(x) for x in p] if all(x is not None for x in p) else [0.40, 0.26, 0.34]
        out.append({'home': canonicalize(r['home_team']), 'away': canonicalize(r['away_team']),
                    'finished': fin, 'hs': r.get('home_score'), 'as': r.get('away_score'), 'probs': p})
    return out


def load_matches_local() -> list[dict]:
    """Fallback for --preview without a DB: FPL fixtures + V2 model predictions."""
    from populate_pl_matches import fixtures, load_model, predict, load_elo, load_form
    fx = fixtures(); calib, feats = load_model(); elo, form = load_elo(), load_form()
    out = []
    for f in fx:
        p = list(predict(calib, feats, f['home'], f['away'], elo, form))
        out.append({'home': f['home'], 'away': f['away'], 'finished': f['finished'] and f['hs'] is not None,
                    'hs': f['hs'], 'as': f['as'], 'probs': p})
    return out


def simulate(matches: list[dict], n: int = 10000) -> list[dict]:
    teams = sorted({t for m in matches for t in (m['home'], m['away'])})
    base_pts, base_gd = defaultdict(int), defaultdict(int)
    unplayed = []
    for m in matches:
        if m['finished'] and m['hs'] is not None:
            hs, as_ = int(m['hs']), int(m['as'])
            base_gd[m['home']] += hs - as_; base_gd[m['away']] += as_ - hs
            if hs > as_:   base_pts[m['home']] += 3
            elif as_ > hs: base_pts[m['away']] += 3
            else:          base_pts[m['home']] += 1; base_pts[m['away']] += 1
        else:
            p = np.array(m['probs'], float); p = p / p.sum()
            unplayed.append((m['home'], m['away'], p))
    champ = defaultdict(int); top4 = defaultdict(int); top6 = defaultdict(int); rel = defaultdict(int)
    spts = defaultdict(float); spos = defaultdict(float)
    rng = np.random.default_rng(13)
    for _ in range(n):
        pts = {t: base_pts[t] for t in teams}; gd = {t: base_gd[t] for t in teams}
        for home, away, p in unplayed:
            o = rng.choice(3, p=p)
            if o == 0:   pts[home] += 3; gd[home] += 1; gd[away] -= 1
            elif o == 2: pts[away] += 3; gd[away] += 1; gd[home] -= 1
            else:        pts[home] += 1; pts[away] += 1
        order = sorted(teams, key=lambda t: (-pts[t], -gd[t], rng.random()))
        champ[order[0]] += 1
        for t in order[:4]: top4[t] += 1
        for t in order[:6]: top6[t] += 1
        for t in order[-3:]: rel[t] += 1
        for pos, t in enumerate(order, 1):
            spts[t] += pts[t]; spos[t] += pos
    table = [{'team_name': t, 'champion_pct': round(champ[t] / n * 100, 1),
              'top4_pct': round(top4[t] / n * 100, 1), 'top6_pct': round(top6[t] / n * 100, 1),
              'relegation_pct': round(rel[t] / n * 100, 1), 'avg_points': round(spts[t] / n, 1),
              'avg_position': round(spos[t] / n, 1)} for t in teams]
    table.sort(key=lambda x: x['avg_position'])
    return table


def print_table(table):
    print(f"{'#':<4}{'Team':<26}{'Champ%':<9}{'Top4%':<8}{'Top6%':<8}{'Releg%':<8}{'AvgPts':<8}{'AvgPos'}")
    for i, r in enumerate(table, 1):
        print(f"{i:<4}{r['team_name']:<26}{r['champion_pct']:<9}{r['top4_pct']:<8}{r['top6_pct']:<8}"
              f"{r['relegation_pct']:<8}{r['avg_points']:<8}{r['avg_position']}")


def upsert_results(sb, table, n):
    for r in table:
        sb.table('pl_simulation_results').upsert({**r, 'competition': COMPETITION, 'simulations': n},
                                                 on_conflict='team_name,competition').execute()


def run_simulation(sb=None, n: int = 10000, insert: bool = False) -> list[dict]:
    """Pipeline entry point: read matches, simulate, optionally upsert. Returns the table."""
    sb = sb or _sb()
    table = simulate(load_matches_supabase(sb), n)
    if insert:
        upsert_results(sb, table, n)
    return table


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview', action='store_true')
    ap.add_argument('--insert', action='store_true'); ap.add_argument('-n', type=int, default=10000)
    a = ap.parse_args()
    if a.insert:
        table = run_simulation(n=a.n, insert=True); print_table(table)
        print(f"\nUpserted {len(table)} rows to pl_simulation_results (n={a.n})."); return
    # preview: try Supabase, else local fallback
    try:
        matches = load_matches_supabase(_sb()); src = 'Supabase'
    except Exception as e:
        matches = load_matches_local(); src = f'LOCAL fallback (no DB: {type(e).__name__})'
    table = simulate(matches, a.n)
    print(f"=== PL 2026-27 league simulation (n={a.n}, source: {src}) ===")
    print_table(table)
    print("\n(preview only — use --insert to write to Supabase.)")


if __name__ == '__main__':
    main()
