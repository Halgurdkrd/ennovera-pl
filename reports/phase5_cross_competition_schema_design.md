# ENNOVERA PHASE 5.0 — CANONICAL SCHEMA DESIGN

## Proposed Schema: `player_match_performance`
- `player_canonical_id` (VARCHAR, FK)
- `team_canonical_id` (VARCHAR, FK)
- `opponent_canonical_id` (VARCHAR, FK)
- `competition_id` (ENUM: 'PL', 'UCL', 'UEL', 'UECL', 'FAC', 'EFL')
- `season` (VARCHAR: '2022-23' ... '2025-26')
- `match_date` (DATE)
- `kickoff_timestamp` (TIMESTAMPTZ)
- `was_home` (BOOLEAN)
- `started` (BOOLEAN)
- `minutes` (INTEGER: 0–120)
- `goals`, `assists`, `shots`, `shots_on_target` (INTEGER)
- `xg`, `xa`, `xgi` (FLOAT)
- `key_passes`, `touches_box` (INTEGER)
- `clean_sheet` (BOOLEAN), `goals_conceded` (INTEGER)
- `competition_strength_index` (FLOAT: 0.70–1.40)
- `opponent_elo` (FLOAT: 1200–2100)
