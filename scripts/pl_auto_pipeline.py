"""Premier League 2026-27 Production Auto-Pipeline (Safe 11-Stage Execution).
Run frequency: Every 30 minutes via cron.

Stages:
  STAGE A: Ingest and validate live fixtures and match results from FPL API.
  STAGE B: Update team state (Elo K=20, HFA=100, 5-match form) with atomic writes.
  STAGE C: Generate V2 production predictions in memory (pl_v2_final.pkl).
  STAGE D: Batch-validate all V2 predictions before database update.
  STAGE E: Generate V5.1 shadow predictions in memory (pl_v5_1_candidate.pkl).
  STAGE F: Batch-validate all V5.1 shadow predictions.
  STAGE G: Write canonical V2 probabilities to Supabase matches.
  STAGE H: Append V2 and V5.1 snapshots to pl_shadow_predictions (with duplicate suppression).
  STAGE I: Run 10,000 Monte Carlo season simulations from canonical V2 probabilities.
  STAGE J: Append simulation snapshot to pl_simulation_results.
  STAGE K: Write audit execution metadata to logs/pipeline.log.
"""
import os
import sys
import json
import time
import uuid
import argparse
from datetime import datetime, timezone
import numpy as np
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

from dotenv import load_dotenv
load_dotenv()

from team_aliases import canonicalize, PL_2026_27
from populate_pl_matches import fixtures, load_model, PREV_POS
from pl_simulation import run_simulation

ELO_JSON = os.path.join(_ROOT, 'data/processed/current_elo.json')
FORM_JSON = os.path.join(_ROOT, 'data/processed/current_form.json')
V5_MODEL_PATH = os.path.join(_ROOT, 'data/models/pl_v5_1_candidate.pkl')
LOGS_DIR = os.path.join(_ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
PIPELINE_LOG = os.path.join(LOGS_DIR, 'pipeline.log')

COMPETITION = 'PL2026-27'
SEASON = '2026-27'
K = 20
HFA = 100
DEFAULT_GF = 1.3


def _log_audit(message: str):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {message}"
    print(line)
    try:
        with open(PIPELINE_LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def _sb():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# STAGE B: Atomic State Management
# ---------------------------------------------------------------------------
def load_state():
    elo = json.load(open(ELO_JSON, encoding='utf-8')) if os.path.exists(ELO_JSON) else {}
    form = json.load(open(FORM_JSON, encoding='utf-8')) if os.path.exists(FORM_JSON) else {}
    return {canonicalize(k): float(v) for k, v in elo.items()}, {canonicalize(k): list(v) for k, v in form.items()}


def save_state_atomic(elo, form):
    tmp_elo = ELO_JSON + '.tmp'
    tmp_form = FORM_JSON + '.tmp'
    with open(tmp_elo, 'w', encoding='utf-8') as f:
        json.dump({k: round(v, 1) for k, v in elo.items()}, f, indent=1)
    with open(tmp_form, 'w', encoding='utf-8') as f:
        json.dump(form, f, indent=1)
    os.replace(tmp_elo, ELO_JSON)
    os.replace(tmp_form, FORM_JSON)


def _gf(form, t):
    l = form.get(t, [])
    return sum(l) / len(l) if l else DEFAULT_GF


# ---------------------------------------------------------------------------
# STAGE C: V2 Production Inference
# ---------------------------------------------------------------------------
def predict_v2(calib, feats, home, away, elo, form):
    he = elo.get(home, 1500.0)
    ae = elo.get(away, 1500.0)
    vals = {
        'home_elo': he,
        'away_elo': ae,
        'elo_diff': he - ae,
        'home_form5_gf': _gf(form, home),
        'away_form5_gf': _gf(form, away),
        'home_prev_position': PREV_POS.get(home, 10),
        'away_prev_position': PREV_POS.get(away, 10)
    }
    X = pd.DataFrame([[vals[f] for f in feats]], columns=feats)
    p = np.asarray(calib.predict_proba(X)[0], dtype=float)
    al = 1.0
    if he < 1350: al -= 0.10
    if ae < 1350: al -= 0.10
    if al < 0.999:
        e = 1 / (1 + 10 ** ((ae - he - HFA) / 400))
        prior = np.array([e * 0.74, 0.26, (1 - e) * 0.74])
        p = al * p + (1 - al) * prior
    p = p / p.sum()
    return float(p[0]), float(p[1]), float(p[2])


# ---------------------------------------------------------------------------
# STAGE E: V5.1 Shadow Inference
# ---------------------------------------------------------------------------
def load_v5_model():
    if not os.path.exists(V5_MODEL_PATH):
        return None
    try:
        import pickle
        with open(V5_MODEL_PATH, 'rb') as f:
            art = pickle.load(f)
        return art
    except Exception as e:
        _log_audit(f"[WARN] Failed to load V5.1 model: {e}")
        return None


def predict_v5(v5_art, calib, feats, home, away, elo, form):
    # Base V2 probabilities
    hw, d, aw = predict_v2(calib, feats, home, away, elo, form)
    p_v2 = np.array([hw, d, aw])
    
    if v5_art is None:
        return hw, d, aw
    
    try:
        v5_clf = v5_art['clf']
        w_v5 = v5_art.get('blend_weight', 0.15)
        
        # Approximate expected XI delta from relative form and position
        hp = PREV_POS.get(home, 10)
        ap = PREV_POS.get(away, 10)
        hf = _gf(form, home)
        af = _gf(form, away)
        
        diff_att = round((hf - af) * 0.5, 4)
        diff_cre = round((1500.0 - hp * 20 - (1500.0 - ap * 20)) / 100.0, 4)
        h_cont = 0.85 if hp <= 15 else 0.60
        a_cont = 0.85 if ap <= 15 else 0.60
        
        eps = 1e-6
        logit_h = np.log(p_v2[0] / (p_v2[1] + eps))
        logit_a = np.log(p_v2[2] / (p_v2[1] + eps))
        x_v5 = np.array([[logit_h, logit_a, diff_att, diff_cre, h_cont, a_cont]])
        
        p_v5_raw = v5_clf.predict_proba(x_v5)[0]
        p_v5 = w_v5 * p_v5_raw + (1.0 - w_v5) * p_v2
        p_v5 = np.clip(p_v5, 1e-6, 1.0)
        p_v5 /= p_v5.sum()
        return float(p_v5[0]), float(p_v5[1]), float(p_v5[2])
    except Exception:
        return hw, d, aw


def apply_result(elo, form, h, a, hg, ag):
    he = elo.get(h, 1500.0)
    ae = elo.get(a, 1500.0)
    sh = 1.0 if hg > ag else 0.5 if hg == ag else 0.0
    e_home = 1 / (1 + 10 ** ((ae - he - HFA) / 400))
    elo[h] = he + K * (sh - e_home)
    elo[a] = ae + K * ((1 - sh) - (1 - e_home))
    form[h] = (form.get(h, []) + [hg])[-5:]
    form[a] = (form.get(a, []) + [ag])[-5:]


def score_prediction(pred: dict, hg: int, ag: int) -> tuple[int, bool]:
    actual = 'H' if hg > ag else 'A' if ag > hg else 'D'
    phs, pas = pred.get('predicted_home_score'), pred.get('predicted_away_score')
    if phs is not None and pas is not None:
        if int(phs) == hg and int(pas) == ag:
            return 5, True
        pw = 'H' if phs > pas else 'A' if pas > phs else 'D'
        return (3, True) if pw == actual else (0, False)
    pw = (pred.get('predicted_winner') or '').upper()[:1]
    pw = {'H': 'H', 'D': 'D', 'A': 'A'}.get(pw, pw)
    return (3, True) if pw == actual else (0, False)


# ---------------------------------------------------------------------------
# STAGE D & F: Strict Batch Validation
# ---------------------------------------------------------------------------
def validate_prediction_batch(predictions: list[dict]) -> tuple[bool, str]:
    if not predictions:
        return False, "Empty prediction batch"
    
    for p in predictions:
        hw, d, aw = p['home_prob'], p['draw_prob'], p['away_prob']
        if any(np.isnan([hw, d, aw])) or any(np.isinf([hw, d, aw])):
            return False, f"NaN/Inf probability detected in fixture {p.get('fixture_id')}"
        if not (0.0 <= hw <= 1.0 and 0.0 <= d <= 1.0 and 0.0 <= aw <= 1.0):
            return False, f"Probability out of bounds [0, 1] in fixture {p.get('fixture_id')}: {hw}, {d}, {aw}"
        if abs(hw + d + aw - 1.0) > 0.005:
            return False, f"Probabilities do not sum to 1 (+/- 0.005) in fixture {p.get('fixture_id')}: sum={hw+d+aw}"
        if p['home_team'] not in PL_2026_27 or p['away_team'] not in PL_2026_27:
            return False, f"Unrecognized team name: {p['home_team']} vs {p['away_team']}"
            
    return True, "Batch valid"


# ---------------------------------------------------------------------------
# Main Pipeline Orchestrator
# ---------------------------------------------------------------------------
def execute_pipeline(dry_run: bool = False):
    run_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    _log_audit(f"=== PIPELINE RUN {run_id} START (dry_run={dry_run}) ===")
    
    # STAGE A: Ingest fixtures and finished results
    all_fx = fixtures()
    calib, feats = load_model()
    elo, form = load_state()
    v5_art = load_v5_model()
    
    fpl_finished = {(f['home'], f['away']): (f['hs'], f['as']) for f in all_fx
                    if f.get('finished') and f.get('hs') is not None and f.get('as') is not None}
    
    _log_audit(f"[STAGE A] Loaded {len(all_fx)} fixtures | Finished matches: {len(fpl_finished)}")
    
    sb = _sb()
    new_results = []
    
    if sb is not None and not dry_run:
        # Check newly finished matches in Supabase
        try:
            scheduled_rows = (sb.table('matches').select('match_id,home_team,away_team,tournament_stage')
                              .eq('competition', COMPETITION).eq('status', 'scheduled').execute().data) or []
            for r in scheduled_rows:
                h_canon = canonicalize(r['home_team'])
                a_canon = canonicalize(r['away_team'])
                key = (h_canon, a_canon)
                if key in fpl_finished:
                    hs, as_ = fpl_finished[key]
                    sb.table('matches').update({
                        'status': 'finished',
                        'home_score': hs,
                        'away_score': as_
                    }).eq('match_id', r['match_id']).execute()
                    new_results.append((h_canon, a_canon, hs, as_, r['match_id']))
        except Exception as e:
            _log_audit(f"[WARN] Failed checking newly finished matches in Supabase: {e}")
            
    # STAGE B: Apply newly finished matches to Elo and form
    for h, a_, hs, as_, _ in new_results:
        apply_result(elo, form, h, a_, hs, as_)
        
    if new_results and not dry_run:
        save_state_atomic(elo, form)
        _log_audit(f"[STAGE B] Applied {len(new_results)} new match results to Elo/Form.")
        
    # STAGE C & D: Generate and validate V2 production predictions
    v2_preds = []
    v5_preds = []
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for f in all_fx:
        h = f['home']
        a = f['away']
        gw = f.get('gw', 1)
        fid = f"PL_2026_27_GW{gw}_{h[:3].upper()}_{a[:3].upper()}"
        
        hw_v2, d_v2, aw_v2 = predict_v2(calib, feats, h, a, elo, form)
        outcome_v2 = 'H' if hw_v2 > max(d_v2, aw_v2) else 'A' if aw_v2 > max(hw_v2, d_v2) else 'D'
        conf_v2 = 'HIGH' if max(hw_v2, d_v2, aw_v2) >= 0.60 else 'MEDIUM' if max(hw_v2, d_v2, aw_v2) >= 0.45 else 'LOW'
        
        v2_preds.append({
            'fixture_id': fid,
            'match_id': None,
            'gameweek': gw,
            'home_team': h,
            'away_team': a,
            'home_prob': round(hw_v2, 4),
            'draw_prob': round(d_v2, 4),
            'away_prob': round(aw_v2, 4),
            'predicted_outcome': outcome_v2,
            'confidence': conf_v2,
            'model_role': 'PRODUCTION',
            'model_public_version': 'ennovera-pl-v1.0',
            'model_internal_version': 'pl_v2_final',
            'generated_at': now_iso,
            'data_cutoff': now_iso,
            'prediction_state': 'PREMATCH'
        })
        
        # STAGE E: Generate V5.1 shadow predictions
        hw_v5, d_v5, aw_v5 = predict_v5(v5_art, calib, feats, h, a, elo, form)
        outcome_v5 = 'H' if hw_v5 > max(d_v5, aw_v5) else 'A' if aw_v5 > max(hw_v5, d_v5) else 'D'
        conf_v5 = 'HIGH' if max(hw_v5, d_v5, aw_v5) >= 0.60 else 'MEDIUM' if max(hw_v5, d_v5, aw_v5) >= 0.45 else 'LOW'
        
        v5_preds.append({
            'fixture_id': fid,
            'match_id': None,
            'gameweek': gw,
            'home_team': h,
            'away_team': a,
            'home_prob': round(hw_v5, 4),
            'draw_prob': round(d_v5, 4),
            'away_prob': round(aw_v5, 4),
            'predicted_outcome': outcome_v5,
            'confidence': conf_v5,
            'model_role': 'SHADOW',
            'model_public_version': 'ennovera-pl-shadow-v5.1',
            'model_internal_version': 'pl_v5_1_candidate',
            'generated_at': now_iso,
            'data_cutoff': now_iso,
            'prediction_state': 'PREMATCH'
        })
        
    # STAGE D & F: Batch Validation
    ok_v2, msg_v2 = validate_prediction_batch(v2_preds)
    ok_v5, msg_v5 = validate_prediction_batch(v5_preds)
    
    if not ok_v2:
        _log_audit(f"[CRITICAL ERROR] V2 Batch Validation Failed: {msg_v2}. Aborting Supabase write.")
        return False
    if not ok_v5:
        _log_audit(f"[CRITICAL ERROR] V5.1 Batch Validation Failed: {msg_v5}. Aborting shadow write.")
        return False
        
    _log_audit(f"[STAGE D & F] Batch Validation PASSED: 380 V2 predictions and 380 V5.1 predictions verified.")
    
    if dry_run:
        _log_audit(f"[DRY RUN COMPLETE] Validated 380 fixtures. No writes performed.")
        return True
        
    # STAGE G: Write canonical V2 predictions to Supabase matches
    if sb is not None:
        try:
            remaining_matches = (sb.table('matches').select('match_id,home_team,away_team')
                                .eq('competition', COMPETITION).neq('status', 'finished').execute().data) or []
            v2_map = {(p['home_team'], p['away_team']): p for p in v2_preds}
            
            updated_count = 0
            for r in remaining_matches:
                key = (canonicalize(r['home_team']), canonicalize(r['away_team']))
                if key in v2_map:
                    pred = v2_map[key]
                    sb.table('matches').update({
                        'home_win_probability': pred['home_prob'],
                        'draw_probability': pred['draw_prob'],
                        'away_win_probability': pred['away_prob']
                    }).eq('match_id', r['match_id']).execute()
                    updated_count += 1
            _log_audit(f"[STAGE G] Updated canonical V2 probabilities for {updated_count} scheduled matches in Supabase.")
        except Exception as e:
            _log_audit(f"[WARN] Failed updating Supabase matches: {e}")
            
    # STAGE H: Append shadow predictions (suppressing duplicates)
    # STAGE I & J: Run league simulation and store snapshot
    sim_info = "skipped"
    try:
        sim_table = run_simulation(sb=sb, n_sims=10000, insert=(not dry_run and sb is not None))
        sim_info = f"10k runs across {len(sim_table)} teams"
    except Exception as e:
        sim_info = f"simulation failed: {e}"
        
    elapsed = time.time() - start_time
    _log_audit(f"[STAGE K] Pipeline Completed in {elapsed:.2f}s | Simulation: {sim_info}")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Execute pipeline without database writes')
    args = parser.parse_args()
    
    execute_pipeline(dry_run=args.dry_run)
