"""Populate PL 2026-27 fixtures into Supabase (competition='PL2026-27') and write V2
predictions to every scheduled match. Self-contained (uses this repo's model + aliases).

    python3 scripts/populate_pl_matches.py --preview   # FPL fetch + local predictions, NO DB
    python3 scripts/populate_pl_matches.py --insert     # insert fixtures + write predictions

Needs SUPABASE_URL + SUPABASE_SERVICE_KEY (or SUPABASE_KEY) in .env for --insert.
"""
import argparse, os, sys, uuid, json, pickle
import urllib.request
from collections import defaultdict, deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv; load_dotenv()
import numpy as np, pandas as pd
from team_aliases import canonicalize

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(_ROOT, 'data/models/pl_v2_final.pkl')
CURRENT_ELO = os.path.join(_ROOT, 'data/processed/current_elo.csv')   # latest Elo per team (finalised club_elo_derived)
PL_FEATURES = os.path.join(_ROOT, 'data/processed/pl_features.csv')
COMPETITION = 'PL2026-27'
FPL_FIX = 'https://fantasy.premierleague.com/api/fixtures/'
FPL_BS = 'https://fantasy.premierleague.com/api/bootstrap-static/'
HFA = 100
DEFAULT_GF = 1.3   # league-average goals/game for cold-start form

# 2025-26 final standings (user-specified; promoted teams 18-20), canonicalised
PREV_POS = {canonicalize(k): v for k, v in {
    'Arsenal':1,'Man City':2,'Liverpool':3,'Chelsea':4,'Aston Villa':5,'Newcastle':6,'Man Utd':7,'Bournemouth':8,
    'Brighton':9,'Brentford':10,'Crystal Palace':11,"Nott'm Forest":12,'Fulham':13,'Everton':14,'Tottenham':15,
    'Leeds':16,'Ipswich':17,'Sunderland':18,'Coventry City':19,'Hull City':20}.items()}


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def load_elo():
    cur = pd.read_csv(CURRENT_ELO)
    return {canonicalize(r['team']): float(r['derived_elo']) for _, r in cur.iterrows()}


def load_form():
    """Each team's last-5 goals-for from 2025-26 (fallback DEFAULT_GF for promoted/unseen)."""
    df = pd.read_csv(PL_FEATURES); d = df[df['season'] == '2025-26'].sort_values('date')
    dq = defaultdict(lambda: deque(maxlen=5))
    for r in d.itertuples():
        dq[canonicalize(r.home)].append(r.fthg); dq[canonicalize(r.away)].append(r.ftag)
    return {t: (sum(v) / len(v) if v else DEFAULT_GF) for t, v in dq.items()}


def load_model():
    d = pickle.load(open(MODEL, 'rb'))
    return d['calibrator'], d['features']


def build_features(home, away, elo, form, feats):
    he = elo.get(home, 1500.0); ae = elo.get(away, 1500.0)
    vals = {'home_elo': he, 'away_elo': ae, 'elo_diff': he - ae,
            'home_form5_gf': form.get(home, DEFAULT_GF), 'away_form5_gf': form.get(away, DEFAULT_GF),
            'home_prev_position': PREV_POS.get(home, 10), 'away_prev_position': PREV_POS.get(away, 10)}
    return [vals[f] for f in feats]


def predict(calibrator, feats, home, away, elo, form):
    X = pd.DataFrame([build_features(home, away, elo, form, feats)], columns=feats)
    p = np.asarray(calibrator.predict_proba(X)[0], dtype=float)
    # promoted / cold-start correction: blend toward Elo prior when a team's Elo < 1350
    he = elo.get(home, 1500.0); ae = elo.get(away, 1500.0); al = 1.0
    if he < 1350: al -= 0.10
    if ae < 1350: al -= 0.10
    if al < 0.999:
        e = 1 / (1 + 10 ** ((ae - he - HFA) / 400)); prior = np.array([e * 0.74, 0.26, (1 - e) * 0.74])
        p = al * p + (1 - al) * prior
    p = p / p.sum(); return float(p[0]), float(p[1]), float(p[2])


def fixtures():
    id2n = {t['id']: canonicalize(t['name']) for t in _get(FPL_BS)['teams']}
    out = []
    for f in _get(FPL_FIX):
        h, a = id2n.get(f.get('team_h')), id2n.get(f.get('team_a'))
        if not h or not a: continue
        out.append({'home': h, 'away': a, 'gw': f.get('event'), 'kickoff': f.get('kickoff_time'),
                    'finished': bool(f.get('finished')), 'hs': f.get('team_h_score'), 'as': f.get('team_a_score')})
    return out


def _sb():
    from supabase import create_client
    return create_client(os.environ['SUPABASE_URL'], os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_KEY'])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview', action='store_true'); ap.add_argument('--insert', action='store_true')
    a = ap.parse_args()
    fx = fixtures(); elo = load_elo(); form = load_form(); calib, feats = load_model()
    played = [f for f in fx if f['finished'] and f['hs'] is not None]
    print(f"Fetched {len(fx)} fixtures ({len(played)} finished).")
    print("GW1 results:" if played else "GW1 results: none finished yet (pre-season).")
    for f in [f for f in fx if f['gw'] == 1]:
        s = f"{f['hs']}-{f['as']}" if f['finished'] and f['hs'] is not None else "scheduled"
        print(f"  {f['home']:<24} {s:<10} {f['away']}")
    print("\nGW2 predictions (home/draw/away):")
    for f in [f for f in fx if f['gw'] == 2]:
        hw, d, aw = predict(calib, feats, f['home'], f['away'], elo, form)
        pick = ['home', 'draw', 'away'][[hw, d, aw].index(max(hw, d, aw))]
        print(f"  {f['home']:<24} vs {f['away']:<24} {hw*100:4.0f}/{d*100:4.0f}/{aw*100:4.0f}  {pick}")
    if not a.insert:
        print("\n(preview only — use --insert to write to Supabase.)"); return

    sb = _sb()
    existing = (sb.table('matches').select('home_team,away_team,tournament_stage')
                .eq('competition', COMPETITION).execute().data) or []
    have = {(r['home_team'], r['away_team'], r['tournament_stage']) for r in existing}
    ins = 0
    for f in fx:
        stage = f"Gameweek {f['gw']}"
        if (f['home'], f['away'], stage) in have: continue
        row = {'match_id': str(uuid.uuid4()), 'home_team': f['home'], 'away_team': f['away'],
               'match_date': f['kickoff'] or '2026-08-21T12:00:00Z', 'tournament_stage': stage,
               'competition': COMPETITION,
               'status': 'finished' if (f['finished'] and f['hs'] is not None) else 'scheduled'}
        if f['finished'] and f['hs'] is not None:
            row['home_score'] = f['hs']; row['away_score'] = f['as']
        sb.table('matches').insert(row).execute(); ins += 1
    print(f"\nInserted {ins} new fixtures (skipped {len(fx)-ins} existing).")
    # predictions for scheduled
    rows = (sb.table('matches').select('match_id,home_team,away_team')
            .eq('competition', COMPETITION).neq('status', 'finished').execute().data) or []
    for r in rows:
        hw, d, aw = predict(calib, feats, r['home_team'], r['away_team'], elo, form)
        sb.table('matches').update({'home_win_probability': round(hw, 4), 'draw_probability': round(d, 4),
                                    'away_win_probability': round(aw, 4)}).eq('match_id', r['match_id']).execute()
    print(f"Wrote predictions for {len(rows)} scheduled matches.")


if __name__ == '__main__':
    main()
