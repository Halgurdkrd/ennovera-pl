# ENNOVERA PHASE 5.15 — SCHEMA VALIDATION REPORT

## Canonical Tables Built in `data/cross_competition/processed/`
1. `matches.parquet`: 16 columns (Match ID, Competition, Season, Kickoff, End Time, Venue, Goals, xG, Source).
2. `player_matches.parquet`: 22 columns (Match ID, Player ID, Team ID, Opponent, Starter, Minutes [0–120], Goals, Assists, xG, xA, Shots, Def, GK).
3. `team_matches.parquet`: 11 columns (Match ID, Team ID, Opponent, Goals For/Against, xG For/Against, Clean Sheet).
4. `fpl_crosscomp_eligibility.parquet`: Point-in-time eligibility index across 152 historical gameweeks.
