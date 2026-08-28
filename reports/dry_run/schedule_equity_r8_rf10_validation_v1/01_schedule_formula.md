# SCHEDULE-EQUITY FORMULA IMPLEMENTATION

## Implementation Analysis:
- In Ennovera's core simulation engine (`app/services/season_simulator.py`), remaining schedule difficulty is **not an explicit additive multiplier**.
- The simulator receives the list of 370 remaining fixtures and simulates each match sequentially using the Dixon-Coles bivariate Poisson model parameterized by team ratings ($\mu + 	ext{Venue} + lpha_{	ext{home}} + eta_{	ext{away}}$).
- Therefore, the difficulty of remaining fixtures is **natively and fully encoded** in the remaining fixtures list.
- An aggregate metric $\text{DifficultyRemaining} = \frac{1}{N_{\text{rem}}} \sum (\mu + \beta_{\text{opp}} - \text{Venue})$ is purely **descriptive/diagnostic**.
