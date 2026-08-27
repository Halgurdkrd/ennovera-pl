# ENNOVERA LIVE xP CURRENT ARCHITECTURE
## Forensic Review of Live Ingestion Layer

**Source Code:** `app/services/fpl_ingestor.py` (lines 135–150)  

---

### Formula Specification

$$	ext{base\_pts} = (	ext{form} 	imes 0.70) + \left(rac{	ext{total\_points}}{38} 	imes 0.30ight)$$
$$	ext{exp\_pts} = 	ext{base\_pts} 	imes \left(rac{	ext{exp\_mins}}{90.0}ight)$$

### Weaknesses Identified
1. **Zero Sample-Size Awareness:** When $N=1$ (at GW2), `form` equals the single GW1 score.
2. **Missing Component Decomposition:** Does not distinguish between attacking xG/xA vs defensive CS probability.
3. **Extreme Momentum Dominance:** Gives 70% weight to a single match sample.
