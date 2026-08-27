# ENNOVERA PHASE 3.2 — HYBRID MINUTES ARCHITECTURE

## Mathematical Formulation

### 1. Mutually Exclusive Probability States
- $P(60+) = P(\text{start}) \cdot 0.92$
- $P(1\text{--}59) = P(\text{start}) \cdot 0.08 + (1 - P(\text{start})) \cdot P(\text{sub})$
- $P(0) = (1 - P(\text{start})) \cdot (1 - P(\text{sub}))$
- **Constraint:** $P(0) + P(1\text{--}59) + P(60+) = 1.0$ strictly.

### 2. State-Conditional Minute Expectation
$$E[M] = P(\text{start}) \cdot E[M \mid \text{start}] + (1 - P(\text{start})) \cdot P(\text{sub}) \cdot E[M \mid \text{sub}]$$
where $E[M \mid \text{start}] = \text{clip}(0.70 \cdot \text{roll\_starter\_mins} + 0.30 \cdot 82.0, 65.0, 90.0)$ and $E[M \mid \text{sub}] = 20.0$.
