# ENNOVERA PHASE 3.2 — MINUTES SEMANTIC AUDIT

## Mathematical Semantic Breakdown

### 1. Expected Minutes V1
- **Formula:** $E[M]_{\text{V1}} = 0.60 \cdot \text{roll\_mins}_3 + 0.40 \cdot \text{roll\_mins}_5$
- **Semantic Meaning:** Unconditional expected minutes derived from trailing rolling averages.
- **Key Property:** Implicitly discounts non-appearances because 0-minute matches enter the trailing average directly.

### 2. Expected Minutes V2
- **Formula:** $E[M]_{\text{V2}} = P(\text{start}) \cdot 81.0 + (1 - P(\text{start})) \cdot P(\text{sub}) \cdot 20.0$
- **Semantic Meaning:** State-decomposed expectation combining two distinct binary logistic stages: $P(\text{start})$ and $P(\text{sub} \mid \text{bench})$.
- **Key Property:** Explicitly generates probability distributions ($P(\text{start}), P(\text{appearance}), P(60+)$).

### 3. Double-Discounting Hazard
- **Finding:** A naive formulation multiplying $E[M]_{\text{V1}} \times P(\text{appearance})$ would **double-discount** non-availability because V1 already has trailing zeros factored into its rolling expectation.
- **Correct Formulation:** State-conditional expectation where conditional minutes $E[M \mid \text{start}]$ and $E[M \mid \text{sub}]$ are multiplied by their respective mutually exclusive state probabilities.
