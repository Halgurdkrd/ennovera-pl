"""V3 Step 1: fetch all FPL data -> data/v3/*.json. Self-contained."""
import os, sys, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team_aliases import canonicalize
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V3=os.path.join(_ROOT,'data/v3'); os.makedirs(V3,exist_ok=True)
def _get(u):
    r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(r,timeout=30) as x: return json.loads(x.read().decode())
bs=_get('https://fantasy.premierleague.com/api/bootstrap-static/'); fx=_get('https://fantasy.premierleague.com/api/fixtures/')
id2n={t['id']:canonicalize(t['name']) for t in bs['teams']}
# A. team strength
strength={id2n[t['id']]:{k:t.get(k) for k in ['strength_overall_home','strength_overall_away','strength_attack_home','strength_attack_away','strength_defence_home','strength_defence_away']} for t in bs['teams']}
json.dump(strength,open(f'{V3}/fpl_team_strength.json','w'),indent=1)
# B. players
def f(v,d=0.0):
    try: return float(v)
    except: return d
players=[{'web_name':p['web_name'],'team':id2n.get(p['team']),'position':p['element_type'],'now_cost':p['now_cost'],
 'total_points':p['total_points'],'form':f(p.get('form')),'ppg':f(p.get('points_per_game')),'xg':f(p.get('expected_goals')),
 'xa':f(p.get('expected_assists')),'xgi':f(p.get('expected_goal_involvements')),'ict':f(p.get('ict_index')),
 'minutes':p['minutes'],'starts':p.get('starts',0),'clean_sheets':p.get('clean_sheets',0),
 'chance_this':p.get('chance_of_playing_this_round'),'chance_next':p.get('chance_of_playing_next_round'),
 'status':p.get('status'),'tin':p.get('transfers_in_event',0),'tout':p.get('transfers_out_event',0)} for p in bs['elements']]
json.dump(players,open(f'{V3}/fpl_players.json','w'),indent=1)
# C. FDR per team per gameweek
fdr={}
for m in fx:
    gw=m.get('event')
    if gw is None: continue
    fdr.setdefault(str(gw),[]).append({'home':id2n.get(m['team_h']),'away':id2n.get(m['team_a']),
        'home_fdr':m.get('team_h_difficulty'),'away_fdr':m.get('team_a_difficulty')})
json.dump(fdr,open(f'{V3}/fpl_fdr.json','w'),indent=1)
print(f"saved: fpl_team_strength.json ({len(strength)} teams), fpl_players.json ({len(players)}), fpl_fdr.json ({len(fdr)} GWs)")
print("D. per-player historical (vaastav): NOT downloaded — full clone deferred (gitignored, ~500MB). Historical xG unavailable pre-2022-23.")
