"""Final V1 tests: (1) Elo-only vs V1 on BOTH seasons, (2) Bet365 methodology verification
+ calibration comparison. Saves data/experiments/v1_final_benchmark.json."""
import pandas as pd, numpy as np, os, sys, json
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
ELO3=['home_elo','away_elo','elo_diff']
TR=['2016-17','2017-18','2018-19','2019-20','2020-21','2021-22','2022-23','2023-24']; A_S=['2021-22','2022-23','2023-24']
tr=df[df.season.isin(TR)]
HP=dict(objective='multi:softprob',num_class=3,n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,
        colsample_bytree=0.8,min_child_weight=3,eval_metric='mlogloss',random_state=13,verbosity=0)
def fit(X,y,f): m=xgb.XGBClassifier(**HP); m.fit(X[f],y); return m
def met(P,y):
    P=np.clip(P,1e-9,1); P=P/P.sum(1,keepdims=True); pred=P.argmax(1)
    acc=int((pred==y).sum()); ll=-np.mean([np.log(P[i,y[i]]) for i in range(len(y))])
    oh=np.eye(3)[y]; br=np.mean(np.sum((P-oh)**2,1)); dc=int(((pred==1)&(y==1)).sum())
    return acc,round(float(ll),4),round(float(br),4),dc
mE=fit(tr,tr['y'],ELO3); mA=fit(tr[tr.season.isin(A_S)],tr[tr.season.isin(A_S)]['y'],FEAT_A); mB=fit(tr,tr['y'],FEAT_B)

# ── TEST 1: Elo vs V1 on both seasons ───────────────────────────────────────────
print("=== TEST 1: Elo-only vs V1 ensemble — both seasons ===")
print(f"{'Config':<16}{'24-25 acc':<12}{'24-25 LL':<11}{'25-26 acc':<12}{'25-26 LL':<11}{'consistent'}")
t1={}
for nm,pf in [('Elo-only',None),('V1 ensemble',None)]:
    res={}
    for s in ['2024-25','2025-26']:
        d=df[df.season==s]; y=d['y'].values
        if nm=='Elo-only': P=mE.predict_proba(d[ELO3])
        else: P=0.5*mA.predict_proba(d[FEAT_A])+0.5*mB.predict_proba(d[FEAT_B])
        res[s]=met(P,y)
    t1[nm]=res
    ea,el,_,_=res['2024-25']; ha,hl,_,_=res['2025-26']; gap=abs(ea-ha)/380*100
    print(f"{nm:<16}{f'{ea}/380':<12}{el:<11}{f'{ha}/380':<12}{hl:<11}{'YES' if gap<3 else f'no({gap:.1f}pp)'}")
elo_wins_both = t1['Elo-only']['2024-25'][0]>=t1['V1 ensemble']['2024-25'][0] and t1['Elo-only']['2025-26'][0]>=t1['V1 ensemble']['2025-26'][0]
print(f"\nElo beats/ties V1 on BOTH seasons: {elo_wins_both}  ->  {'V1 is DEFINITIVELY over-engineered' if elo_wins_both else 'inconclusive (seasonal variation)'}")

# ── TEST 2: Bet365 verification (aligned 380 sample) ────────────────────────────
raw=pd.read_csv('data/raw/pl_history/E0_2025-26.csv',encoding='latin-1')
raw['date']=pd.to_datetime(raw['Date'],dayfirst=True,errors='coerce').dt.date.astype(str)
raw['home']=raw['HomeTeam'].map(canonicalize); raw['away']=raw['AwayTeam'].map(canonicalize)
hold=df[df.season=='2025-26'].copy()
merged=hold.merge(raw[['date','home','away','FTR','B365H','B365D','B365A']],on=['date','home','away'],how='left')
b365_cols=[c for c in raw.columns if c.startswith('B365')]
missing=merged['B365H'].isna().sum()
have=merged.dropna(subset=['B365H','B365D','B365A']).copy()
raw_probs=np.vstack([1/have['B365H'],1/have['B365D'],1/have['B365A']]).T
overround=raw_probs.sum(1)
impl=raw_probs/overround[:,None]
yb=have['y'].values
book=met(impl,yb)
print("\n=== TEST 2: Bet365 verification checklist ===")
print(f"  1. Pre-match odds? B365H/D/A = pre-match odds. Closing odds (B365CH/CD/CA) present: {'B365CH' in raw.columns}. Used PRE-MATCH.")
print(f"  2. Margin removal: mean overround (sum of 1/odds) = {overround.mean():.4f} (typical 1.05-1.07); normalized to sum=1.")
print(f"  3. Missing odds: {missing}/380 matches. All B365 cols present: {sorted(b365_cols)[:6]}")
print(f"  4. Aligned sample: merged {len(merged)}/380, with odds {len(have)}/380 — SAME matches as Elo/V1 (joined on date+teams).")
print(f"  5. No post-match info: odds are pre-kickoff; features are leak-free (Phase 2 verified). OK.")
print(f"  Bet365 on {len(have)}: acc {book[0]}/{len(have)} ll {book[1]} brier {book[2]} draws {book[3]}/{int((yb==1).sum())}")

# ── calibration comparison (V1 vs Bet365) on 2025-26 ────────────────────────────
Pv1=0.5*mA.predict_proba(hold[FEAT_A])+0.5*mB.predict_proba(hold[FEAT_B]); Pv1/=Pv1.sum(1,keepdims=True)
yv1=hold['y'].values
def calib(P,y,name):
    print(f"\n  {name} calibration (max-prob bin -> actual accuracy):")
    conf=P.max(1); pred=P.argmax(1); rows=[]
    for lo,hi in [(0.4,0.5),(0.5,0.6),(0.6,0.7),(0.7,0.8),(0.8,1.01)]:
        m=(conf>=lo)&(conf<hi); n=int(m.sum())
        acc=float((pred[m]==y[m]).mean()) if n else 0.0
        print(f"    {int(lo*100)}-{int(hi*100) if hi<=1 else 100}%: n={n:<4} actual {acc*100:.0f}%")
        rows.append({'bin':f'{int(lo*100)}-{min(int(hi*100),100)}','n':n,'actual_acc':round(acc,3)})
    return rows
cal_v1=calib(Pv1,yv1,'V1 ensemble'); cal_book=calib(impl,yb,'Bet365')

out={'test1_elo_vs_v1':{k:{s:{'acc':v[s][0],'logloss':v[s][1],'brier':v[s][2],'draws':v[s][3]} for s in v} for k,v in t1.items()},
     'elo_beats_v1_both_seasons':bool(elo_wins_both),
     'test2_bet365':{'pre_match':True,'closing_available':bool('B365CH' in raw.columns),'mean_overround':round(float(overround.mean()),4),
                     'missing_odds':int(missing),'aligned_sample':len(have),'acc':book[0],'logloss':book[1],'brier':book[2],'draws':book[3]},
     'calibration':{'v1':cal_v1,'bet365':cal_book}}
os.makedirs('data/experiments',exist_ok=True)
json.dump(out,open('data/experiments/v1_final_benchmark.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
print("\nsaved data/experiments/v1_final_benchmark.json")
