# ENNOVERA PHASE 6 — DISTRIBUTION ARCHITECTURE DESIGN

## Stochastic Component Architecture ($N = 10,000$ Monte Carlo Draws)
- **Minutes Distribution:** Categorical State $(P_0, P_{1-59}, P_{60+})$ + Beta-distributed conditional playing minutes.
- **Goals Distribution:** Poisson / Negative Binomial intensity $\lambda_{\text{goal}} = \text{xG90} \times \frac{\text{mins}}{90} \times \text{MatchConditioning}$.
- **Assists Distribution:** Poisson intensity $\lambda_{\text{assist}} = \text{xA90} \times \frac{\text{mins}}{90} \times \text{MatchConditioning}$.
- **Clean Sheets & Concession:** $P(\text{CS}_{\text{team}} \mid 60+\text{ mins})$ + Poisson opponent goals $k_{\text{opp}}$.
- **Saves & Bonus:** Poisson save intensity $\lambda_{\text{save}}$ + Match-conditioned relative BPS ordinal regression.
- **Exact FPL Scoring:** Applied to every simulated trial.
