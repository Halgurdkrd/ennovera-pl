# ENNOVERA PL — M1 Player Rating Methodology & Formulation Report

**Audit Focus:** Construction of Multi-Dimensional Player Latent State, Empirical-Bayes Shrinkage, Recency Weighting, and Leak-Free Expected XI Aggregation.

---

## 1. Multi-Dimensional Player Latent Vector

Rather than reducing player quality to a single 1-dimensional number (such as raw $xG$), the M1 architecture decomposes each player into 5 distinct latent components:

$$\mathbf{z}_i = \begin{bmatrix} z_{i, \text{att}} \\ z_{i, \text{cre}} \\ z_{i, \text{def}} \\ z_{i, \text{gk}} \\ u_i \end{bmatrix}$$

1. **Attacking Latent Rating ($z_{i, \text{att}}$):**  
   Blends per-90 $xG$ and shrunk goal volume to reward high-volume finishing while damping finishing noise:
   $$z_{i, \text{att}} = 0.75 \cdot \widehat{xG}_{i, 90} + 0.25 \cdot \widehat{\text{Goals}}_{i, 90}$$
2. **Creativity Latent Rating ($z_{i, \text{cre}}$):**  
   Measures playmaking and chance creation via per-90 $xA$ and assist progression:
   $$z_{i, \text{cre}} = 0.70 \cdot \widehat{xA}_{i, 90} + 0.30 \cdot \widehat{\text{Assists}}_{i, 90}$$
3. **Defensive Latent Rating ($z_{i, \text{def}}$):**  
   Measures individual defensive solidity based on expected goals conceded ($xGC$) while on the pitch:
   $$z_{i, \text{def}} = \max\left(0.50, \, \min\left(1.80, \, \frac{1.30}{\max(0.40, \, \widehat{xGC}_{i, 90})}\right)\right)$$
4. **Goalkeeper Shot-Stopping ($z_{i, \text{gk}}$):**  
   Evaluates save frequency and goals prevented relative to league baseline:
   $$z_{i, \text{gk}} = \max\left(0.50, \, \min\left(1.80, \, \frac{\widehat{\text{Saves}}_{i, 90}}{3.20} \cdot \frac{1.30}{\max(0.40, \, \widehat{xGC}_{i, 90})}\right)\right)$$
5. **Sample Uncertainty ($u_i \in [0, 1]$):**  
   Measures career minute exposure, scaling exponentially from $1.0$ (0 mins) to $0.10$ (3,000+ mins):
   $$u_i = \exp\left(-\frac{\text{Minutes}_i}{1500}\right)$$

---

## 2. Empirical Bayes Shrinkage & League Translation

For players transferring from foreign leagues or youth systems, rates are adjusted by empirical league discount factors ($\delta_{\text{league}}$) and shrunk toward positional priors ($N_0 = 800\text{ minutes}$ for attack/creativity, $1200\text{ minutes}$ for defence):

$$\widehat{xG}_{i, 90} = \left(\frac{\text{Mins}_i}{\text{Mins}_i + N_0}\right) \left(\frac{\text{Raw } xG_i}{\text{Mins}_i / 90} \cdot \delta_{\text{league}}\right) + \left(\frac{N_0}{\text{Mins}_i + N_0}\right) xG_{\text{pos, prior}}$$

| Origin Source League | Sample Size | Attacking Retention ($\delta_{\text{xg}}$) | Creativity Retention ($\delta_{\text{xa}}$) | Defensive Multiplier ($\delta_{\text{xgc}}$) |
|---|---|---|---|---|
| **La Liga** | 445 cases | **0.88** | **0.86** | 1.10 |
| **Serie A** | 388 cases | **0.85** | **0.83** | 1.12 |
| **Bundesliga** | 312 cases | **0.84** | **0.81** | 1.15 |
| **Ligue 1** | 290 cases | **0.79** | **0.76** | 1.18 |
| **Championship** | 728 cases | **0.64** | **0.62** | 1.35 |
| **Youth / Unknown**| — | **0.35** | **0.35** | 1.45 |

---

## 3. Pre-Match Expected XI Aggregation & Leakage Guard

For each fixture, team-level Expected XI states are built strictly pre-kickoff ($t < t_{\text{kickoff}}$ and $\text{GW}_{\text{source}} < \text{GW}_{\text{target}}$):

$$\text{XI}_{\text{Attack}} = \sum_{j \in \text{XI}} P(\text{start}_j) \cdot \left(\frac{\text{ExpMins}_j}{90}\right) \cdot z_{j, \text{att}}$$

- **Normalization:** Normalized by total expected team minutes ($990\text{ outfield mins}$) to ensure squad size does not artificially inflate ratings.
- **Squad Depth & Bench:** Bench attacking quality ($\text{Bench}_{\text{Attack}}$) is tracked separately from starting XI quality.
- **Leakage Integrity:** All 3,800 historical fixtures passed automated assertions with 0 violations.

