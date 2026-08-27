# ENNOVERA PHASE 3.1 — CANONICAL EVALUATION PROTOCOL

## Universal Protocol Rules
1. **Primary Population:** ALL ELIGIBLE PLAYERS in pre-deadline rosters across 2022-23 to 2025-26 ($N = 111,231$ rows). Zero-minute players are strictly included.
2. **Secondary Diagnostic Populations:** Actual Appearers ($>0\text{m}$), Actual Starters ($\ge 60\text{m}$), Non-Starters ($<60\text{m}$), Rotation-Risk, and Positional Splits.
3. **Target Variable:** Actual official FPL matchweek minutes played ($0$ to $90+$).
4. **Strict Temporal Integrity:** All rolling minutes, start rates, and prices strictly lagged with `.shift(1)`.
