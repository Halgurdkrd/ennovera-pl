# ENNOVERA LIVE VS HISTORICAL FPL-03 ARCHITECTURE MATRIX
## Side-by-Side Component Comparison

| Component | Historical FPL-03 Engine | Current Live Engine | Same? | Impact | Required Port? |
|---|---|---|---|---|---|
| **Minutes Modeling** | Multi-head EWMA (3 & 5 GWs) + Price Prior | Status heuristic (0.95 / 0.85) | NO | High | YES |
| **Attacking Modeling** | Rolling xG & xA with position goal multipliers | Implicit via raw points | NO | High | YES |
| **Defensive Modeling** | Clean sheet probability & goal conceded penalties | Implicit via raw points | NO | High | YES |
| **Early-Season Shrinkage** | Historical prior baseline | None (100% current form) | NO | CRITICAL | YES |
| **Captain Utility** | $U = 	ext{xP} + 3.0 \cdot P(	ext{Haul}) - 	ext{penalty}$ | $U = 	ext{xP} + 3.0 \cdot P(	ext{Haul}) - 	ext{penalty}$ | YES | Clean | Kept Identical |
| **LP Squad Optimizer** | Scipy `linprog` with budget & formation constraints | Scipy `linprog` with budget & formation constraints | YES | Clean | Kept Identical |
| **Chip Decision Logic** | Reservation value tournament rules | Reservation value tournament rules | YES | Clean | Kept Identical |
