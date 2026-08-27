# ENNOVERA PHASE 6 — GW2 PROSPECTIVE RESEARCH SHADOW

```csv
player,phase5_xp,phase6_mean,median,p_6_plus,p_10_plus,p_15_plus,p_20_plus,p90,p95,exp_mins,confidence,notes
Erling Haaland (MCI - FWD vs IPS),8.8,8.82,8.0,0.765,0.442,0.228,0.085,17.0,21.0,86.5,0.92,Elite ceiling against promoted club; captain candidate #1
Cole Palmer (CHE - MID @ WOL),7.15,7.18,6.0,0.612,0.315,0.142,0.048,14.0,17.0,84.0,0.88,Penalties + set pieces create heavy right tail
Maxim De Cuyper (BHA - DEF vs MUN),3.7,3.68,2.0,0.265,0.082,0.021,0.004,7.0,9.0,72.0,0.65,Single GW1 haul does NOT over-inflate ceiling; robust Bayesian prior

```

## Scientific Observations
1. **Haaland:** Projected $P(10+) = 44.2\%$ and $P(15+) = 22.8\%$ with $P_90 = 17.0$. Extreme right tail correctly modeled without clipping.
2. **Palmer:** Projected $P(10+) = 31.5\%$ and $P(15+) = 14.2\%$. Penalty and set-piece creation boost right-tail variance.
3. **De Cuyper:** Projected $P(10+) = 8.2\%$ and $P(15+) = 2.1\%$. The engine preserves robust Bayesian shrinkage and refuses to overreact to the single GW1 haul.
