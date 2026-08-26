# ENNOVERA — WC2026 Player & Squad Rating Formula Audit

**Audit Scope:** Mathematical Recovery, Functional Code Tracing, and Parameter Provenance Audit of the WC2026 Player Rating Transformation and Squad Aggregation Engine.

---

## 1. The Exact Individual Player Rating Formula

Recovered from [`app/services/scorer_predictor.py`](file:///f:/AI/fifi2026/innovera-wc2026-backend/app/services/scorer_predictor.py#L320-L381):

### A. Position-Specific Anchoring Transformation
$$\operatorname{Anchor}(v, \text{lo}, \text{hi}=99) = \max\left(0.0, \min\left(100.0, \frac{v - \text{lo}}{99 - \text{lo}} \times 100\right)\right)$$

- **For Attackers (`ST, CF, LW, RW, CAM, SS`):**
  $$\text{lo} = 45, \quad \text{Quality} = \operatorname{Anchor}(\text{OVR}, 45), \quad \text{Form} = \begin{cases} \operatorname{Percentile}(xG_{90}) & \text{if } xG_{90} > 0 \\ \operatorname{Anchor}(\text{SHO}, 45) & \text{otherwise} \end{cases}$$
- **For Midfielders (`CM, CDM, LM, RM, DM`):**
  $$\text{lo} = 45, \quad \text{Quality} = \operatorname{Anchor}(\text{OVR}, 45), \quad \text{Form} = \begin{cases} 0.60 \cdot \operatorname{Pct}(xA_{90}) + 0.40 \cdot \operatorname{Anchor}(\text{PAS}, 45) & \text{if } xA \text{ valid} \\ \operatorname{Anchor}(\text{PAS}, 45) & \text{otherwise} \end{cases}$$
- **For Defenders (`CB, LB, RB, LWB, RWB`):**
  $$\text{lo} = 55, \quad \text{Quality} = \operatorname{Anchor}(\text{OVR}, 55), \quad \text{Form} = \operatorname{Anchor}(\text{DEF}, 55)$$
- **For Goalkeepers (`GK`):**
  $$\text{lo} = 57, \quad \text{Quality} = \operatorname{Anchor}(\text{OVR}, 57), \quad \text{Form} = \operatorname{Anchor}(\text{GK\_Reflexes}, 57)$$

### B. Experience & Final Composite Formulation
$$\text{Experience} = \max\left(50.0, \min\left(100.0, \frac{\text{Minutes}}{2700} \times 100\right)\right)$$
$$\text{Final Display Rating} = \operatorname{round}(\max(43.0, \mathbf{0.65} \cdot \text{Quality} + \mathbf{0.25} \cdot \text{Form} + \mathbf{0.10} \cdot \text{Experience}))$$

---

## 2. Squad Potential Rating (SPR) Aggregation Formulas

Recovered from [`scripts/fix_squad_features.py`](file:///f:/AI/fifi2026/innovera-wc2026-backend/scripts/fix_squad_features.py#L380-L435):

1. **Squad Attack Rating (0–10 scale):**  
   $$\text{Attack Rating} = \operatorname{Anchor}_{0\text{--}10}(\text{Mean SHO of Top 3 Forwards})$$
2. **Squad Creativity / Midfield Rating (0–10 scale):**  
   $$\text{Creativity Rating} = \operatorname{Anchor}_{0\text{--}10}(\text{Mean PAS of Top 3 Midfielders})$$
3. **Squad Defensive Rating (0–10 scale):**  
   $$\text{Defense Rating} = 0.70 \cdot \operatorname{Anchor}_{0\text{--}10}(\text{Mean DEF of Top 4 Defenders}) + 0.30 \cdot \operatorname{Anchor}_{0\text{--}10}(\text{GK Reflexes})$$
4. **Squad Depth Score (0–1 scale):**  
   $$\text{Depth Score} = \min\left(1.0, \frac{\sum \mathbb{I}(\text{OVR}_j \ge 75)}{11.0}\right)$$

---

## 3. Parameter Provenance & Constant Classification

| Parameter Name | Value | Provenance Method | Classification | Justification / Finding |
|---|---|---|---|---|
| **Quality Component Weight** | **0.65 (65%)** | Manually chosen for UI card stability | **HEURISTIC** | Hardcoded; unvalidated by regression |
| **Form Component Weight** | **0.25 (25%)** | Manually chosen | **HEURISTIC** | Hardcoded; combines xG or EA stats |
| **Experience Component Weight**| **0.10 (10%)** | Manually chosen | **HEURISTIC** | Hardcoded baseline floor at 50% |
| **Attacker Anchor Floor** | **lo = 45** | Empirical visual scaling | **HEURISTIC** | Shifts OVR 70 $\to$ Rating 50 |
| **Defender Anchor Floor** | **lo = 55** | Empirical visual scaling | **HEURISTIC** | Prevents DEF 90 overshooting to 100 |
| **Goalkeeper Anchor Floor** | **lo = 57** | Empirical visual scaling | **HEURISTIC** | Calibrated to elite GK Reflexes (89) |
| **Squad Defense Outfield/GK Blend**| **70% DEF / 30% GK** | Subjective football domain consensus | **HEURISTIC** | Standard industry proxy for clean sheet shares |
| **Squad Depth OVR Threshold** | **OVR $\ge$ 75** | Calibrated to 26-man tournament squads| **EMPIRICAL** | Reasonable proxy for tournament benches |

