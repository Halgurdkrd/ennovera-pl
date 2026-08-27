# ENNOVERA PHASE 5.0 — DATA QUALITY AUDIT

- **Local European/Cup Data Quality:** N/A (Data not yet acquired).
- **Acquisition Quality Target:** Must enforce:
  - 100% valid ISO 8601 timestamps.
  - Minutes bounded strictly within $[0, 120]$.
  - Player-match uniqueness (`player_canonical_id` + `match_id` unique primary key).
  - 0% missing opponent Elo or venue metadata.
