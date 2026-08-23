"""V2 research: M0 (Elo) baseline, M1 calibration, M2-M6 one-feature-at-a-time, M7 combo.
Discipline: a feature is KEPT only if it beats M0 on BOTH validation and holdout (log-loss).
Train 2016-2023, calibrate on 2023-24 (temp/Platt only), validate 2024-25, holdout 2025-26."""
import pandas as pd, numpy as np, os, sys, json, pickle
import xgboost as xgb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
np.random.seed(13)
df=pd.read_csv('data/processed/pl_features.csv')
ENC={'H':0,'D':1,'A':2}; df['y']=df['ftr'].map(ENC)
df['dt']=pd.to_datetime(df['date'])
ELO3=['home_elo','away_elo','elo_diff']
TRAIN=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23']
CAL='2023-24'; VAL='2024-25'; HOLD='2025-26'
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)

# ── rest days (M4) + prev-season position (M5) computed once ─────────────────────
last_played={}; rest_home=[]; rest_away=[]
for r in df.sort_values('dt').itertuples():
    for side,store in [(r.home,rest_home),(r.away,rest_away)]:
        lp=last_played.get(side); store.append((r.dt-lp).days if lp is not None else 7)
    last_played[r.home]=r.dt; last_played[r.away]=r.dt
tmp=df.sort_values('dt').copy(); tmp['home_rest_days']=rest_home; tmp['away_rest_days']=rest_away
df=df.merge(tmp[['date','home','away','home_rest_days','away_rest_days']],on=['date','home','away'],how='left')
df['rest_diff']=(df['home_rest_days']-df['away_rest_days']).clip(-14,14)
df['home_rest_days']=df['home_rest_days'].clip(0,14); df['away_rest_days']=df['away_rest_days'].clip(0,14)
# prev-season final position
seasons=sorted(df['season'].unique())
finalpos={}
for s in seasons:
    d=df[df.season==s]; pts=defaultdict=__import__('collections').defaultdict(float); gd=__import__('collections').defaultdict(float)
    for r in d.itertuples():
        if r.fthg>r.ftag: pts[r.home]+=3
        elif r.ftag>r.fthg: pts[r.away]+=3
        else: pts[r.home]+=1; pts[r.away]+=1
        gd[r.home]+=r.fthg-r.ftag; gd[r.away]+=r.ftag-r.fthg
    rank=sorted(pts,key=lambda t:(-pts[t],-gd[t]))
    for i,t in enumerate(rank,1): finalpos[(s,t)]=i
def prev_pos(season,team):
    i=seasons.index(season)
    if i==0: return 18
    return finalpos.get((seasons[i-1],team),18)   # promoted/unknown -> 18
df['home_prev_pos']=[prev_pos(s,t) for s,t in zip(df['season'],df['home'])]
df['away_prev_pos']=[prev_pos(s,t) for s,t in zip(df['season'],df['away'])]

tr=df[df.season.isin(TRAIN)]; cal=df[df.season==CAL]; val=df[df.season==VAL]; hold=df[df.season==HOLD]
def metrics(P,y):
    P=np.clip(P,1e-9,1); P=P/P.sum(1,keepdims=True); pred=P.argmax(1)
    acc=int((pred==y).sum()); ll=-np.mean([np.log(P[i,y[i]]) for i in range(len(y))])
    return acc,round(float(ll),4)
def run_model(feats,train_seasons=None):
    T=tr if train_seasons is None else df[df.season.isin(train_seasons)]
    m=xgb.XGBClassifier(**HP); m.fit(T[feats],T['y'])
    va=metrics(m.predict_proba(val[feats]),val['y'].values); ho=metrics(m.predict_proba(hold[feats]),hold['y'].values)
    return m,va,ho

R={}  # name -> (val_acc,val_ll,hold_acc,hold_ll)
# ── M0 ──
mE,va0,ho0=run_model(ELO3); R['M0 Elo (3)']=(va0[0],va0[1],ho0[0],ho0[1])
M0vll,M0hll=va0[1],ho0[1]
def beats(vll,hll): return vll<M0vll and hll<M0hll

# ── M1 calibration ──
def temp(P,Tt): lp=np.log(np.clip(P,1e-9,1)); s=np.exp(lp/Tt); return s/s.sum(1,keepdims=True)
Pcal=mE.predict_proba(cal[ELO3]); yc=cal['y'].values
bestT=min([0.8,0.9,1.0,1.1,1.2,1.3,1.5,2.0],key=lambda T:metrics(temp(Pcal,T),yc)[1])
va=metrics(temp(mE.predict_proba(val[ELO3]),bestT),val['y'].values); ho=metrics(temp(mE.predict_proba(hold[ELO3]),bestT),hold['y'].values)
R[f'M1a Elo+temp(T={bestT})']=(va[0],va[1],ho[0],ho[1])
from sklearn.calibration import CalibratedClassifierCV
for nm,meth in [('M1b Elo+Platt','sigmoid'),('M1c Elo+Isotonic','isotonic')]:
    try:
        c=CalibratedClassifierCV(mE,method=meth,cv='prefit'); c.fit(cal[ELO3],cal['y'])
        va=metrics(c.predict_proba(val[ELO3]),val['y'].values); ho=metrics(c.predict_proba(hold[ELO3]),hold['y'].values)
        R[nm]=(va[0],va[1],ho[0],ho[1])
    except Exception as e: R[nm]=('ERR',str(e)[:20],'','')

# ── M2 Elo+goals, M4 Elo+rest, M5 Elo+prevpos ──
_,va,ho=run_model(ELO3+['home_form5_gf','away_form5_gf','home_form5_ga','away_form5_ga']); R['M2 Elo+goals']=(va[0],va[1],ho[0],ho[1])
_,va,ho=run_model(ELO3+['home_rest_days','away_rest_days','rest_diff']); R['M4 Elo+rest']=(va[0],va[1],ho[0],ho[1])
_,va,ho=run_model(ELO3+['home_prev_pos','away_prev_pos'],train_seasons=TRAIN[1:]); R['M5 Elo+prevpos']=(va[0],va[1],ho[0],ho[1])
R['M3 Elo+availability']=('SKIP','no historical injury data','','')
R['M6 Elo+manager']=('SKIP','no manager-change data','','')

# ── M7 best combo: Elo + any feature groups that beat M0 on BOTH seasons ──
groups={'goals':['home_form5_gf','away_form5_gf','home_form5_ga','away_form5_ga'],
        'rest':['home_rest_days','away_rest_days','rest_diff'],'prevpos':['home_prev_pos','away_prev_pos']}
winners=[]
for g,fs in groups.items():
    _,va,ho=run_model(ELO3+fs);
    if beats(va[1],ho[1]): winners.append((g,fs))
combo=ELO3+[f for _,fs in winners for f in fs]
if winners:
    mC,va,ho=run_model(combo)
    Pc=mC.predict_proba(cal[combo]); bT=min([0.8,0.9,1.0,1.1,1.2,1.3,1.5,2.0],key=lambda T:metrics(temp(Pc,T),yc)[1])
    va=metrics(temp(mC.predict_proba(val[combo]),bT),val['y'].values); ho=metrics(temp(mC.predict_proba(hold[combo]),bT),hold['y'].values)
    R[f'M7 combo({"+".join(g for g,_ in winners)})+temp']=(va[0],va[1],ho[0],ho[1])
else:
    R['M7 combo']=('none','no feature beat M0','','')

# ── results ──
print("=== V2 FEATURE TESTS — sorted by holdout log-loss ===")
print(f"{'Model':<30}{'Val acc':<10}{'Val LL':<9}{'Hold acc':<10}{'Hold LL':<9}{'Beats M0?'}")
def sortkey(kv):
    v=kv[1]; return v[3] if isinstance(v[3],float) else 9
for nm,v in sorted(R.items(),key=sortkey):
    if isinstance(v[3],float):
        b='YES' if beats(v[1],v[3]) else 'no'
        print(f"{nm:<30}{f'{v[0]}/380':<10}{v[1]:<9}{f'{v[2]}/380':<10}{v[3]:<9}{b}")
    else:
        print(f"{nm:<30}{str(v[0]):<10}{str(v[1])}")
print(f"{'Bet365 (benchmark)':<30}{'-':<10}{'-':<9}{'186/380':<10}{'1.0185':<9}reference")
print(f"\ngap to Bet365 (holdout LL): M0 {M0hll-1.0185:+.4f}  |  best {min(v[3] for v in R.values() if isinstance(v[3],float))-1.0185:+.4f}")

best=min([(nm,v) for nm,v in R.items() if isinstance(v[3],float)],key=lambda x:x[1][3])
print(f"\nBEST by holdout LL: {best[0]}  (hold {best[1][2]}/380, LL {best[1][3]})")
pickle.dump({'model':mE,'calibration':'temperature','T':bestT,'features':ELO3,'note':'V2 candidate = calibrated Elo (see report)'},
            open('data/models/pl_v2_candidate.pkl','wb'))
json.dump({'results':{k:list(v) for k,v in R.items()},'M0':{'val_ll':M0vll,'hold_ll':M0hll},'best':best[0],
           'bet365_hold_ll':1.0185,'best_T':bestT},open('data/experiments/v2_feature_tests.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
print("saved v2_feature_tests.json + pl_v2_candidate.pkl")
