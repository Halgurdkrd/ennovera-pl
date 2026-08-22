"""Phase 2: derive Club Elo from 10 seasons of results + build leak-free pre-match
features for all ~3,800 matches. Run from ennovera-pl/ .

Outputs (data/processed/):
  club_elo_derived.csv  — per-match pre-match Elo (leak-free) + running ratings
  current_elo.csv       — latest Elo per team + 2026-27 promoted-team handling
  pl_features.csv       — full pre-match feature matrix (target = FTR)
"""
import pandas as pd, numpy as np, glob, os, sys
from collections import defaultdict, deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team_aliases import canonicalize, PL_2026_27

RAW = 'data/raw/pl_history'; OUT = 'data/processed'; os.makedirs(OUT, exist_ok=True)

# ── load + canonicalize all seasons ─────────────────────────────────────────────
frames = []
for f in sorted(glob.glob(f'{RAW}/E0_*.csv')):
    season = os.path.basename(f).replace('E0_', '').replace('.csv', '')
    d = pd.read_csv(f, encoding='latin-1')
    d = d[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']].copy()
    d['season'] = season
    frames.append(d)
df = pd.concat(frames, ignore_index=True).dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
df['home'] = df['HomeTeam'].map(canonicalize); df['away'] = df['AwayTeam'].map(canonicalize)
df['fthg'] = df['FTHG'].astype(int); df['ftag'] = df['FTAG'].astype(int)
df['date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
print(f"loaded {len(df)} matches, {df['season'].nunique()} seasons, "
      f"{len(set(df['home'])|set(df['away']))} teams (canonicalized)")

# ── state ───────────────────────────────────────────────────────────────────────
K, HFA = 20, 100
elo = defaultdict(lambda: 1500.0)
res5 = defaultdict(lambda: deque(maxlen=5));  res10 = defaultdict(lambda: deque(maxlen=10))
home5 = defaultdict(lambda: deque(maxlen=5)); away5 = defaultdict(lambda: deque(maxlen=5))
h2h = defaultdict(lambda: deque(maxlen=5))    # frozenset(pair) -> deque of winner name / 'draw'
s_pts = defaultdict(lambda: defaultdict(float)); s_gd = defaultdict(lambda: defaultdict(float))
s_gf = defaultdict(lambda: defaultdict(int));   s_played = defaultdict(lambda: defaultdict(int))

def fs(dq, pre=''):
    if not dq:
        return {f'{pre}ppg': 0.0, f'{pre}gf': 0.0, f'{pre}ga': 0.0, f'{pre}cs': 0.0, f'{pre}n': 0}
    n = len(dq)
    return {f'{pre}ppg': sum(x[0] for x in dq) / n, f'{pre}gf': sum(x[1] for x in dq) / n,
            f'{pre}ga': sum(x[2] for x in dq) / n, f'{pre}cs': sum(x[3] for x in dq) / n, f'{pre}n': n}

def position(season, team):
    tbl = sorted(((t, s_pts[season][t], s_gd[season][t], s_gf[season][t]) for t in s_pts[season]),
                 key=lambda x: (-x[1], -x[2], -x[3]))
    for i, (t, *_) in enumerate(tbl, 1):
        if t == team:
            return i
    return len(tbl) + 1

rows, elo_hist = [], []
for r in df.itertuples():
    h, a, season = r.home, r.away, r.season
    eh, ea = elo[h], elo[a]
    # ---- PRE-MATCH features (leak-free) ----
    hp, ap = position(season, h), position(season, a)
    pr = frozenset((h, a)); hh = list(h2h[pr])
    feat = {
        'date': r.date.date().isoformat(), 'season': season, 'home': h, 'away': a,
        'fthg': r.fthg, 'ftag': r.ftag, 'ftr': r.FTR,          # FTR = target (H/D/A)
        'home_elo': round(eh, 1), 'away_elo': round(ea, 1), 'elo_diff': round(eh - ea, 1),
        'home_pos': hp, 'away_pos': ap, 'pos_diff': ap - hp,
        'home_played': s_played[season][h], 'away_played': s_played[season][a],
        'h2h_home_wins': sum(1 for w in hh if w == h),
        'h2h_away_wins': sum(1 for w in hh if w == a),
        'h2h_draws': sum(1 for w in hh if w == 'draw'), 'h2h_n': len(hh),
    }
    feat.update(fs(res5[h], 'home_form5_')); feat.update(fs(res5[a], 'away_form5_'))
    feat.update(fs(res10[h], 'home_form10_')); feat.update(fs(res10[a], 'away_form10_'))
    feat.update(fs(home5[h], 'home_athome_')); feat.update(fs(away5[a], 'away_ataway_'))
    rows.append(feat)
    elo_hist.append({'date': feat['date'], 'season': season, 'home': h, 'away': a,
                     'home_elo_before': round(eh, 1), 'away_elo_before': round(ea, 1),
                     'fthg': r.fthg, 'ftag': r.ftag})
    # ---- UPDATE state (after the match) ----
    sh = 1.0 if r.fthg > r.ftag else 0.5 if r.fthg == r.ftag else 0.0
    e_home = 1 / (1 + 10 ** ((ea - eh - HFA) / 400))
    elo[h] = eh + K * (sh - e_home); elo[a] = ea + K * ((1 - sh) - (1 - e_home))
    hp_pts, ap_pts = (3, 0) if sh == 1 else (1, 1) if sh == 0.5 else (0, 3)
    res5[h].append((hp_pts, r.fthg, r.ftag, 1 if r.ftag == 0 else 0))
    res5[a].append((ap_pts, r.ftag, r.fthg, 1 if r.fthg == 0 else 0))
    res10[h].append((hp_pts, r.fthg, r.ftag, 1 if r.ftag == 0 else 0))
    res10[a].append((ap_pts, r.ftag, r.fthg, 1 if r.fthg == 0 else 0))
    home5[h].append((hp_pts, r.fthg, r.ftag, 1 if r.ftag == 0 else 0))
    away5[a].append((ap_pts, r.ftag, r.fthg, 1 if r.fthg == 0 else 0))
    h2h[pr].append(h if sh == 1 else a if sh == 0 else 'draw')
    s_pts[season][h] += hp_pts; s_pts[season][a] += ap_pts
    s_gd[season][h] += r.fthg - r.ftag; s_gd[season][a] += r.ftag - r.fthg
    s_gf[season][h] += r.fthg; s_gf[season][a] += r.ftag
    s_played[season][h] += 1; s_played[season][a] += 1

feat_df = pd.DataFrame(rows)
feat_df.to_csv(f'{OUT}/pl_features.csv', index=False)
pd.DataFrame(elo_hist).to_csv(f'{OUT}/club_elo_derived.csv', index=False)
print(f"saved pl_features.csv ({len(feat_df)} rows, {len(feat_df.columns)} cols)")
print(f"saved club_elo_derived.csv ({len(elo_hist)} rows)")

# ── current Elo + 2026-27 promoted-team handling (Priority 3) ────────────────────
fpl_path = 'data/raw/fpl_history/2026-27/teams.csv'
fpl = pd.read_csv(fpl_path) if os.path.exists(fpl_path) else pd.DataFrame()
fpl_str = {}
if not fpl.empty:
    for _, t in fpl.iterrows():
        fpl_str[canonicalize(t['name'])] = (t.get('strength_overall_home'), t.get('strength_overall_away'))
cur = []
PROMOTED_BASELINE = 1300.0
for team in PL_2026_27:
    has_hist = team in elo
    sh, sa = fpl_str.get(team, (None, None))
    if has_hist:
        e = round(elo[team], 1); note = 'derived'
        if team in ('Hull City', 'Sunderland'):
            note = 'derived (STALE — last PL season years ago; Elo frozen at relegation)'
    else:
        e = PROMOTED_BASELINE; note = 'promoted, no PL history -> baseline 1300 (use FPL strength proxy)'
    cur.append({'team': team, 'derived_elo': e, 'fpl_strength_home': sh, 'fpl_strength_away': sa, 'note': note})
cur_df = pd.DataFrame(cur).sort_values('derived_elo', ascending=False)
cur_df.to_csv(f'{OUT}/current_elo.csv', index=False)
print(f"\nsaved current_elo.csv — 2026-27 teams ranked by derived Elo:")
print(cur_df.to_string(index=False))
