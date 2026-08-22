"""Phase 3: PL match-outcome ensemble (Model A specialist + Model B generalist),
mirroring the WC2026 architecture. Chronological split, no host/knockout adjustments
(PL has real home advantage + no knockouts). Run from ennovera-pl/ ."""
import pandas as pd, numpy as np, glob, os, sys, json, pickle
from collections import defaultdict, deque
import xgboost as xgb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team_aliases import canonicalize, PL_2026_27

OUT='data/models'; PRED='data/predictions'; REP='reports'
for d in (OUT,PRED,REP): os.makedirs(d, exist_ok=True)
np.random.seed(13)

# ── STEP 1: load + chronological split ──────────────────────────────────────────
df=pd.read_csv('data/processed/pl_features.csv')
ENC={'H':0,'D':1,'A':2}; LAB={0:'home',1:'draw',2:'away'}
df['y']=df['ftr'].map(ENC)
NONFEAT={'date','season','home','away','fthg','ftag','ftr','y'}
FEAT_A=[c for c in df.columns if c not in NONFEAT]
FEAT_B=['home_elo','away_elo','elo_diff','home_form5_ppg','away_form5_ppg','home_form5_gf','away_form5_gf',
        'home_form5_ga','away_form5_ga','home_form10_ppg','away_form10_ppg','home_athome_ppg','away_ataway_ppg',
        'h2h_home_wins','h2h_away_wins','h2h_draws']
TRAIN_SEASONS=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23','2023-24']
A_SEASONS=['2021-22','2022-23','2023-24']
VAL='2024-25'; HOLD='2025-26'
tr=df[df.season.isin(TRAIN_SEASONS)]; val=df[df.season==VAL]; hold=df[df.season==HOLD]
print("=== STEP 1: split ===")
for nm,d in [('train(2016-24)',tr),('val(2024-25)',val),('holdout(2025-26)',hold)]:
    vc=d['ftr'].value_counts().to_dict(); print(f"  {nm}: {len(d)} rows  H/D/A = {vc.get('H',0)}/{vc.get('D',0)}/{vc.get('A',0)}")

HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,
        subsample=0.8,colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def train(Xtr,ytr,Xval,yval):
    m=xgb.XGBClassifier(early_stopping_rounds=50,**HP)
    m.fit(Xtr,ytr,eval_set=[(Xval,yval)],verbose=False); return m
def acc(m,X,y): return (m.predict(X)==y.values).mean()
def imp(m,feats,k=10):
    return sorted(zip(feats,m.feature_importances_),key=lambda x:-x[1])[:k]

# ── STEP 2: Model A (specialist) ────────────────────────────────────────────────
mA=train(tr[tr.season.isin(A_SEASONS)][FEAT_A],tr[tr.season.isin(A_SEASONS)]['y'],val[FEAT_A],val['y'])
print("\n=== STEP 2: Model A (specialist, 2021-24, 42 feat) ===")
print(f"  train acc {acc(mA,tr[tr.season.isin(A_SEASONS)][FEAT_A],tr[tr.season.isin(A_SEASONS)]['y'])*100:.1f}% | val acc {acc(mA,val[FEAT_A],val['y'])*100:.1f}%")
print("  top feats:", [f'{f}:{v:.3f}' for f,v in imp(mA,FEAT_A)])
pickle.dump(mA,open(f'{OUT}/pl_model_a_specialist.pkl','wb'))

# ── STEP 3: Model B (generalist) ────────────────────────────────────────────────
mB=train(tr[FEAT_B],tr['y'],val[FEAT_B],val['y'])
print("\n=== STEP 3: Model B (generalist, 2016-24, 16 feat) ===")
print(f"  train acc {acc(mB,tr[FEAT_B],tr['y'])*100:.1f}% | val acc {acc(mB,val[FEAT_B],val['y'])*100:.1f}%")
print("  top feats:", [f'{f}:{v:.3f}' for f,v in imp(mB,FEAT_B)])
pickle.dump(mB,open(f'{OUT}/pl_model_b_generalist.pkl','wb'))

# ── STEP 4-6: ensemble + corrections ────────────────────────────────────────────
HFA=100
def elo_prior(he,ae):
    e=1/(1+10**((ae-he-HFA)/400)); return np.array([e*0.74,0.26,(1-e)*0.74])
def temp(p,T):
    lp=np.log(np.clip(p,1e-9,1)); s=np.exp(lp/T); return s/s.sum()
FPL_STRENGTH={'Arsenal':5,'Manchester City':5,'Liverpool':5,'Chelsea':4,'Manchester United':4,'Tottenham':4,
 'Newcastle United':4,'Aston Villa':4,'Brighton and Hove Albion':3,'Bournemouth':3,'Brentford':3,'Crystal Palace':3,
 'Fulham':3,'Nottingham Forest':3,'Everton':3,'Leeds United':3,'Ipswich Town':2,'Sunderland':2,'Hull City':2,'Coventry City':2}
def predict_rows(D,wA=0.5,wB=0.5,T=1.0,promoted=False,fpl=False):
    pa=mA.predict_proba(D[FEAT_A]); pb=mB.predict_proba(D[FEAT_B]); out=[]
    for i,(ix,r) in enumerate(D.iterrows()):
        p=wA*pa[i]+wB*pb[i]; p=p/p.sum(); e=temp(p,T)
        if promoted:  # Hybrid-style: cold-start teams -> blend toward Elo prior
            al=1.0
            if r['home_elo']<1350 and r['home_form5_n']<5: al-=0.15
            if r['away_elo']<1350 and r['away_form5_n']<5: al-=0.15
            if al<0.999: e=al*e+(1-al)*elo_prior(r['home_elo'],r['away_elo']); e=e/e.sum()
        if fpl:
            sh=FPL_STRENGTH.get(r['home']); sa=FPL_STRENGTH.get(r['away'])
            if sh is not None and sa is not None and abs(sh-sa)>=2:
                b=(sh-sa)*0.02; e=np.array([e[0]+b,e[1],e[2]-b]); e=np.clip(e,0.01,None); e=e/e.sum()
        out.append(e)
    return np.array(out)
def metrics(P,y):
    yv=y.values; pred=P.argmax(1); a=(pred==yv).mean()
    ll=-np.mean([np.log(max(P[i,yv[i]],1e-9)) for i in range(len(yv))])
    oh=np.eye(3)[yv]; br=np.mean(np.sum((P-oh)**2,axis=1))
    return a,ll,br

# ── STEP 7: validate all configs ────────────────────────────────────────────────
print("\n=== STEP 7: validation (2024-25, 380) ===")
print(f"{'config':<34}{'acc':<10}{'log-loss':<11}{'brier'}")
def paP(D): return mA.predict_proba(D[FEAT_A])
def pbP(D): return mB.predict_proba(D[FEAT_B])
CFG={'Model A solo':paP(val),'Model B solo':pbP(val),
     'Ensemble 50/50':predict_rows(val),
     'Ensemble + promoted corr':predict_rows(val,promoted=True),
     'Ensemble + FPL boost':predict_rows(val,fpl=True),
     'Ensemble + both':predict_rows(val,promoted=True,fpl=True)}
valres={}
for nm,P in CFG.items():
    a,ll,br=metrics(P,val['y']); valres[nm]=(a,ll,br)
    print(f"{nm:<34}{f'{int(a*380)}/380':<10}{ll:<11.4f}{br:.4f}")
# per-class + confusion + calibration for the ensemble+both
P=CFG['Ensemble + both']; yv=val['y'].values; pred=P.argmax(1)
conf=np.zeros((3,3),int)
for t,pp in zip(yv,pred): conf[t,pp]+=1
print("\n  per-class recall (Ensemble+both):", {LAB[c]:f'{conf[c,c]}/{conf[c].sum()}' for c in range(3)})
print("  confusion [true x pred] home/draw/away:");
for c in range(3): print("   ",LAB[c],conf[c].tolist())
conf_mask=P.max(1)>=0.60
print(f"  calibration: predicted>=60% -> {conf_mask.sum()} matches, actual correct {(pred[conf_mask]==yv[conf_mask]).mean()*100:.0f}%")

# ── STEP 11 + 12: temperature + blend sweeps ────────────────────────────────────
print("\n=== STEP 11: temperature sweep (val) ===")
for T in [0.8,1.0,1.25,1.5,2.0]:
    a,ll,br=metrics(predict_rows(val,T=T),val['y']); print(f"  T={T}: acc {int(a*380)}/380  ll {ll:.4f}  brier {br:.4f}")
print("=== STEP 12: blend sweep A/B (val) ===")
best_w=(0.5,0.5); best=(0,9)
for wA in [0.4,0.5,0.6,0.7]:
    a,ll,br=metrics(predict_rows(val,wA=wA,wB=1-wA),val['y']); print(f"  {int(wA*100)}/{int((1-wA)*100)}: acc {int(a*380)}/380  ll {ll:.4f}")
    if ll<best[1]: best=(a,ll); best_w=(wA,1-wA)

# ── STEP 8: holdout test (best config = Ensemble+both, best blend) ───────────────
bestcfg=min(valres,key=lambda k:valres[k][1])
print(f"\n=== STEP 8: HOLDOUT 2025-26 — best config '{bestcfg}', blend {best_w} ===")
Ph=predict_rows(hold,wA=best_w[0],wB=best_w[1],promoted=True,fpl=True)
ah,llh,brh=metrics(Ph,hold['y']); av=valres['Ensemble + both'][0]
print(f"  holdout acc {int(ah*380)}/380 ({ah*100:.1f}%)  ll {llh:.4f}  brier {brh:.4f}")
print(f"  validation was {av*100:.1f}% -> gap {abs(ah-av)*100:.1f}pp -> {'STABLE' if abs(ah-av)<0.03 else 'check overfit'}")

# ── STEP 9: retrain final on ALL data ───────────────────────────────────────────
alld=df  # 2016-26
A_FINAL=['2021-22','2022-23','2023-24','2024-25','2025-26']
mAf=xgb.XGBClassifier(**HP); mAf.fit(alld[alld.season.isin(A_FINAL)][FEAT_A],alld[alld.season.isin(A_FINAL)]['y'])
mBf=xgb.XGBClassifier(**HP); mBf.fit(alld[FEAT_B],alld['y'])
pickle.dump(mAf,open(f'{OUT}/pl_model_a_final.pkl','wb')); pickle.dump(mBf,open(f'{OUT}/pl_model_b_final.pkl','wb'))
print("\n=== STEP 9: retrained final models (A 2021-26, B 2016-26) saved ===")

# ── STEP 10: GW2 predictions (cold-start pre-season estimate) ────────────────────
print("\n=== STEP 10: GW2 2026-27 predictions ===")
cur=pd.read_csv('data/processed/current_elo.csv').set_index('team')
# each team's most-recent form row (end of 2025-26) as the carried pre-season state
last_state={}
for _,r in df.sort_values('date').iterrows():
    for side in ('home','away'):
        t=r[side]; pre='home_' if side=='home' else 'away_'
        last_state[t]={k.replace(pre,''):r[k] for k in df.columns if k.startswith(pre) and k not in('home','away')}
def gw2_feat(h,a):
    hs=last_state.get(h,{}); as_=last_state.get(a,{})
    he=cur.loc[h,'derived_elo'] if h in cur.index else 1300.0; ae=cur.loc[a,'derived_elo'] if a in cur.index else 1300.0
    row={'home_elo':he,'away_elo':ae,'elo_diff':he-ae,'home_pos':10,'away_pos':10,'pos_diff':0,'home_played':0,'away_played':0,
         'h2h_home_wins':0,'h2h_away_wins':0,'h2h_draws':0,'h2h_n':0}
    for k in ['form5_ppg','form5_gf','form5_ga','form5_cs','form5_n','form10_ppg','form10_gf','form10_ga','form10_cs','form10_n','athome_ppg','athome_gf','athome_ga','athome_cs','athome_n']:
        row[f'home_{k}']=hs.get(k,0.0); row[f'away_{k}']=as_.get(k,0.0)
    row['away_ataway_ppg']=as_.get('ataway_ppg',as_.get('athome_ppg',0.0))
    for k in ['ataway_gf','ataway_ga','ataway_cs','ataway_n']: row[f'away_{k}']=as_.get(k,0.0)
    return row
def predict_one(h,a):
    r=pd.Series(gw2_feat(h,a)); r['home']=h; r['away']=a
    D=pd.DataFrame([r]);
    for c in FEAT_A:
        if c not in D.columns: D[c]=0.0
    P=predict_rows(D,wA=best_w[0],wB=best_w[1],promoted=True,fpl=True)[0]; return P
# GW2 fixtures from FPL
fx=json.load(open('data/raw/fpl/fixtures.json',encoding='utf-8'))
bs=json.load(open('data/raw/fpl/bootstrap_static.json',encoding='utf-8'))
id2name={t['id']:canonicalize(t['name']) for t in bs['teams']}
gw2=[f for f in fx if f.get('event')==2]
gw2preds=[]
print(f"{'Match':<44}{'Home%':<7}{'Draw%':<7}{'Away%':<7}{'Pick'}")
for f in gw2:
    h=id2name.get(f['team_h']); a=id2name.get(f['team_a'])
    if not h or not a: continue
    P=predict_one(h,a); pick=LAB[int(P.argmax())]
    gw2preds.append({'home':h,'away':a,'home_pct':round(float(P[0])*100,1),'draw_pct':round(float(P[1])*100,1),'away_pct':round(float(P[2])*100,1),'pick':pick})
    print(f"{h+' vs '+a:<44}{P[0]*100:5.1f}  {P[1]*100:5.1f}  {P[2]*100:5.1f}  {pick}")
json.dump({'gameweek':2,'model':'PL Ensemble A/B + promoted corr + FPL boost','blend':best_w,'predictions':gw2preds},
          open(f'{PRED}/gw2_predictions.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
print(f"\nsaved {len(gw2preds)} GW2 predictions")

# ── save report data ────────────────────────────────────────────────────────────
rep={'val_results':{k:{'acc':round(v[0],4),'logloss':round(v[1],4),'brier':round(v[2],4)} for k,v in valres.items()},
     'holdout':{'acc':round(ah,4),'logloss':round(llh,4),'brier':round(brh,4),'val_acc':round(av,4)},
     'best_config':bestcfg,'best_blend':best_w,
     'model_a_top_feats':[[f,round(float(v),4)] for f,v in imp(mA,FEAT_A)],
     'model_b_top_feats':[[f,round(float(v),4)] for f,v in imp(mB,FEAT_B)],
     'gw2':gw2preds}
json.dump(rep,open(f'{PRED}/training_summary.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
print("saved training_summary.json")
