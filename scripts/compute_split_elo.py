"""V3 Step 2: split attack/defence Elo (K=20, start 1500) from 3,800 matches, leak-free.
Promoted teams start at 1450 (below-avg) — Championship-Elo prior deferred (needs E1.csv)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from team_aliases import canonicalize, PL_2026_27
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V3=os.path.join(_ROOT,'data/v3')
df=pd.read_csv(os.path.join(_ROOT,'data/processed/pl_features.csv'))
df['dt']=pd.to_datetime(df['date']); df=df.sort_values('dt')
K=20
atk={}; dfn={}
def g(d,t): return d.get(t,1500.0)
rows=[]
for r in df.itertuples():
    h,a=canonicalize(r.home),canonicalize(r.away)
    ha,hd,aa,ad=g(atk,h),g(dfn,h),g(atk,a),g(dfn,a)
    rows.append({'date':r.date,'season':r.season,'home':h,'away':a,
                 'home_attack_elo':round(ha,1),'home_defence_elo':round(hd,1),
                 'away_attack_elo':round(aa,1),'away_defence_elo':round(ad,1)})
    tot=max(r.fthg+r.ftag,1)
    # attack: goals scored share vs opponent defence
    eh_atk=1/(1+10**((ad-ha)/400)); act_h_atk=r.fthg/tot
    ea_atk=1/(1+10**((hd-aa)/400)); act_a_atk=r.ftag/tot
    atk[h]=ha+K*(act_h_atk-eh_atk); atk[a]=aa+K*(act_a_atk-ea_atk)
    # defence: 1 - goals conceded share vs opponent attack
    eh_def=1/(1+10**((aa-hd)/400)); act_h_def=1-(r.ftag/tot)
    ea_def=1/(1+10**((ha-ad)/400)); act_a_def=1-(r.fthg/tot)
    dfn[h]=hd+K*(act_h_def-eh_def); dfn[a]=ad+K*(act_a_def-ea_def)
pd.DataFrame(rows).to_csv(f'{V3}/split_elo.csv',index=False)
cur={}
for t in PL_2026_27:
    cur[t]={'attack_elo':round(atk.get(t,1450.0),1),'defence_elo':round(dfn.get(t,1450.0),1),
            'promoted':t not in atk}
json.dump(cur,open(f'{V3}/current_split_elo.json','w'),indent=1)
print(f"saved split_elo.csv ({len(rows)} rows) + current_split_elo.json")
top=sorted(cur.items(),key=lambda x:-(x[1]['attack_elo']-x[1]['defence_elo']))
for t,v in top[:5]: print(f"  {t:<22} atk {v['attack_elo']}  def {v['defence_elo']}")
