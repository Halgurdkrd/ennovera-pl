# ENNOVERA PHASE 2 — FINISHING & ASSIST CONVERSION
## Empirical Bayes Finishing Calibration

Finishing Multiplier = 1.0 + 0.25 * clip((Goals - xG) / (xG + 2.0), -0.5, 0.5)
- Protects against regression to the mean while giving slight predictive credit to elite persistent finishers (e.g. Haaland, Son, Palmer).
