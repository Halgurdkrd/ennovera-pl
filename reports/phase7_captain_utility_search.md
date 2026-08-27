# ENNOVERA PHASE 7 — CAPTAIN UTILITY SEARCH

```csv
candidate,dev_gain,val_gain,test_gain,regret,status
CAP-A: Mean only,0.0,0.0,0.0,68.0,Baseline
CAP-B: Mean + P10,4.5,5.0,4.0,62.0,Evaluated
CAP-C: Mean + P15,12.0,13.5,14.0,54.0,Strong
CAP-D: Mean + P10 + P15,14.0,15.0,15.5,51.0,Very Strong
CAP-E: Mean + P15 + P90,17.5,18.0,18.5,48.0,Superior
CAP-F: Mean + P10 + P15 + P90,18.0,18.5,19.0,47.0,Superior
CAP-G: Full Utility + Uncertainty Penalty,21.0,22.5,22.0,46.0,SELECTED WINNER

```

## Selected Formula (Learned on Dev 2022–2024, Validated on Test 2025–26)
U_capt = 0.50 * Norm_Mean + 0.30 * P15 + 0.20 * Norm_P90 - 0.15 * P(0_mins) * UncertaintyPenalty
