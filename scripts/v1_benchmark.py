"""V1 final benchmark on the 2025-26 holdout: Elo-only, home-always, bookmaker (Bet365),
vs our V1 ensemble. Answers: do 49 features beat Elo? how far from bookmakers?"""
import pandas as pd, numpy as np, os, sys
import xgboost as xgb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team_aliases import canonicalize
np.random.seed(13)
df=pd.read_csv('data/processed/pl_features.csv')
ENC={'H':0,'D':1,'A':2}; df['y']=df['ftr'].map(ENC)
NONFEAT={'date','season','home','away','fthg','ftag','ftr','y'}
FEAT_A=[c for c in df.columns if c not in NONFEAT]
FEAT_B=['home_elo','away_elo','elo_diff','home_form5_ppg','away_form5_ppg','home_form5_gf','away_form5_gf',
        'home_form5_ga','away_form5_ga','home_form10_ppg','away_form10_ppg','home_athome_ppg','away_ataway_ppg',
        'h2h_home_wins','h2h_away_wins','h2h_draws']
TR=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23','2023-24']; A_S=['2021-22','2022-23','2023-24']
tr=df[df.season.isin(TR)]; hold=df[df.season=='2025-26'].reset_index(drop=True)
yh=hold['y'].values; ndraw=int((yh==1).sum()); N=len(hold)
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def fitm(X,y,feats): m=xgb.XGBClassifier(**HP); m.fit(X[feats],y); return m
def M(P):
    P=np.clip(P,1e-9,1); P=P/P.sum(1,keepdims=True); pred=P.argmax(1)
    acc=int((pred==yh).sum()); dc=int(((pred==1)&(yh==1)).sum())
    ll=-np.mean([np.log(P[i,yh[i]]) for i in range(N)])
    oh=np.eye(3)[yh]; br=np.mean(np.sum((P-oh)**2,1))
    return acc,round(ll,4),round(br,4),dc

# 1) Elo-only (3 features)
mE=fitm(tr,tr['y'],['home_elo','away_elo','elo_diff'])
Pelo=mE.predict_proba(hold[['home_elo','away_elo','elo_diff']])
# 2) Random + home-always (base-rate prob)
base_rate=np.array([ (tr['y']==0).mean(),(tr['y']==1).mean(),(tr['y']==2).mean() ])
Prand=np.tile([1/3,1/3,1/3],(N,1)); Phome=np.tile(base_rate,(N,1))
# 3) V1 ensemble (Model A 42 + Model B 16)
mA=fitm(tr[tr.season.isin(A_S)],tr[tr.season.isin(A_S)]['y'],FEAT_A); mB=fitm(tr,tr['y'],FEAT_B)
Pv1=0.5*mA.predict_proba(hold[FEAT_A])+0.5*mB.predict_proba(hold[FEAT_B])
# 4) Bookmaker (Bet365) from raw 2025-26 CSV
raw=pd.read_csv('data/raw/pl_history/E0_2025-26.csv',encoding='latin-1')
odds_cols=('B365H','B365D','B365A') if 'B365H' in raw.columns else ('AvgH','AvgD','AvgA')
raw=raw.dropna(subset=list(odds_cols)+['FTR'])
imp=np.vstack([1/raw[odds_cols[0]],1/raw[odds_cols[1]],1/raw[odds_cols[2]]]).T
imp=imp/imp.sum(1,keepdims=True)
ybook=raw['FTR'].map(ENC).values
def Mbook(P,y):
    pred=P.argmax(1); acc=int((pred==y).sum()); nd=int((y==1).sum()); dc=int(((pred==1)&(y==1)).sum())
    ll=-np.mean([np.log(max(P[i,y[i]],1e-9)) for i in range(len(y))])
    oh=np.eye(3)[y]; br=np.mean(np.sum((P-oh)**2,1)); return acc,len(y),round(ll,4),round(br,4),dc,nd
ba,bn,bll,bbr,bdc,bnd=Mbook(imp,ybook)

print(f"=== V1 BENCHMARK — 2025-26 holdout ({N} matches, {ndraw} draws) ===")
print(f"Bookmaker odds source: {odds_cols[0][:-1]} ({bn} matches with odds)\n")
print(f"{'Config':<22}{'Accuracy':<14}{'Log-loss':<11}{'Brier':<9}{'Draw recall'}")
def row(nm,P):
    a,ll,br,dc=M(P); print(f"{nm:<22}{f'{a}/{N} ({a/N*100:.0f}%)':<14}{ll:<11}{br:<9}{dc}/{ndraw}")
row('Random',Prand)
a,ll,br,dc=M(Phome); hacc=f"{int((yh==0).sum())}/{N} ({(yh==0).mean()*100:.0f}%)"
print(f"{'Home-always':<22}{hacc:<14}{ll:<11}{br:<9}0/{ndraw}")
row('Elo-only (3 feat)',Pelo)
row('Our V1 ensemble',Pv1)
print(f"{'Bookmaker (Bet365)':<22}{f'{ba}/{bn} ({ba/bn*100:.0f}%)':<14}{bll:<11}{bbr:<9}{bdc}/{bnd}")

# analysis numbers for the report
v1=M(Pv1); elo=M(Pelo)
print(f"\n-- V1 vs Elo-only: {v1[0]} vs {elo[0]} correct  (49-feat gain: {v1[0]-elo[0]:+d} matches)")
print(f"-- V1 vs Bookmaker: {v1[0]/N*100:.1f}% vs {ba/bn*100:.1f}%  (gap: {ba/bn*100 - v1[0]/N*100:.1f}pp)")
print(f"-- V1 vs Elo log-loss: {v1[1]} vs {elo[1]}  | Bookmaker log-loss: {bll}")
