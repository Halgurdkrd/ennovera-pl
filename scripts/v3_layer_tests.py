"""V3 Steps 6/10/12: the BACKTESTABLE comparison — V2 (Elo+Platt) vs Layer 1 (split Elo)
vs LSTM, on validation (2024-25) + holdout (2025-26). Layers 2-4 use current-only FPL data
and cannot be backtested (documented in the report)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import xgboost as xgb
from collections import defaultdict
from sklearn.calibration import CalibratedClassifierCV
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
np.random.seed(13)
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df=pd.read_csv(os.path.join(_ROOT,'data/processed/pl_features.csv')); df['y']=df['ftr'].map({'H':0,'D':1,'A':2})
se=pd.read_csv(os.path.join(_ROOT,'data/v3/split_elo.csv'))
df=df.merge(se[['date','home','away','home_attack_elo','home_defence_elo','away_attack_elo','away_defence_elo']],
            on=['date','home','away'],how='left')
# prev-season position
seasons=sorted(df['season'].unique()); fpos={}
for s in seasons:
    d=df[df.season==s]; pts=defaultdict(float); gd=defaultdict(float)
    for r in d.itertuples():
        if r.fthg>r.ftag: pts[r.home]+=3
        elif r.ftag>r.fthg: pts[r.away]+=3
        else: pts[r.home]+=1; pts[r.away]+=1
        gd[r.home]+=r.fthg-r.ftag; gd[r.away]+=r.ftag-r.fthg
    for i,t in enumerate(sorted(pts,key=lambda t:(-pts[t],-gd[t])),1): fpos[(s,t)]=i
def pp(s,t):
    i=seasons.index(s); return 18 if i==0 else fpos.get((seasons[i-1],t),18)
df['home_prev']=[pp(s,t) for s,t in zip(df.season,df.home)]; df['away_prev']=[pp(s,t) for s,t in zip(df.season,df.away)]
TRAIN=seasons[:7]  # 2016-23
tr=df[df.season.isin(TRAIN)]; cal=df[df.season=='2023-24']; val=df[df.season=='2024-25']; hold=df[df.season=='2025-26']
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def M(P,y):
    P=np.clip(P,1e-9,1); P=P/P.sum(1,keepdims=True); pred=P.argmax(1)
    return int((pred==y).sum()), round(float(-np.mean([np.log(P[i,y[i]]) for i in range(len(y))])),4)
def xgb_platt(feats):
    m=xgb.XGBClassifier(**HP); m.fit(tr[feats],tr['y'])
    c=CalibratedClassifierCV(m,method='sigmoid',cv='prefit'); c.fit(cal[feats],cal['y'])
    return M(c.predict_proba(val[feats]),val['y'].values), M(c.predict_proba(hold[feats]),hold['y'].values)
R={}
R['V2 (Elo+Platt, 3f)']=xgb_platt(['home_elo','away_elo','elo_diff'])
R['Layer1 (split Elo, 6f)']=xgb_platt(['home_attack_elo','home_defence_elo','away_attack_elo','away_defence_elo','home_prev','away_prev'])

# ── LSTM (Step 10): last-10-match sequences per team ────────────────────────────
try:
    import tensorflow as tf; from tensorflow.keras import layers, models
    tf.random.set_seed(13)
    hist=defaultdict(list)  # team -> [ [gf,ga,pts] ]
    def seq(t):
        s=hist[t][-10:]; s=[[0,0,0]]*(10-len(s))+s; return s
    X,Y=[],[]; meta_season=[]
    for r in df.sort_values('date').itertuples():
        X.append(np.concatenate([np.array(seq(r.home)),np.array(seq(r.away))],axis=1))  # (10,6)
        Y.append(r.y); meta_season.append(r.season)
        ph=3 if r.fthg>r.ftag else 1 if r.fthg==r.ftag else 0
        hist[r.home].append([r.fthg,r.ftag,ph]); hist[r.away].append([r.ftag,r.fthg,3-ph if ph!=1 else 1])
    X=np.array(X,dtype='float32')/6.0; Y=np.array(Y); ms=np.array(meta_season)
    tri=np.isin(ms,TRAIN); vi=ms=='2024-25'; hi=ms=='2025-26'
    net=models.Sequential([layers.Input((10,6)),layers.LSTM(64,return_sequences=True),layers.Dropout(0.3),
                           layers.LSTM(32),layers.Dropout(0.3),layers.Dense(3,activation='softmax')])
    net.compile(optimizer='adam',loss='sparse_categorical_crossentropy')
    net.fit(X[tri],Y[tri],validation_data=(X[vi],Y[vi]),epochs=12,batch_size=64,verbose=0)
    R['LSTM (10-match seq)']=(M(net.predict(X[vi],verbose=0),Y[vi]), M(net.predict(X[hi],verbose=0),Y[hi]))
    # XGBoost base + LSTM blend (50/50 on probabilities)
    c=CalibratedClassifierCV(xgb.XGBClassifier(**HP).fit(tr[['home_elo','away_elo','elo_diff']],tr['y']),method='sigmoid',cv='prefit')
    c.fit(cal[['home_elo','away_elo','elo_diff']],cal['y'])
    for nm,mask in [('val',vi),('hold',hi)]:
        pass
    xv=c.predict_proba(val[['home_elo','away_elo','elo_diff']]); xh=c.predict_proba(hold[['home_elo','away_elo','elo_diff']])
    lv=net.predict(X[vi],verbose=0); lh=net.predict(X[hi],verbose=0)
    R['XGBoost + LSTM (50/50)']=(M(0.5*xv+0.5*lv,val['y'].values), M(0.5*xh+0.5*lh,hold['y'].values))
except Exception as e:
    R['LSTM (10-match seq)']=('ERR',str(e)[:40]); R['XGBoost + LSTM (50/50)']=('ERR','')

print("=== V3 BACKTESTABLE COMPARISON — validation (2024-25) + holdout (2025-26) ===")
print(f"{'Config':<26}{'Val acc':<10}{'Val LL':<9}{'Hold acc':<10}{'Hold LL':<9}{'vs V2 hold LL'}")
v2h=R['V2 (Elo+Platt, 3f)'][1][1]
for nm,(v,h) in R.items():
    if isinstance(v,tuple):
        d=h[1]-v2h; print(f"{nm:<26}{f'{v[0]}/380':<10}{v[1]:<9}{f'{h[0]}/380':<10}{h[1]:<9}{d:+.4f}")
    else:
        print(f"{nm:<26}{str(v):<10}{h}")
print(f"{'Bet365 (benchmark)':<26}{'-':<10}{'-':<9}{'186/380':<10}{'1.0185':<9}reference")
print("\nLayers 2-4 (strength/xG/availability): CURRENT-only FPL data -> NOT backtestable. Built as")
print("live-season overlays (see v3_overlays.py + report). No holdout numbers can be honestly claimed.")
json.dump({k:(list(v) if isinstance(v[0],tuple) else v) for k,v in R.items()},
          open(os.path.join(_ROOT,'data/experiments/v3_layer_tests.json') if os.path.isdir(os.path.join(_ROOT,'data/experiments')) else os.path.join(_ROOT,'data/v3/v3_layer_tests.json'),'w'),indent=1,default=str)
print("saved v3_layer_tests.json")
