# ENNOVERA PHASE 10.5 — MULTI-GW HORIZON & DISCOUNT REVALIDATION

```csv
H,gamma,nested_val_score,transfers_yr,bank_rate,net_transfer_gain,transfer_regret,decision
3,0.9,2168.2,41.2,8.5,+14.2 pts,26.0,REJECT (Myopic)
3,0.95,2168.8,40.5,9.0,+14.8 pts,25.2,REJECT
5,0.875,2170.1,35.8,11.8,+17.8 pts,22.5,ACCEPTABLE
5,0.9,2170.5,35.2,12.0,+18.5 pts,22.0,KEEP_CURRENT (OPTIMAL)
5,0.925,2170.4,34.8,12.2,+18.2 pts,22.1,PLATEAU
8,0.85,2169.1,31.4,14.5,+16.0 pts,24.5,REJECT (Too rigid)
8,0.9,2168.5,30.2,15.0,+15.2 pts,25.8,REJECT (Distant uncertainty overweighted)

```

## Scientific Findings
- $H=5, \gamma=0.90$ remains optimal with lowest transfer regret ($22.0\text{ pts}$) and highest net gain ($+18.5\text{ pts}$).
- **Decision:** **KEEP_CURRENT ($H=5, \gamma=0.90$)**.
