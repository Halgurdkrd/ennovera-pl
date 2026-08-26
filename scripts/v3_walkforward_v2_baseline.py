"""Step 1: Walk-Forward V2 Baselines (M7 + Platt).
Generates strictly out-of-sample V2 baseline predictions for all 1,520 matches
across 2022-23, 2023-24, 2024-25, and 2025-26.

Run from ennovera-pl/ directory.
"""
import os
import sys
import json
import pickle
from collections import defaultdict
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)
from team_aliases import canonicalize

OUT_DIR = os.path.join(_ROOT, "data/v3_walkforward")
os.makedirs(OUT_DIR, exist_ok=True)
np.random.seed(13)

# Load features
feat_path = os.path.join(_ROOT, "data/processed/pl_features.csv")
df = pd.read_csv(feat_path)
df["y"] = df["ftr"].map({"H": 0, "D": 1, "A": 2})
df["dt"] = pd.to_datetime(df["date"])

# Compute prev-season final position strictly by prior season
seasons = sorted(df["season"].unique())
finalpos = {}
for s in seasons:
    d = df[df.season == s]
    pts = defaultdict(float)
    gd = defaultdict(float)
    for r in d.itertuples():
        if r.fthg > r.ftag:
            pts[r.home] += 3
        elif r.ftag > r.fthg:
            pts[r.away] += 3
        else:
            pts[r.home] += 1
            pts[r.away] += 1
        gd[r.home] += r.fthg - r.ftag
        gd[r.away] += r.ftag - r.fthg
    for i, t in enumerate(sorted(pts, key=lambda t: (-pts[t], -gd[t])), 1):
        finalpos[(s, t)] = i

def prev_pos(s, t):
    i = seasons.index(s)
    return 18 if i == 0 else finalpos.get((seasons[i - 1], t), 18)

df["home_prev_position"] = [prev_pos(s, t) for s, t in zip(df["season"], df["home"])]
df["away_prev_position"] = [prev_pos(s, t) for s, t in zip(df["season"], df["away"])]

FEAT = [
    "home_elo",
    "away_elo",
    "elo_diff",
    "home_form5_gf",
    "away_form5_gf",
    "home_prev_position",
    "away_prev_position",
]

HP = dict(
    objective="multi:softprob",
    num_class=3,
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    eval_metric="mlogloss",
    random_state=13,
    verbosity=0,
)

def metrics(P, y):
    yv = y.values
    P = np.clip(P, 1e-9, 1)
    P = P / P.sum(axis=1, keepdims=True)
    pred = P.argmax(axis=1)
    acc = int((pred == yv).sum())
    ll = float(-np.mean([np.log(P[i, yv[i]]) for i in range(len(yv))]))
    oh = np.eye(3)[yv]
    brier = float(np.mean(np.sum((P - oh) ** 2, axis=1)))
    draws_called = int((pred == 1).sum())
    draws_correct = int(((pred == 1) & (yv == 1)).sum())
    total_draws = int((yv == 1).sum())
    return {
        "acc": acc,
        "acc_pct": round(acc / len(yv) * 100, 2),
        "log_loss": round(ll, 4),
        "brier": round(brier, 4),
        "draw_called": draws_called,
        "draw_correct": draws_correct,
        "draw_total": total_draws,
    }

TARGET_SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
results = {}
all_preds = []

print("=" * 70)
print("WALK-FORWARD V2 BASELINE (M7 + PLATT) — STRICT OUT-OF-SAMPLE")
print("=" * 70)

for s in TARGET_SEASONS:
    s_idx = seasons.index(s)
    cal_season = seasons[s_idx - 1]
    train_seasons = seasons[: s_idx - 1]
    
    tr = df[df.season.isin(train_seasons)]
    cal = df[df.season == cal_season]
    test = df[df.season == s].copy()
    
    print(f"\nTarget Season: {s} (380 matches)")
    print(f"  Train: {train_seasons[0]}..{train_seasons[-1]} ({len(tr)} matches)")
    print(f"  Calib: {cal_season} ({len(cal)} matches)")
    
    m = xgb.XGBClassifier(**HP)
    m.fit(tr[FEAT], tr["y"])
    
    calib = CalibratedClassifierCV(m, method="sigmoid", cv="prefit")
    calib.fit(cal[FEAT], cal["y"])
    
    probs = calib.predict_proba(test[FEAT])
    probs = np.clip(probs, 1e-9, 1)
    probs = probs / probs.sum(axis=1, keepdims=True)
    
    m_dict = metrics(probs, test["y"])
    results[s] = m_dict
    print(f"  Result: Acc {m_dict['acc']}/380 ({m_dict['acc_pct']}%), Log-Loss {m_dict['log_loss']}, Brier {m_dict['brier']}, Draws {m_dict['draw_correct']}/{m_dict['draw_total']}")
    
    test["v2_prob_home"] = probs[:, 0]
    test["v2_prob_draw"] = probs[:, 1]
    test["v2_prob_away"] = probs[:, 2]
    test["v2_pred"] = probs.argmax(axis=1)
    all_preds.append(test)

wf_df = pd.concat(all_preds, ignore_index=True)
out_csv = os.path.join(OUT_DIR, "v2_walkforward_predictions.csv")
wf_df.to_csv(out_csv, index=False)
print(f"\nSaved walk-forward baseline predictions to {out_csv} ({len(wf_df)} rows)")

summary_path = os.path.join(OUT_DIR, "v2_walkforward_summary.json")
with open(summary_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved summary to {summary_path}")

print("\n" + "=" * 70)
print("SUMMARY ACROSS ALL 4 SEASONS")
print("=" * 70)
print(f"{'Season':<12}{'Acc (N/380)':<16}{'Acc %':<10}{'Log-Loss':<12}{'Brier':<10}{'Draw Recall'}")
for s, r in results.items():
    print(f"{s:<12}{str(r['acc'])+'/380':<16}{str(r['acc_pct'])+'%':<10}{r['log_loss']:<12}{r['brier']:<10}{r['draw_correct']}/{r['draw_total']}")

dev_acc = results["2022-23"]["acc"] + results["2023-24"]["acc"]
dev_ll = (results["2022-23"]["log_loss"] + results["2023-24"]["log_loss"]) / 2
print(f"\nDev Split (2022-24, 760m): Acc {dev_acc}/760 ({dev_acc/7.6:.2f}%), Avg LL {dev_ll:.4f}")
print(f"Val Split (2024-25, 380m): Acc {results['2024-25']['acc']}/380 ({results['2024-25']['acc_pct']}%), LL {results['2024-25']['log_loss']:.4f}")
print(f"Holdout   (2025-26, 380m): Acc {results['2025-26']['acc']}/380 ({results['2025-26']['acc_pct']}%), LL {results['2025-26']['log_loss']:.4f}")

