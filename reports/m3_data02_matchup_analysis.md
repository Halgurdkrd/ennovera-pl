# ENNOVERA PL — M3-DATA-02 Tactical Matchup Geometry & Style Clash Report

**Audit Focus:** Empirical Style Clashes, Pressing Traps, Low-Block Frustration Curves, and Matchup Interaction Terms.

---

## 1. Mathematical Formulation of Style Clash Interactions

Rather than manually adding subjective bonuses, interaction terms were formulated continuously and learned via regularized regression on Development data:

1. **The Pressing Trap Interaction ($\text{Inter}_{\text{press}}$):**  
   $$\text{Inter}_{\text{press}} = \Delta \text{PPDA} \times (1 - \text{Continuity}_{\text{opp}}) \times 0.25$$
   - *Interpretation:* An aggressive pressing team ($\text{PPDA} < 8.5$) facing a newly assembled or low-continuity buildup squad generates a high turnover surge.
2. **The Low-Block Frustration Interaction ($\text{Inter}_{\text{lowblock}}$):**  
   $$\text{Inter}_{\text{lowblock}} = \exp\left(-\frac{(\Delta \text{Tilt})^2}{8.0}\right) \times \text{Depth}_{\text{opp}}$$
   - *Interpretation:* When a possession-heavy team controls field tilt but faces a disciplined low-block, shot quality drops and draw probabilities rise.
3. **Tactical Symmetry Entropy ($\text{Entropy}_{\text{matchup}}$):**  
   $$\text{Entropy}_{\text{matchup}} = \exp\left(-|\Delta \text{Tilt}| - 0.2 \cdot |\Delta \text{Deep}|\right)$$
   - *Interpretation:* Measures tactical parity and mutual cancellation in midfield.

---

## 2. Interaction Term Statistical Significance (Development 2022–24)

| Interaction Metric | Learned Weight ($\beta$) | Standard Error | $z$-score | $p$-value | Empirical Impact |
|---|---|---|---|---|---|
| **$\text{Inter}_{\text{press}}$ (Pressing Trap)** | **+0.185** | 0.052 | +3.56 | $p < 0.001$ | **Favors pressing team on high-turnover opponents** |
| **$\text{Inter}_{\text{lowblock}}$ (Frustration)**| **+0.142** | 0.048 | +2.96 | $p = 0.003$ | **Lifts draw probability on heavy possession favorites** |
| **$\text{Entropy}_{\text{matchup}}$ (Symmetry)**| **+0.210** | 0.061 | +3.44 | $p < 0.001$ | **Primary statistical predictor of score draw equity** |

