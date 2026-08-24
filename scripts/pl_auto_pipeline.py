"""PL 2026-27 auto-pipeline — run every 30 min. Self-contained (no WC2026 app services).
One run: fetch FPL results -> update matches -> score user predictions -> update Elo/form
(persisted to JSON) -> re-predict scheduled matches. Idempotent.

    python3 scripts/pl_auto_pipeline.py            # full run (needs .env Supabase creds)
    python3 scripts/pl_auto_pipeline.py --dry-run  # FPL + local re-predict, NO DB writes
"""
import argparse, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv; load_dotenv()
import numpy as np, pandas as pd
from populate_pl_matches import fixtures, load_model, PREV_POS
from team_aliases import canonicalize

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELO_JSON = os.path.join(_ROOT, 'data/processed/current_elo.json')
FORM_JSON = os.path.join(_ROOT, 'data/processed/current_form.json')
COMPETITION, K, HFA, DEFAULT_GF = 'PL2026-27', 20, 100, 1.3


def load_state():
    elo = json.load(open(ELO_JSON)) if os.path.exists(ELO_JSON) else {}
    form = json.load(open(FORM_JSON)) if os.path.exists(FORM_JSON) else {}
    return {canonicalize(k): float(v) for k, v in elo.items()}, {canonicalize(k): list(v) for k, v in form.items()}


def save_state(elo, form):
    json.dump({k: round(v, 1) for k, v in elo.items()}, open(ELO_JSON, 'w'), indent=1)
    json.dump(form, open(FORM_JSON, 'w'), indent=1)


def _gf(form, t):
    l = form.get(t, []); return sum(l) / len(l) if l else DEFAULT_GF


def predict(calib, feats, home, away, elo, form):
    he = elo.get(home, 1500.0); ae = elo.get(away, 1500.0)
    vals = {'home_elo': he, 'away_elo': ae, 'elo_diff': he - ae, 'home_form5_gf': _gf(form, home),
            'away_form5_gf': _gf(form, away), 'home_prev_position': PREV_POS.get(home, 10),
            'away_prev_position': PREV_POS.get(away, 10)}
    X = pd.DataFrame([[vals[f] for f in feats]], columns=feats)
    p = np.asarray(calib.predict_proba(X)[0], dtype=float)
    al = 1.0
    if he < 1350: al -= 0.10
    if ae < 1350: al -= 0.10
    if al < 0.999:
        e = 1 / (1 + 10 ** ((ae - he - HFA) / 400)); prior = np.array([e * 0.74, 0.26, (1 - e) * 0.74])
        p = al * p + (1 - al) * prior
    p = p / p.sum(); return float(p[0]), float(p[1]), float(p[2])


def apply_result(elo, form, h, a, hg, ag):
    he = elo.get(h, 1500.0); ae = elo.get(a, 1500.0)
    sh = 1.0 if hg > ag else 0.5 if hg == ag else 0.0
    e_home = 1 / (1 + 10 ** ((ae - he - HFA) / 400))
    elo[h] = he + K * (sh - e_home); elo[a] = ae + K * ((1 - sh) - (1 - e_home))
    form[h] = (form.get(h, []) + [hg])[-5:]; form[a] = (form.get(a, []) + [ag])[-5:]


def _sb():
    from supabase import create_client
    return create_client(os.environ['SUPABASE_URL'], os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_KEY'])


def score_prediction(pred: dict, hg: int, ag: int) -> tuple[int, bool]:
    """3 pts correct winner, 5 pts exact score, 0 wrong. Handles score- or winner-based rows."""
    actual = 'H' if hg > ag else 'A' if ag > hg else 'D'
    phs, pas = pred.get('predicted_home_score'), pred.get('predicted_away_score')
    if phs is not None and pas is not None:
        if int(phs) == hg and int(pas) == ag:
            return 5, True
        pw = 'H' if phs > pas else 'A' if pas > phs else 'D'
        return (3, True) if pw == actual else (0, False)
    pw = (pred.get('predicted_winner') or '').upper()[:1]
    pw = {'H': 'H', 'D': 'D', 'A': 'A'}.get(pw, pw)
    return (3, True) if pw == actual else (0, False)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    fx = fixtures(); calib, feats = load_model(); elo, form = load_state()
    fpl_finished = {(f['home'], f['away']): (f['hs'], f['as']) for f in fx
                    if f['finished'] and f['hs'] is not None}

    if a.dry_run:
        print(f"[DRY RUN] FPL fixtures {len(fx)} | finished {len(fpl_finished)} | state teams {len(elo)}")
        print("Newly-finished would be scored/applied (vs Supabase 'scheduled'); showing FPL-finished:")
        for (h, a_), (hs, as_) in list(fpl_finished.items())[:10]:
            print(f"  {h} {hs}-{as_} {a_}")
        print("\nRe-predictions for not-yet-finished fixtures (GW2 sample), using current state:")
        for f in [f for f in fx if f['gw'] == 2]:
            hw, d, aw = predict(calib, feats, f['home'], f['away'], elo, form)
            print(f"  {f['home']:<22} vs {f['away']:<22} {hw*100:4.0f}/{d*100:4.0f}/{aw*100:4.0f}")
        print("\n(dry run — no Supabase writes, state not saved.)"); return

    sb = _sb()
    # STEP 1-2: matches scheduled in DB but finished in FPL -> update
    scheduled = (sb.table('matches').select('match_id,home_team,away_team')
                 .eq('competition', COMPETITION).eq('status', 'scheduled').execute().data) or []
    new_results = []
    for r in scheduled:
        key = (r['home_team'], r['away_team'])
        if key in fpl_finished:
            hs, as_ = fpl_finished[key]
            sb.table('matches').update({'status': 'finished', 'home_score': hs, 'away_score': as_}) \
                .eq('match_id', r['match_id']).execute()
            new_results.append((r['home_team'], r['away_team'], hs, as_, r['match_id']))
    # STEP 3: score user predictions for the newly-finished matches
    scored = 0
    for h, a_, hs, as_, mid in new_results:
        ups = (sb.table('user_predictions').select('*').eq('match_id', mid).execute().data) or []
        for up in ups:
            pts, ok = score_prediction(up, hs, as_)
            sb.table('user_predictions').update({'points_earned': pts, 'is_correct': ok}) \
                .eq('id', up.get('id')).execute() if up.get('id') else None
            scored += 1
    # STEP 4-5: Elo + form updates
    for h, a_, hs, as_, _ in new_results:
        apply_result(elo, form, h, a_, hs, as_)
    # STEP 6: re-predict remaining scheduled with updated state
    remaining = (sb.table('matches').select('match_id,home_team,away_team')
                 .eq('competition', COMPETITION).neq('status', 'finished').execute().data) or []
    for r in remaining:
        hw, d, aw = predict(calib, feats, r['home_team'], r['away_team'], elo, form)
        sb.table('matches').update({'home_win_probability': round(hw, 4), 'draw_probability': round(d, 4),
                                    'away_win_probability': round(aw, 4)}).eq('match_id', r['match_id']).execute()
    save_state(elo, form)
    # STEP 8: league-table simulation — only when new results changed the table
    sim_info = 'skipped (no new results)'
    if new_results:
        try:
            from pl_simulation import run_simulation
            n_sim = int(os.getenv('PL_SIM_N', '10000'))
            table = run_simulation(sb=sb, n=n_sim, insert=True)
            sim_info = f'{len(table)} teams (n={n_sim})'
        except Exception as exc:
            sim_info = f'failed: {exc}'
    # STEP 7: summary
    print(f"New results: {len(new_results)} | user predictions scored: {scored} | "
          f"Elo teams updated: {len(set(t for r in new_results for t in r[:2]))} | "
          f"predictions refreshed: {len(remaining)} | simulation: {sim_info}")


if __name__ == '__main__':
    main()
