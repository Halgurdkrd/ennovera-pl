import json
import urllib.request
import os

url = "https://fantasy.premierleague.com/api/fixtures/?event=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    fixtures = json.loads(r.read().decode())

teams_map = {
    1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brentford", 5: "Brighton",
    6: "Chelsea", 7: "Coventry City", 8: "Crystal Palace", 9: "Everton", 10: "Fulham",
    11: "Hull City", 12: "Ipswich Town", 13: "Leeds", 14: "Liverpool", 15: "Man City",
    16: "Man Utd", 17: "Newcastle", 18: "Nott'm Forest", 19: "Spurs", 20: "Sunderland"
}

print(f"Total GW1 Fixtures fetched: {len(fixtures)}")
gw1_records = []
for fix in fixtures:
    h = teams_map[fix["team_h"]]
    a = teams_map[fix["team_a"]]
    hs = fix.get("team_h_score")
    as_s = fix.get("team_a_score")
    ftr = "H" if hs > as_s else ("A" if as_s > hs else "D") if hs is not None else None
    print(f"ID {fix['id']}: {fix['kickoff_time']} | {h} {hs} - {as_s} {a} | Result: {ftr} | Finished: {fix.get('finished') or fix.get('finished_provisional')}")
    gw1_records.append({
        "fixture_id": fix["id"],
        "kickoff_time": fix["kickoff_time"],
        "home_team": h,
        "away_team": a,
        "home_score": hs,
        "away_score": as_s,
        "ftr": ftr,
    })

os.makedirs("data/experiments", exist_ok=True)
with open("data/experiments/2026_27_gw1_official_results.json", "w") as f:
    json.dump(gw1_records, f, indent=2)
print("Saved official GW1 results to data/experiments/2026_27_gw1_official_results.json")

