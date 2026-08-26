# ENNOVERA PL — M3-PQ Player Quality Methodology & Mathematical Specification

**Methodology Scope:** Mathematical Formulation, Position Grouping, Expected XI Dynamic Weighting, and Gating Network Design for Player Quality Modeling.

---

## 1. Positional Attribute Grouping

Rather than collapsing player talent into a single monolithic OVR number, M3-PQ extracts 4 specialized attribute vectors from point-in-time EA FC databases:

1. **Attacking Quality ($\text{Attr}_{\text{att}}$):**  
   $$\text{Attr}_{\text{att}} = 0.60 \cdot \text{SHO} + 0.25 \cdot \text{Finishing} + 0.15 \cdot \text{Positioning}$$
2. **Creative / Playmaking Quality ($\text{Attr}_{\text{cre}}$):**  
   $$\text{Attr}_{\text{cre}} = 0.60 \cdot \text{PAS} + 0.25 \cdot \text{Vision} + 0.15 \cdot \text{Short Passing}$$
3. **Defensive Quality ($\text{Attr}_{\text{def}}$):**  
   $$\text{Attr}_{\text{def}} = 0.60 \cdot \text{DEF} + 0.25 \cdot \text{Defensive Awareness} + 0.15 \cdot \text{Interceptions}$$
4. **Goalkeeper Shot-Stopping Quality ($\text{Attr}_{\text{gk}}$):**  
   $$\text{Attr}_{\text{gk}} = 0.50 \cdot \text{GK Reflexes} + 0.30 \cdot \text{GK Positioning} + 0.20 \cdot \text{GK Diving}$$

---

## 2. Dynamic Expected XI Aggregation

For every match fixture $t$, team $i$'s starting XI player quality is computed by weighting individual attributes by starting probability and expected minutes:

$$\text{PQ\_XI}_{i, \text{dim}} = \sum_{j \in \text{Roster}_i} P(\text{start}_{j, t}) \cdot \left(\frac{\text{ExpectedMinutes}_{j, t}}{90}\right) \cdot \text{Attr}_{j, \text{dim}}$$

- **Normalization:** Evaluated across the 11 starting positions ($990\text{ total outfield minutes}$), ensuring squad depth does not artificially inflate starting XI quality.
- **Pre-Match Differentials:**  
  $$\Delta \text{PQ}_{\text{dim}} = \text{PQ\_XI}_{\text{home}, \text{dim}} - \text{PQ\_XI}_{\text{away}, \text{dim}}$$

---

## 3. Adaptive Gating Network (Candidate PQ7)

$$\mathbf{P}_{\text{PQ7}} = (1 - g_t) \cdot \mathbf{P}_{\text{M1-D}} + g_t \cdot \mathbf{P}_{\text{PQ4}}$$

Where the gating parameter $g_t \in [0.05, 0.45]$ dynamically modulates reliance on EA FC player attributes based on squad state:

$$g_t = \sigma(1.20 \cdot \mathbb{I}(\text{Promoted}) + 0.80 \cdot (1 - \text{Continuity}) + 0.60 \cdot \text{Uncertainty} - 0.90)$$

- **Stable Clubs:** $g_t \approx 0.05\text{--}0.10$ (Retains 90–95% F2/M1-D statistical history).
- **Rebuilt / Promoted Clubs:** $g_t \approx 0.35\text{--}0.45$ (Transfers up to 45% weight to verified EA FC scouting attributes).

