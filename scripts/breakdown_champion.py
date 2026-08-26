"""Full breakdown of how V3 gives Man City 51.7% and Arsenal 36.0% champion probability.
Traces: raw inputs -> base V2 per-match probs -> V3 overlay components -> expected points ->
Monte Carlo champion %."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv; load_dotenv()
import numpy as np
from populate_pl_matches import fixtures, load_model, load_elo, load_form, PREV_POS, DEFAULT_GF
from pl_simulation import simulate
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V3=os.path.join(_ROOT,'data/v3')
strength=json.load(open(f'{V3}/fpl_team_strength.json')); squad=json.load(open(f'{V3}/squad_features.json'))
calib,feats=load_model(); elo=load_elo(); form=load_form()
AVG_VALUE=np.mean([squad[t]['squad_value'] for t in squad])
CITY,ARS='Manchester City','Arsenal'

def fg(t): v=form.get(t,DEFAULT_GF); return v if isinstance(v,(int,float)) else DEFAULT_GF
def v2_predict(h,a):
    he=elo.get(h,1500.); ae=elo.get(a,1500.)
    vals={'home_elo':he,'away_elo':ae,'elo_diff':he-ae,'home_form5_gf':fg(h),'away_form5_gf':fg(a),
          'home_prev_position':PREV_POS.get(h,10),'away_prev_position':PREV_POS.get(a,10)}
    import pandas as pd
    p=np.asarray(calib.predict_proba(pd.DataFrame([[vals[f] for f in feats]],columns=feats))[0],float)
    if he<1350: al=0.9; e=1/(1+10**((ae-he-100)/400)); p=al*p+(1-al)*np.array([e*.74,.26,(1-e)*.74])
    return p/p.sum()
def overlay_components(h,a):
    s=strength.get(h,{}); s2=strength.get(a,{}); q=squad.get(h,{}); q2=squad.get(a,{})
    n=lambda x:(x or 1100)/1000.0
    atk=n(s.get('strength_attack_home'))-n(s2.get('strength_attack_away'))
    dfc=n(s.get('strength_defence_home'))-n(s2.get('strength_defence_away'))
    val=(q.get('squad_value',AVG_VALUE)-q2.get('squad_value',AVG_VALUE))/max(AVG_VALUE,1)
    comp=(0.5*atk+0.3*dfc+0.2*val)*0.05
    dep=(q2.get('dependency',0.3)-q.get('dependency',0.3))*0.15
    coh=(q.get('cohesion',0.75)-q2.get('cohesion',0.75))*0.10
    raw=comp+dep+coh; adj=float(np.clip(raw,-0.06,0.06))
    return dict(strength=round(comp,4),dependency=round(dep,4),cohesion=round(coh,4),raw=round(raw,4),clipped=round(adj,4))
def v3_predict(h,a):
    p=v2_predict(h,a).copy(); adj=overlay_components(h,a)['clipped']
    p=np.array([p[0]+adj,p[1],p[2]-adj]); p=np.clip(p,0.02,None); return p/p.sum()

fx=fixtures()
print("="*70)
print("STAGE 1 — RAW INPUTS (the numbers everything derives from)")
print("="*70)
print(f"{'':<16}{'Elo':<8}{'prev_pos':<10}{'sq_value':<10}{'dependency':<12}{'FPL atk(H/A)':<14}{'FPL def(H/A)'}")
for t in (CITY,ARS):
    s=strength[t]; q=squad[t]
    print(f"{t:<16}{round(elo[t]):<8}{PREV_POS[t]:<10}{q['squad_value']:<10}{q['dependency']:<12}"
          f"{str(s['strength_attack_home'])+'/'+str(s['strength_attack_away']):<14}"
          f"{str(s['strength_defence_home'])+'/'+str(s['strength_defence_away'])}")

print("\n"+"="*70)
print("STAGE 2 — V3 OVERLAY, decomposed & averaged over each team's 38 matches")
print("  (per-match adjustment to that team's win prob; + = upgrade, - = downgrade)")
print("="*70)
def team_overlay_avg(team):
    comps=dict(strength=[],dependency=[],cohesion=[],clipped=[])
    for f in fx:
        if f['home']==team:
            c=overlay_components(team,f['away'])
            for k in comps: comps[k].append(c[k])          # team is home -> +adj
        elif f['away']==team:
            c=overlay_components(f['home'],team)
            for k in comps: comps[k].append(-c[k])          # team is away -> -adj
    return {k:round(np.mean(v),4) for k,v in comps.items()}
print(f"{'':<16}{'strength':<12}{'dependency':<12}{'cohesion':<12}{'NET/match':<12}")
for t in (CITY,ARS):
    o=team_overlay_avg(t)
    net=round(o['clipped'],4)
    print(f"{t:<16}{o['strength']:+.4f}     {o['dependency']:+.4f}     {o['cohesion']:+.4f}     {net:+.4f}")
print("\n  -> City's high dependency (0.40) makes its dependency term NEGATIVE (self-downgrade);")
print("     Arsenal's strength + lower dependency net POSITIVE. Cohesion=0 (all 0.5 pre-season).")

print("\n"+"="*70)
print("STAGE 3 — EXPECTED POINTS over all 38 matches (3*P(win)+1*P(draw))")
print("="*70)
def xpoints(pf,team):
    xp=0.0
    for f in fx:
        if f['home']==team: p=pf(f['home'],f['away']); xp+=3*p[0]+p[1]
        elif f['away']==team: p=pf(f['home'],f['away']); xp+=3*p[2]+p[1]
    return xp
print(f"{'':<16}{'V2 xPts':<10}{'V3 xPts':<10}{'change'}")
for t in (CITY,ARS):
    x2=xpoints(v2_predict,t); x3=xpoints(v3_predict,t)
    print(f"{t:<16}{x2:<10.1f}{x3:<10.1f}{x3-x2:+.1f}")
gap2=xpoints(v2_predict,CITY)-xpoints(v2_predict,ARS); gap3=xpoints(v3_predict,CITY)-xpoints(v3_predict,ARS)
print(f"\n  City-minus-Arsenal expected-points lead:  V2 {gap2:+.1f}  ->  V3 {gap3:+.1f}  (overlay shrinks City's lead)")

print("\n"+"="*70)
print("STAGE 4 — MONTE CARLO -> champion % (why the lead maps to 51.7 / 36.0)")
print("="*70)
def champ(pf):
    ms=[{'home':f['home'],'away':f['away'],'finished':False,'hs':None,'as':None,'probs':list(pf(f['home'],f['away']))} for f in fx]
    return {r['team_name']:(r['champion_pct'],r['avg_points']) for r in simulate(ms,5000)}
c2=champ(v2_predict); c3=champ(v3_predict)
print(f"{'':<16}{'V2 champ%':<12}{'V2 avgPts':<11}{'V3 champ%':<12}{'V3 avgPts'}")
for t in (CITY,ARS):
    print(f"{t:<16}{c2[t][0]:<12.1f}{c2[t][1]:<11.1f}{c3[t][0]:<12.1f}{c3[t][1]:.1f}")
combined=c3[CITY][0]+c3[ARS][0]
print(f"\n  City+Arsenal own {combined:.0f}% of title outcomes -> essentially a 2-horse race.")
print(f"  It's decided by their avg-points gap + season variance: a ~{gap3:.0f}-pt V3 lead for City")
print(f"  over 38 noisy matches -> City wins the title ~{c3[CITY][0]:.0f}% of sims, Arsenal ~{c3[ARS][0]:.0f}%.")
