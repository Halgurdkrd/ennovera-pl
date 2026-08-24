"""V3 Step 3: squad-level features from current FPL player data -> data/v3/squad_features.json.
Current-season only (no historical player data)."""
import os, sys, json
from collections import defaultdict
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V3=os.path.join(_ROOT,'data/v3')
players=json.load(open(f'{V3}/fpl_players.json'))
by_team=defaultdict(list)
for p in players:
    if p['team']: by_team[p['team']].append(p)
out={}
for team,ps in by_team.items():
    by_min=sorted(ps,key=lambda x:-x['minutes'])
    top18=by_min[:18]; top11=by_min[:11]; top15=by_min[:15]
    sv=sum(p['now_cost'] for p in top18)/10; xi=sum(p['now_cost'] for p in top11)/10
    bench=sv-xi
    total_xg=sum(p['xg'] for p in ps); total_xa=sum(p['xa'] for p in ps)
    top_xg=max((p['xg'] for p in ps),default=0.0)
    dep=top_xg/max(total_xg,0.1)
    # new signings proxy: low minutes among nominal squad = recently arrived / not established
    new=sum(1 for p in by_min[:25] if p['minutes']<200)
    cohesion=1.0-(new/25)*0.5
    avg_min11=sum(p['minutes']/max(p['starts'],1) for p in top11)/max(len(top11),1)
    out[team]={'squad_value':round(sv,1),'xi_value':round(xi,1),'bench_value':round(bench,1),
               'depth_ratio':round(bench/max(xi,1),3),'avg_ict':round(sum(p['ict'] for p in top15)/max(len(top15),1),1),
               'total_xg':round(total_xg,1),'total_xa':round(total_xa,1),'dependency':round(dep,3),
               'new_signings':new,'cohesion':round(cohesion,3),'avg_minutes_top11':round(avg_min11,1)}
json.dump(out,open(f'{V3}/squad_features.json','w'),indent=1)
print(f"saved squad_features.json ({len(out)} teams)")
for t in sorted(out,key=lambda x:-out[x]['squad_value'])[:5]:
    v=out[t]; print(f"  {t:<20} value {v['squad_value']}m  dep {v['dependency']}  cohesion {v['cohesion']}")
