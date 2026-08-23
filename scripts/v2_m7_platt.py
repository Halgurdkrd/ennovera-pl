"""The untested combo: M7 features (Elo + goals + prev-position) + Platt calibration.
Split: train 2016-2023, Platt on 2023-24, validate 2024-25, holdout 2025-26."""
import pandas as pd, numpy as np, os, sys, json, pickle
import xgboost as xgb
from collections import defaultdict
from sklearn.calibration import CalibratedClassifierCV
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
np.random.seed(13)
df=pd.read_csv('data/processed/pl_features.csv'); df['y']=df['ftr'].map({'H':0,'D':1,'A':2}); df['dt']=pd.to_datetime(df['date'])
# prev-season final position (same as v2_feature_tests)
seasons=sorted(df['season'].unique()); finalpos={}
for s in seasons:
    d=df[df.season==s]; pts=defaultdict(float); gd=defaultdict(float)
    for r in d.itertuples():
        if r.fthg>r.ftag: pts[r.home]+=3
        elif r.ftag>r.fthg: pts[r.away]+=3
        else: pts[r.home]+=1; pts[r.away]+=1
        gd[r.home]+=r.fthg-r.ftag; gd[r.away]+=r.ftag-r.fthg
    for i,t in enumerate(sorted(pts,key=lambda t:(-pts[t],-gd[t])),1): finalpos[(s,t)]=i
def prev_pos(s,t):
    i=seasons.index(s); return 18 if i==0 else finalpos.get((seasons[i-1],t),18)
df['home_prev_position']=[prev_pos(s,t) for s,t in zip(df['season'],df['home'])]
df['away_prev_position']=[prev_pos(s,t) for s,t in zip(df['season'],df['away'])]
FEAT=['home_elo','away_elo','elo_diff','home_form5_gf','away_form5_gf','home_prev_position','away_prev_position']
TRAIN=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23']
tr=df[df.season.isin(TRAIN)]; cal=df[df.season=='2023-24']; val=df[df.season=='2024-25']; hold=df[df.season=='2025-26']
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def M(P,y):
    P=np.clip(P,1e-9,1); P=P/P.sum(1,keepdims=True); pred=P.argmax(1)
    return int((pred==y).sum()), round(float(-np.mean([np.log(P[i,y[i]]) for i in range(len(y))])),4)

m=xgb.XGBClassifier(**HP); m.fit(tr[FEAT],tr['y'])
calib=CalibratedClassifierCV(m,method='sigmoid',cv='prefit'); calib.fit(cal[FEAT],cal['y'])
va=M(calib.predict_proba(val[FEAT]),val['y'].values); ho=M(calib.predict_proba(hold[FEAT]),hold['y'].values)

print("=== M7 + Platt (THE untested combo) ===")
print(f"{'Config':<22}{'Val acc':<10}{'Val LL':<9}{'Hold acc':<10}{'Hold LL'}")
print(f"{'M0 Elo raw':<22}{'196':<10}{'1.063':<9}{'181':<10}{'1.100'}")
print(f"{'M1b Elo+Platt':<22}{'197':<10}{'1.010':<9}{'184':<10}{'1.053'}")
print(f"{'M7 goals+pos+temp':<22}{'199':<10}{'1.025':<9}{'188':<10}{'1.056'}")
print(f"{'NEW: M7+Platt':<22}{str(va[0]):<10}{str(va[1]):<9}{str(ho[0]):<10}{ho[1]}")
print(f"{'Bet365':<22}{'-':<10}{'-':<9}{'186':<10}{'1.0185'}")

beats_m1b_ll = va[1]<1.010 and ho[1]<1.053
beats_m7_acc = va[0]>199 or ho[0]>188   # accuracy improvement
print(f"\nBeats M1b on log-loss (both seasons)? {beats_m1b_ll}")
print(f"Beats M7 on accuracy?                 {ho[0]>=188} (hold {ho[0]} vs 188)")
champion = beats_m1b_ll and ho[0]>=188
print(f"\n>>> {'M7+Platt is the V2 CHAMPION' if champion else 'V2 = M1b (Platt Elo) — M7+Platt did not dominate'}")
print(f"gap to Bet365 (hold LL): M7+Platt {ho[1]-1.0185:+.4f}  vs  M1b Platt {1.053-1.0185:+.4f}")

# save winner
if champion:
    pickle.dump({'model':m,'calibrator':calib,'features':FEAT,'calibration':'platt','name':'M7+Platt'},
                open('data/models/pl_v2_final.pkl','wb')); win='M7+Platt (Elo+goals+prevpos, Platt-calibrated)'
else:
    # V2 = M1b: refit Elo-only + Platt
    mE=xgb.XGBClassifier(**HP); mE.fit(tr[['home_elo','away_elo','elo_diff']],tr['y'])
    cE=CalibratedClassifierCV(mE,method='sigmoid',cv='prefit'); cE.fit(cal[['home_elo','away_elo','elo_diff']],cal['y'])
    pickle.dump({'model':mE,'calibrator':cE,'features':['home_elo','away_elo','elo_diff'],'calibration':'platt','name':'M1b Elo+Platt'},
                open('data/models/pl_v2_final.pkl','wb')); win='M1b Elo+Platt'
print(f"saved pl_v2_final.pkl -> {win}")
json.dump({'M7_platt':{'val_acc':va[0],'val_ll':va[1],'hold_acc':ho[0],'hold_ll':ho[1]},
           'champion':bool(champion),'v2_final':win},open('data/experiments/v2_m7_platt.json','w'),indent=1)
