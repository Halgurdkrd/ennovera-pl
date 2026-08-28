# ENNOVERA CANONICAL FREEZE POLICY

- **Premier League Official Horizon:**
  - Operational Window: $T-75	ext{ minutes}$ to $T-60	ext{ minutes}$ pre-kickoff.
  - Preferred Target: $T-70	ext{ minutes}$.
  - Hard Invariant: `official_freeze_at <= kickoff_time - 60 minutes`.
  - Exactly one canonical snapshot per fixture (`canonical_evaluation_eligible = True`).
- **FPL Official Horizon:**
  - Operational Window: $T-90	ext{ minutes}$ to $T-30	ext{ minutes}$ pre-deadline.
  - Preferred Target: $T-60	ext{ minutes}$.
  - Exactly one canonical snapshot per gameweek (`canonical_evaluation_eligible = True`).
