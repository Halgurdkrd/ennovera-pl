"""V3 Steps 13-15: V3 = validated V2 base (regular Elo+Platt) + Layer 2/4 FPL overlays
(unvalidated live-season heuristics). Predicts 2026-27, compares V2 vs V3, adds confidence,
champion% shift. Split Elo (Layer 1) was REJECTED (overfit validation, worse holdout)."""
import os, sys, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv; load_dotenv()
import numpy as np, pandas as pd
from populate_pl_matches import fixtures, load_model, load_elo, load_form, PREV_POS, DEFAULT_GF
from pl_simulation import simulate
from team_aliases import canonicalize
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V3=os.path.join(_ROOT,'data/v3')
strength=json.load(open(f'{V3}/fpl_team_strength.json')); squad=json.load(open(f'{V3}/squad_features.json'))
calib,feats=load_model(); elo=load_elo(); form=load_form()
AVG_VALUE=np.mean([squad[t]['squad_value'] for t in squad])

def v2_predict(h,a):
    he=elo.get(h,1500.); ae=elo.get(a,1500.)
    fg=lambda t: form.get(t,DEFAULT_GF) if isinstance(form.get(t),(int,float)) else DEFAULT_GF
    vals={'home_elo':he,'away_elo':ae,'elo_diff':he-ae,'home_form5_gf':fg(h),'away_form5_gf':fg(a),
          'home_prev_position':PREV_POS.get(h,10),'away_prev_position':PREV_POS.get(a,10)}
    X=pd.DataFrame([[vals[f] for f in feats]],columns=feats)
    p=np.asarray(calib.predict_proba(X)[0],float)
    if he<1350: al=0.9; e=1/(1+10**((ae-he-100)/400)); p=al*p+(1-al)*np.array([e*.74,.26,(1-e)*.74])
    return p/p.sum()

def overlay(h,a):
    """Layer 2 (strength/value) + Layer 4 (dependency/cohesion/FDR). xG-form (Layer 3) ~0
    pre-season. Normalised + CLIPPED to +-0.06. Heuristic, UNVALIDATED (no historical FPL)."""
    s=strength.get(h,{}); s2=strength.get(a,{}); q=squad.get(h,{}); q2=squad.get(a,{})
    def n(x): return (x or 1100)/1000.0
    atk=n(s.get('strength_attack_home'))-n(s2.get('strength_attack_away'))
    dfc=n(s.get('strength_defence_home'))-n(s2.get('strength_defence_away'))
    val=((q.get('squad_value',AVG_VALUE)-q2.get('squad_value',AVG_VALUE))/max(AVG_VALUE,1))
    comp=0.5*atk+0.3*dfc+0.2*val
    # Layer 4: high dependency = fragile (small penalty); cohesion diff; (availability~0 pre-season)
    dep=(q2.get('dependency',0.3)-q.get('dependency',0.3))*0.15   # away more dependent -> home edge
    coh=(q.get('cohesion',0.75)-q2.get('cohesion',0.75))*0.10
    adj=comp*0.05+dep+coh
    return float(np.clip(adj,-0.06,0.06))

def v3_predict(h,a):
    p=v2_predict(h,a).copy(); adj=overlay(h,a)
    p=np.array([p[0]+adj,p[1],p[2]-adj]); p=np.clip(p,0.02,None); return p/p.sum()

def confidence(h,a):
    promoted=(elo.get(h,1500)<1400) or (elo.get(a,1500)<1400) or PREV_POS.get(h,10)>=18 or PREV_POS.get(a,10)>=18
    return 'LOW' if promoted else 'HIGH'

fx=fixtures(); LAB=['home','draw','away']
print("=== V2 vs V3 — GW2 (V3 = V2 base + FPL overlays) ===")
print(f"{'Match':<44}{'V2 (H/D/A)':<16}{'V3 (H/D/A)':<16}{'conf'}")
changes=[]
for f in fx:
    v2=v2_predict(f['home'],f['away']); v3=v3_predict(f['home'],f['away'])
    changes.append((f['home'],f['away'],v2,v3,abs(v2-v3).max()))
    if f['gw']==2:
        c=confidence(f['home'],f['away'])
        print(f"{f['home']+' vs '+f['away']:<44}{f'{v2[0]*100:.0f}/{v2[1]*100:.0f}/{v2[2]*100:.0f}':<16}{f'{v3[0]*100:.0f}/{v3[1]*100:.0f}/{v3[2]*100:.0f}':<16}{c}")
changes.sort(key=lambda x:-x[4])
print("\n=== Top 10 biggest V2->V3 changes ===")
for h,a,v2,v3,d in changes[:10]:
    print(f"  {h} vs {a}: V2 {v2[0]*100:.0f}/{v2[1]*100:.0f}/{v2[2]*100:.0f} -> V3 {v3[0]*100:.0f}/{v3[1]*100:.0f}/{v3[2]*100:.0f}  (Δ{d*100:.0f}pp)")

# champion% shift (quick sim)
def sim_table(pf):
    ms=[{'home':f['home'],'away':f['away'],'finished':f['finished'] and f['hs'] is not None,'hs':f['hs'],'as':f['as'],
         'probs':list(pf(f['home'],f['away']))} for f in fx]
    return {r['team_name']:r['champion_pct'] for r in simulate(ms,3000)}
c2=sim_table(v2_predict); c3=sim_table(v3_predict)
print("\n=== Champion % V2 vs V3 (top 5) ===")
for t in sorted(c3,key=lambda x:-c3[x])[:5]:
    print(f"  {t:<20} V2 {c2.get(t,0):.1f}%  ->  V3 {c3[t]:.1f}%")
preds=[{'home':h,'away':a,'v3':[round(float(x),4) for x in v3],'confidence':confidence(h,a)} for h,a,v2,v3,d in
       [(f['home'],f['away'],v2_predict(f['home'],f['away']),v3_predict(f['home'],f['away']),0) for f in fx if f['gw']==2]]
json.dump({'model':'V3 = V2 base + FPL overlays (Layer2/4)','predictions':preds},
          open(os.path.join(_ROOT,'data/predictions/v3_predictions.json') if os.path.isdir(os.path.join(_ROOT,'data/predictions')) else f'{V3}/v3_predictions.json','w'),indent=1)
print("\nsaved v3_predictions.json")
