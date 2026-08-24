"""One-time state seed for the PL auto-pipeline. Reads the latest Elo per team by
replaying club_elo_derived.csv, and last-5 goals-for from 2025-26, then writes the
persistent JSON state the pipeline updates each run. Run ONCE before pl_auto_pipeline.py.

    python3 scripts/init_pl_state.py
"""
import os, sys, json
from collections import defaultdict, deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from team_aliases import canonicalize, PL_2026_27

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELO_CSV = os.path.join(_ROOT, 'data/processed/club_elo_derived.csv')
CUR_ELO_CSV = os.path.join(_ROOT, 'data/processed/current_elo.csv')
FEATURES = os.path.join(_ROOT, 'data/processed/pl_features.csv')
ELO_JSON = os.path.join(_ROOT, 'data/processed/current_elo.json')
FORM_JSON = os.path.join(_ROOT, 'data/processed/current_form.json')
K, HFA, PROMOTED_ELO = 20, 100, 1300.0


def latest_elo():
    """Replay club_elo_derived.csv -> Elo AFTER each team's most recent match."""
    d = pd.read_csv(ELO_CSV).sort_values('date')
    elo = {}
    for r in d.itertuples():
        he, ae = float(r.home_elo_before), float(r.away_elo_before)
        sh = 1.0 if r.fthg > r.ftag else 0.5 if r.fthg == r.ftag else 0.0
        e_home = 1 / (1 + 10 ** ((ae - he - HFA) / 400))
        elo[canonicalize(r.home)] = he + K * (sh - e_home)
        elo[canonicalize(r.away)] = ae + K * ((1 - sh) - (1 - e_home))
    return elo


def latest_form():
    """Last-5 goals-for per team from 2025-26."""
    df = pd.read_csv(FEATURES); d = df[df['season'] == '2025-26'].sort_values('date')
    dq = defaultdict(lambda: deque(maxlen=5))
    for r in d.itertuples():
        dq[canonicalize(r.home)].append(int(r.fthg)); dq[canonicalize(r.away)].append(int(r.ftag))
    return {t: list(v) for t, v in dq.items()}


def main():
    elo_all = latest_elo()
    cur = {canonicalize(r['team']): float(r['derived_elo']) for _, r in pd.read_csv(CUR_ELO_CSV).iterrows()}
    form_all = latest_form()
    elo_state, form_state = {}, {}
    for team in PL_2026_27:                      # seed only the 20 current teams
        elo_state[team] = round(elo_all.get(team, cur.get(team, PROMOTED_ELO)), 1)
        form_state[team] = form_all.get(team, [])   # promoted -> empty (cold start)
    json.dump(elo_state, open(ELO_JSON, 'w'), indent=1)
    json.dump(form_state, open(FORM_JSON, 'w'), indent=1)
    print(f"seeded current_elo.json ({len(elo_state)} teams) + current_form.json")
    for t in sorted(elo_state, key=lambda x: -elo_state[x])[:5]:
        print(f"  {t:<22} Elo {elo_state[t]}  form5_gf {round(sum(form_state[t])/len(form_state[t]),2) if form_state[t] else 'cold-start(1.3)'}")


if __name__ == '__main__':
    main()
