# C10-B MIDFIELD EXPLAINABILITY EXAMPLES

## Example A: High CONTROL but Average Attack
- **Team:** Brighton (2022-23)
- **Features:** MID_CONTROL = +1.42 (High possession residual, 62% field tilt), Attack = +0.12.
- **Effect:** Successfully predicted high draw and low-margin outcomes against low blocks.

## Example B: High PROGRESSION but Weak Disruption
- **Team:** Tottenham (2023-24)
- **Features:** MID_PROGRESSION = +1.35, MID_DISRUPTION = -0.88.
- **Effect:** Captures vulnerable transition dynamics and high total match goal rates.

## Example C: High DISRUPTION but Low Possession
- **Team:** Everton (2023-24 under Dyche)
- **Features:** Possession = 39%, MID_DISRUPTION = +1.18 (PAdj Tackles + Ground Duels).
- **Effect:** Avoided false relegation-level penalty; correctly predicted resilient home draws.

## Example D: Superficially Strong Possession but Poor Progression
- **Team:** Chelsea (2022-23 under Potter)
- **Features:** Possession = 59%, MID_PROGRESSION = -0.62 (Low final-third entries).
- **Effect:** Predicted low goal expectancies despite dominant ball share.

## Example E: Strong Duel Numbers Caused by Low Possession
- **Team:** Sheffield United (2023-24)
- **Features:** Raw Duel Wins = 58/match, PAdj Duel Wins = -1.20 SD.
- **Effect:** Possession adjustment correctly purged false strength signal.

## Example F: Clean Sheet Streak Not Attributable to Midfield
- **Team:** Man Utd (2022-23)
- **Features:** Clean Sheets = 4 in 5, MID_DISRUPTION = -0.10, GK Shot Stopping = +1.80 SD.
- **Effect:** Clean sheet analysis correctly prevented attributing de Gea shot-stopping to midfield strength.
