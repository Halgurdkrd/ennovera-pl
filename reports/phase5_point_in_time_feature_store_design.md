# ENNOVERA PHASE 5.1 — POINT-IN-TIME FEATURE STORE DESIGN

## Entity Record Schema
- `entity_id` (player or team canonical ID)
- `feature_name` (e.g. `FixtureLoad_7d_Mins`)
- `feature_value` (FLOAT)
- `feature_timestamp` (TIMESTAMPTZ of source match completion)
- `fpl_target_gw` (Target Gameweek)
