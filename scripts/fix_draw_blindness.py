"""DRY RUN: three fixes for draw-blindness, compared on 2024-25 validation.
A=class weighting, B=two-stage (draw-vs-decisive gate), C=post-hoc draw floor."""
import pandas as pd, numpy as np, os, sys
import xgboost as xgb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
np.random.seed(13)
df=pd.read_csv('data/processed/pl_features.csv')
ENC={'H':0,'D':1,'A':2}; df['y']=df['ftr'].map(ENC)
NONFEAT={'date','season','home','away','fthg','ftag','ftr','y'}
FEAT_A=[c for c in df.columns if c not in NONFEAT]
FEAT_B=['home_elo','away_elo','elo_diff','home_form5_ppg','away_form5_ppg','home_form5_gf','away_form5_gf',
        'home_form5_ga','away_form5_ga','home_form10_ppg','away_form10_ppg','home_athome_ppg','away_ataway_ppg',
        'h2h_home_wins','h2h_away_wins','h2h_draws']
TR=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23','2023-24']; A_S=['2021-22','2022-23','2023-24']
tr=df[df.season.isin(TR)]; val=df[df.season=='2024-25']
yv=val['y'].values; is_draw=(yv==1)
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def fit(X,y,sw=None): m=xgb.XGBClassifier(**HP); m.fit(X,y,sample_weight=sw); return m
def metrics(P):
    pred=P.argmax(1); acc=(pred==yv).mean()
    dc=int(((pred==1)&is_draw).sum())
    ll=-np.mean([np.log(max(P[i,yv[i]],1e-9)) for i in range(len(yv))])
    return f"{int(acc*380)}/380", dc, round(ll,4)

# ── BASELINE + APPROACH A (class weighting) ─────────────────────────────────────
trA=tr[tr.season.isin(A_S)]
mA=fit(trA[FEAT_A],trA['y']); mB=fit(tr[FEAT_B],tr['y'])
base=0.5*mA.predict_proba(val[FEAT_A])+0.5*mB.predict_proba(val[FEAT_B]); base/=base.sum(1,keepdims=True)
swA=np.where(trA['y'].values==1,2.0,1.0); swB=np.where(tr['y'].values==1,2.0,1.0)
mAw=fit(trA[FEAT_A],trA['y'],swA); mBw=fit(tr[FEAT_B],tr['y'],swB)
appA=0.5*mAw.predict_proba(val[FEAT_A])+0.5*mBw.predict_proba(val[FEAT_B]); appA/=appA.sum(1,keepdims=True)

# ── APPROACH B (two-stage draw gate) ────────────────────────────────────────────
def s1feats(d):
    fd=d['home_form5_ppg']-d['away_form5_ppg']
    return pd.DataFrame({'abs_elo':np.abs(d['elo_diff']),'abs_formdiff':np.abs(fd),
                         'h2h_draw_rate':d['h2h_draws']/d['h2h_n'].clip(lower=1),'formdiff':fd})
s1=xgb.XGBClassifier(objective='binary:logistic',n_estimators=200,max_depth=3,learning_rate=0.05,
                     subsample=0.85,colsample_bytree=0.9,random_state=13,eval_metric='logloss',verbosity=0)
s1.fit(s1feats(tr),(tr['y']==1).astype(int))
pdraw=s1.predict_proba(s1feats(val))[:,1]
def approachB(thr):
    P=np.zeros((len(val),3))
    for i in range(len(val)):
        hw,dw,aw=base[i]; pd_=pdraw[i]; dec=hw+aw
        P[i]=[pd_ if False else (1-pd_)*hw/dec, pd_, (1-pd_)*aw/dec]
    # argmax logic: if pdraw>thr -> force draw, else decisive argmax of home/away
    pred=np.where(pdraw>thr,1,np.where(base[:,0]>=base[:,2],0,2))
    acc=(pred==yv).mean(); dc=int(((pred==1)&is_draw).sum())
    ll=-np.mean([np.log(max(P[i,yv[i]],1e-9)) for i in range(len(yv))])
    return f"{int(acc*380)}/380",dc,round(ll,4),thr

# ── APPROACH C (post-hoc draw floor) ────────────────────────────────────────────
def approachC(P0,ed):
    P=P0.copy()
    for i in range(len(P)):
        h,dd,a=P[i]; e=abs(ed[i]); tgt=None
        if e<30: tgt=0.32
        elif e<50 and dd<0.25: tgt=0.28
        if tgt and dd<tgt:
            rem=1-tgt; s=h+a
            P[i]=[rem*h/s,tgt,rem*a/s]
    return P
appC=approachC(base,val['elo_diff'].values)

print("=== DRAW-BLINDNESS FIXES — validation 2024-25 (93 draws) ===")
print(f"{'Config':<26}{'Accuracy':<11}{'Draws✓':<9}{'Log-loss'}")
for nm,P in [('Baseline (current)',base),('A: class weighting',appA),('C: draw floor',appC)]:
    a,dc,ll=metrics(P); print(f"{nm:<26}{a:<11}{f'{dc}/93':<9}{ll}")
print("--- B: two-stage, threshold sweep ---")
for thr in [0.28,0.32,0.36,0.40]:
    a,dc,ll,t=approachB(thr); print(f"{'B: gate thr='+str(thr):<26}{a:<11}{f'{dc}/93':<9}{ll}")
print("\nNo deployment — dry run.")
