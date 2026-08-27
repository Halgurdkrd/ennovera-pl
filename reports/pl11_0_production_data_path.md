# ENNOVERA PL PHASE 11.0 — PRODUCTION DATA PATH & ENDPOINTS

```
Opta / Understat Raw Events
  -> Pre-Match Feature Extraction (xG, xGA, Elo, Expected XI)
  -> PLPredictorV5_1 (Poisson-Elo Match Inference)
  -> MatchSimulator (Scoreline Probability Matrix)
  -> TableSimulator (10,000 Monte Carlo Season Simulations)
  -> FastAPI Endpoint: `/api/v1/premier-league/matches/{fixture_id}/predict`
  -> FastAPI Endpoint: `/api/v1/premier-league/table/simulate`
  -> Frontend Dashboard & League Widget
```
