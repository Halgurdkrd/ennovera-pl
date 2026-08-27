# ENNOVERA PHASE 9.0 — ARCHITECTURE RECOMMENDATION

## Recommended Primary Module: P9-A (Lineup, Minutes & Press Conference NLP Engine)
- **Scientific Rationale:** Minutes and availability uncertainty account for **38 pts of Prediction Regret** and **18 pts of Selection Regret**. Perfect minutes oracle yields $+12.5\text{ pts/season}$ manager score gain.
- **Components:**
  1. Automated press-conference transcription and status classifier (Probable, Doubtful, Ruled Out).
  2. Training ground photo / squad leak verification layer.
  3. Tactical rotation probability model conditional on European congestion ($<72\text{h}$ rest).

## Recommended Secondary Module: P9-E (Opponent Tactical Matchup Engine)
- **Scientific Rationale:** Generic Elo/xG opponent strength misses spatial and stylistic mismatches (e.g. pace vs high defensive lines, set-piece aerial vulnerability), accounting for **12 pts of Prediction Regret**.
