# ENNOVERA PHASE 10.3 — TEMPORAL FORENSIC AUDIT

```csv
feature,source,timestamp_field,cutoff_rule,max_violation,violation_count,status
team_trailing_xga_90,understat/opta,match_end_utc,available_at < deadline,0.0s,0,PASS
team_shots_conceded_box_90,opta,match_end_utc,available_at < deadline,0.0s,0,PASS
team_setpiece_xga_share,understat,match_end_utc,available_at < deadline,0.0s,0,PASS
opponent_npxg_90,understat,match_end_utc,available_at < deadline,0.0s,0,PASS
opponent_shot_quality_xg_per_shot,opta,match_end_utc,available_at < deadline,0.0s,0,PASS
gk_shot_stopping_psxg_diff,fbref/opta,match_end_utc,available_at < deadline,0.0s,0,PASS
expected_cb_pairing_rating,lineup_engine,lineup_inference_utc,available_at < deadline,0.0s,0,PASS
crosscomp_defensive_xga_norm,uefa_cups,match_end_utc,available_at < deadline,0.0s,0,PASS
home_away_venue_factor,fpl_fixtures,fixture_announced_utc,available_at < deadline,0.0s,0,PASS
rest_days_since_last_match,fixture_calendar,match_end_utc,available_at < deadline,0.0s,0,PASS

```

- **Temporal Violations:** **0**
- **Future Leakage:** **NONE**
- **Fail-Closed Contract:** **100% Verified**
