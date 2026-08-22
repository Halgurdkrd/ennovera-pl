"""Phase 3b: confirm the two-stage draw model on the 2025-26 holdout, then retrain
finals on ALL data with the chosen config and regenerate GW2 predictions."""
import pandas as pd, numpy as np, os, sys, json, pickle
import xgboost as xgb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team_aliases import canonicalize
np.random.seed(13)
OUT='data/models'; PRED='data/predictions'
df=pd.read_csv('data/processed/pl_features.csv')
ENC={'H':0,'D':1,'A':2}; df['y']=df['ftr'].map(ENC)
NONFEAT={'date','season','home','away','fthg','ftag','ftr','y'}
FEAT_A=[c for c in df.columns if c not in NONFEAT]
FEAT_B=['home_elo','away_elo','elo_diff','home_form5_ppg','away_form5_ppg','home_form5_gf','away_form5_gf',
        'home_form5_ga','away_form5_ga','home_form10_ppg','away_form10_ppg','home_athome_ppg','away_ataway_ppg',
        'h2h_home_wins','h2h_away_wins','h2h_draws']
TR=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23','2023-24']; A_S=['2021-22','2022-23','2023-24']
tr=df[df.season.isin(TR)]; val=df[df.season=='2024-25']; hold=df[df.season=='2025-26']
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def fitm(X,y): m=xgb.XGBClassifier(**HP); m.fit(X,y); return m
def s1feats(d):
    fd=d['home_form5_ppg']-d['away_form5_ppg']
    return pd.DataFrame({'abs_elo':np.abs(d['elo_diff']),'abs_formdiff':np.abs(fd),
                         'h2h_draw_rate':d['h2h_draws']/d['h2h_n'].clip(lower=1),'formdiff':fd})
def s1fit(X,y):
    m=xgb.XGBClassifier(objective='binary:logistic',n_estimators=200,max_depth=3,learning_rate=0.05,
                        subsample=0.85,colsample_bytree=0.9,random_state=13,eval_metric='logloss',verbosity=0)
    m.fit(X,y); return m
mA=fitm(tr[tr.season.isin(A_S)][FEAT_A],tr[tr.season.isin(A_S)]['y']); mB=fitm(tr[FEAT_B],tr['y'])
s1=s1fit(s1feats(tr),(tr['y']==1).astype(int))
def base_probs(D):
    p=0.5*mA.predict_proba(D[FEAT_A])+0.5*mB.predict_proba(D[FEAT_B]); return p/p.sum(1,keepdims=True)
def evalset(D):
    y=D['y'].values; P=base_probs(D); pdraw=s1.predict_proba(s1feats(D))[:,1]
    # two-stage prob (threshold-invariant) for log-loss
    dec=P[:,0]+P[:,2]; TS=np.stack([(1-pdraw)*P[:,0]/dec,pdraw,(1-pdraw)*P[:,2]/dec],1)
    def m(pred):
        acc=(pred==y).mean(); dc=int(((pred==1)&(y==1)).sum()); return int(acc*len(y)),dc
    base_pred=P.argmax(1); b_acc,b_dc=m(base_pred)
    b_ll=-np.mean([np.log(max(P[i,y[i]],1e-9)) for i in range(len(y))])
    ts_ll=-np.mean([np.log(max(TS[i,y[i]],1e-9)) for i in range(len(y))])
    out={'n':len(y),'ndraw':int((y==1).sum()),'base':(b_acc,b_dc,round(b_ll,4))}
    for thr in [0.32,0.36,0.40]:
        pred=np.where(pdraw>thr,1,np.where(P[:,0]>=P[:,2],0,2)); a,d=m(pred); out[thr]=(a,d,round(ts_ll,4))
    return out
V=evalset(val); H=evalset(hold)
print("=== Two-stage: validation vs HOLDOUT ===")
print(f"{'Config':<16}{'Val acc':<12}{'Val draws':<12}{'Hold acc':<13}{'Hold draws':<12}{'Hold ll':<9}{'consistent'}")
def line(name,vk,hk):
    va,vd,_=V[vk]; ha,hd,hll=H[hk]; gap=abs(va/V['n']-ha/H['n'])*100
    vacc=f"{va}/{V['n']}"; vdr=f"{vd}/{V['ndraw']}"; hacc=f"{ha}/{H['n']}"; hdr=f"{hd}/{H['ndraw']}"
    cons='YES' if gap<3 else f'no ({gap:.1f}pp)'
    print(f"{name:<16}{vacc:<12}{vdr:<12}{hacc:<13}{hdr:<12}{hll:<9}{cons}")
line('Baseline','base','base')
for thr in [0.32,0.36,0.40]: line(f'B t={thr}',thr,thr)

# choose threshold by best VALIDATION accuracy (clean), confirm on holdout
best_thr=max([0.32,0.36,0.40],key=lambda t:V[t][0])
print(f"\nChosen threshold (best val accuracy): {best_thr}  -> holdout {H[best_thr][0]}/{H['n']}")

# ── retrain FINAL on ALL data with two-stage ────────────────────────────────────
A_FINAL=['2021-22','2022-23','2023-24','2024-25','2025-26']
mAf=fitm(df[df.season.isin(A_FINAL)][FEAT_A],df[df.season.isin(A_FINAL)]['y'])
mBf=fitm(df[FEAT_B],df['y']); s1f=s1fit(s1feats(df),(df['y']==1).astype(int))
pickle.dump(mAf,open(f'{OUT}/pl_model_a_final.pkl','wb')); pickle.dump(mBf,open(f'{OUT}/pl_model_b_final.pkl','wb'))
pickle.dump(s1f,open(f'{OUT}/pl_draw_gate_final.pkl','wb'))
pickle.dump({'threshold':best_thr},open(f'{OUT}/pl_twostage_config.pkl','wb'))
print("saved finals: pl_model_a_final, pl_model_b_final, pl_draw_gate_final (+ config)")

# ── regenerate GW2 with two-stage ───────────────────────────────────────────────
cur=pd.read_csv('data/processed/current_elo.csv').set_index('team')
last_state={}
for _,r in df.sort_values('date').iterrows():
    for side in ('home','away'):
        pre='home_' if side=='home' else 'away_'
        last_state[r[side]]={k.replace(pre,''):r[k] for k in df.columns if k.startswith(pre) and k not in('home','away')}
def gw2_row(h,a):
    hs=last_state.get(h,{}); as_=last_state.get(a,{})
    he=cur.loc[h,'derived_elo'] if h in cur.index else 1300.0; ae=cur.loc[a,'derived_elo'] if a in cur.index else 1300.0
    row={'home_elo':he,'away_elo':ae,'elo_diff':he-ae,'home_pos':10,'away_pos':10,'pos_diff':0,'home_played':0,'away_played':0,
         'h2h_home_wins':0,'h2h_away_wins':0,'h2h_draws':0,'h2h_n':0}
    for k in ['form5_ppg','form5_gf','form5_ga','form5_cs','form5_n','form10_ppg','form10_gf','form10_ga','form10_cs','form10_n','athome_ppg','athome_gf','athome_ga','athome_cs','athome_n']:
        row[f'home_{k}']=hs.get(k,0.0); row[f'away_{k}']=as_.get(k,0.0)
    row['away_ataway_ppg']=as_.get('ataway_ppg',as_.get('athome_ppg',0.0))
    for k in ['ataway_gf','ataway_ga','ataway_cs','ataway_n']: row[f'away_{k}']=as_.get(k,0.0)
    return row
def predict_gw2(h,a):
    r=pd.Series(gw2_row(h,a)); D=pd.DataFrame([r])
    for c in FEAT_A:
        if c not in D.columns: D[c]=0.0
    p=0.5*mAf.predict_proba(D[FEAT_A])+0.5*mBf.predict_proba(D[FEAT_B]); p=p[0]/p[0].sum()
    pdraw=float(s1f.predict_proba(s1feats(D))[0,1]); dec=p[0]+p[2]
    TS=np.array([(1-pdraw)*p[0]/dec,pdraw,(1-pdraw)*p[2]/dec])
    pick='draw' if pdraw>best_thr else ('home' if p[0]>=p[2] else 'away')
    return TS,pick
fx=json.load(open('data/raw/fpl/fixtures.json',encoding='utf-8')); bs=json.load(open('data/raw/fpl/bootstrap_static.json',encoding='utf-8'))
id2n={t['id']:canonicalize(t['name']) for t in bs['teams']}
gw2=[f for f in fx if f.get('event')==2]; preds=[]
print(f"\n=== GW2 (two-stage, thr={best_thr}) ===")
print(f"{'Match':<44}{'H%':<6}{'D%':<6}{'A%':<6}{'Pick'}")
for f in gw2:
    h=id2n.get(f['team_h']); a=id2n.get(f['team_a'])
    if not h or not a: continue
    P,pick=predict_gw2(h,a)
    preds.append({'home':h,'away':a,'home_pct':round(float(P[0])*100,1),'draw_pct':round(float(P[1])*100,1),'away_pct':round(float(P[2])*100,1),'pick':pick})
    print(f"{h+' vs '+a:<44}{P[0]*100:4.0f}  {P[1]*100:4.0f}  {P[2]*100:4.0f}  {pick}")
json.dump({'gameweek':2,'model':f'PL two-stage ensemble (draw gate thr={best_thr})','predictions':preds},
          open(f'{PRED}/gw2_predictions.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
print(f"\nsaved {len(preds)} GW2 predictions (two-stage). No further deployment.")
