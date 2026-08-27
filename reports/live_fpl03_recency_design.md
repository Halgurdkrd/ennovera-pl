# ENNOVERA LIVE FPL-03 RECENCY DESIGN
## Bayesian Sample-Size Shrinkage Schedule

### Mathematical Formulation
$$w(n) = rac{n}{n + k}, \quad k = 4.0$$
$$	ext{xP}_{	ext{blended}} = (1 - w(n)) \cdot 	ext{xP}_{	ext{prior}} + w(n) \cdot 	ext{xP}_{	ext{observed}}$$

### Schedule by Gameweek
- **GW1 ($n=0$):** $w(0) = 0.00$ (100% Pre-season Bayesian Prior)
- **GW2 ($n=1$):** $w(1) = 0.20$ (80% Prior, 20% GW1 Evidence)
- **GW3 ($n=2$):** $w(2) = 0.33$ (67% Prior, 33% Recent Evidence)
- **GW4 ($n=3$):** $w(3) = 0.43$ (57% Prior, 43% Recent Evidence)
- **GW5 ($n=4$):** $w(4) = 0.50$ (50% Prior, 50% Recent Evidence)
- **GW6+ ($n \ge 5$):** $w(n) \ge 0.56$ (Transitions to rolling multi-head EWMA)
