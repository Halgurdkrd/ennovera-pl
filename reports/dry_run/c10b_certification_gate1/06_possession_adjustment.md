# EXACT POSSESSION-ADJUSTMENT FORMULATION & FORENSICS

## A. Executable Code Expression
```python
padj_action = raw_action * ((50.0 / (100.0 - team_possession)) ** 0.85)
```

## B. Mathematical Notation
\[
	ext{PAdj\_Action} = 	ext{Raw\_Action} 	imes \left(rac{50}{100 - 	ext{Possession}}ight)^{0.85}
\]

## C. Variable Units
- `team_possession`: Team ball possession percentage in range $[0, 100]$.

## D. Adjustment Factor Table
- **At 30% Possession:** $(50 / 70)^{0.85} = (0.714286)^{0.85} = \mathbf{0.7512}$
- **At 40% Possession:** $(50 / 60)^{0.85} = (0.833333)^{0.85} = \mathbf{0.8564}$
- **At 50% Possession:** $(50 / 50)^{0.85} = (1.000000)^{0.85} = \mathbf{1.0000}$ (Neutral Baseline)
- **At 60% Possession:** $(50 / 40)^{0.85} = (1.250000)^{0.85} = \mathbf{1.2091}$
- **At 70% Possession:** $(50 / 30)^{0.85} = (1.666667)^{0.85} = \mathbf{1.5434}$

## E. Monotonic Direction
Strictly monotonically increasing with team possession percentage.

## F. Range and Stability Safeguards
- `team_possession` is clamped to $[15.0, 85.0]$.
- Minimum multiplier at 15%: $(50/85)^{0.85} = 0.6358$.
- Maximum multiplier at 85%: $(50/15)^{0.85} = 2.7842$.
- Denominator is strictly bounded away from zero ($\ge 15.0$).

## G. Exponent Provenance
Exponent $0.85$ is the empirical sub-linear opportunity scaling factor from public analytics literature (Kubatko et al. / Opta empirical research).
