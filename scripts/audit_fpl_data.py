"""Audit historical FPL data for V3 validation. No model changes. Reads data/raw/fpl_full/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from team_aliases import canonicalize
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.path.join(_ROOT,'data/raw/fpl_full/data')
SEASONS=['2022-23','2023-24','2024-25','2025-26']
CRIT=['expected_goals','expected_assists','value','minutes','team','GW','round','was_home','total_points',
      'clean_sheets','ict_index','chance_of_playing_this_round','chance_of_playing_next_round','status',
      'transfers_in','transfers_out']

def load_gw(s):
    p=os.path.join(BASE,s,'gws/merged_gw.csv')
    return pd.read_csv(p,encoding='latin-1',low_memory=False) if os.path.exists(p) else None

print("### 1B: per-season summary ###")
print(f"{'Season':<10}{'Players':<9}{'Teams':<7}{'GWs':<6}{'xG?':<6}{'xA?':<7}{'price?'}")
gws={}
for s in SEASONS:
    g=load_gw(s); gws[s]=g
    if g is None: print(f"{s:<10}MISSING"); continue
    gwcol='GW' if 'GW' in g.columns else ('round' if 'round' in g.columns else None)
    nplay=g['element'].nunique() if 'element' in g.columns else g['name'].nunique()
    nteam=g['team'].nunique() if 'team' in g.columns else '?'
    ngw=g[gwcol].nunique() if gwcol else '?'
    print(f"{s:<10}{nplay:<9}{nteam:<7}{ngw:<6}{'YES' if 'expected_goals' in g.columns else 'no':<6}"
          f"{'YES' if 'expected_assists' in g.columns else 'no':<7}{'YES' if 'value' in g.columns else 'no'}")

print("\n### 1B: critical column presence (merged_gw.csv) ###")
print(f"{'column':<28}"+"".join(f"{s:<10}" for s in SEASONS))
for c in CRIT:
    row=f"{c:<28}"
    for s in SEASONS:
        g=gws[s]; row+=f"{'YES' if (g is not None and c in g.columns) else '--':<10}"
    print(row)

print("\n### 1C: teams.csv strength ratings ###")
for s in SEASONS:
    tp=os.path.join(BASE,s,'teams.csv')
    if not os.path.exists(tp): continue
    t=pd.read_csv(tp); cols=[c for c in ['name','strength_overall_home','strength_overall_away','strength_attack_home','strength_attack_away','strength_defence_home','strength_defence_away'] if c in t.columns]
    print(f"  {s}: cols={cols}")
    if 'strength_attack_home' in t.columns:
        for _,r in t.sort_values('strength_overall_home',ascending=False).head(3).iterrows():
            print(f"    {r['name']:<16} atk_h={r['strength_attack_home']} atk_a={r['strength_attack_away']} def_h={r['strength_defence_home']} def_a={r['strength_defence_away']}")
        nonzero=(t['strength_attack_home']!=0).sum(); print(f"    -> non-zero attack ratings: {nonzero}/{len(t)}")

print("\n### 1D: per-team per-GW features (2024-25, GW1 sample) ###")
g=gws['2024-25']; gwcol='GW' if 'GW' in g.columns else 'round'
if g is not None and 'expected_goals' in g.columns:
    gw1=g[g[gwcol]==1]
    for team in list(gw1['team'].dropna().unique())[:3]:
        d=gw1[gw1['team']==team]
        xg=d['expected_goals'].astype(float).sum(); xa=d['expected_assists'].astype(float).sum()
        val=d.nlargest(18,'value')['value'].sum()/10 if 'value' in d.columns else 0
        avail=(d['minutes'].astype(float)>0).sum()
        xgs=d['expected_goals'].astype(float)
        dep=xgs.max()/max(xgs.sum(),0.1)
        print(f"  GW1 {team}: xG={xg:.1f} xA={xa:.1f} value=£{val:.0f}M played={avail} dep={dep:.2f}")

print("\n### 1E: join FPL -> pl_features (team-name check) ###")
plf=pd.read_csv(os.path.join(_ROOT,'data/processed/pl_features.csv'))
fpl_teams=set(canonicalize(t) for t in g['team'].dropna().unique()) if g is not None else set()
plf_teams=set(plf[plf.season=='2024-25']['home'].unique())
print(f"  FPL 2024-25 teams (canonicalised): {len(fpl_teams)} | pl_features 2024-25 teams: {len(plf_teams)}")
print(f"  in FPL but not pl_features: {sorted(fpl_teams-plf_teams) or 'none'}")
print(f"  in pl_features but not FPL: {sorted(plf_teams-fpl_teams) or 'none'}")

print("\n### 1F: backtestable matches ###")
print(f"{'Season':<10}{'Matches':<9}{'FPL team':<11}{'FPL player':<12}{'Usable?'}")
usable=0
for s in ['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22']+SEASONS:
    has=s in SEASONS and gws.get(s) is not None
    xg=has and 'expected_goals' in gws[s].columns
    u='YES' if xg else 'no'
    if xg: usable+=380
    print(f"{s:<10}{'380':<9}{('YES' if has else 'no'):<11}{('YES(xG)' if xg else 'no'):<12}{u}")
print(f"\n  Total xG-backtestable matches: {usable} (of 3,800)")

print("\n### 1G: data quality (xG coverage per season) ###")
for s in SEASONS:
    g=gws[s]
    if g is None or 'expected_goals' not in g.columns: continue
    gwcol='GW' if 'GW' in g.columns else 'round'
    ngw=g[gwcol].nunique(); miss=g['expected_goals'].isna().mean()*100
    print(f"  {s}: {ngw} GWs, expected_goals missing {miss:.1f}%, "
          f"chance_of_playing present: {'chance_of_playing_this_round' in g.columns}, status present: {'status' in g.columns}")
