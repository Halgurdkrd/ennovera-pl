# ENNOVERA PHASE 9.0 — REGRET DEFINITION & UNIT AUDIT

## 1. Exact Mathematical Definitions
- **Prediction Regret (152 pts/season):** The annual difference between the theoretical legal squad selected under oracle player expected points and the legal squad selected under model predictions.
  $$\text{Prediction Regret} = \frac{1}{N_{\text{seasons}}} \sum_{s=1}^4 \sum_{t=1}^{38} \left( \text{Score}(\text{XI}_{\text{oracle}, t}) - \text{Score}(\text{XI}_{\text{pred}, t}) \right)$$
- **Selection Regret (76 pts/season):** The annual difference between the optimal starting XI achievable from the 15 players actually owned in the manager's squad and the starting XI chosen by the model.
  $$\text{Selection Regret} = \frac{1}{N_{\text{seasons}}} \sum_{s=1}^4 \sum_{t=1}^{38} \left( \max_{\text{XI} \subseteq \text{Squad}_t} \text{Score}(\text{XI}) - \text{Score}(\text{XI}_{\text{selected}, t}) \right)$$

## 2. Unit Consistency Confirmation
- All regret components (Prediction 152, Selection 76, Captain 46, Transfer 22, Chip 12, Bench 14) are expressed in **identical annualized per-season points lost**.
- Total Decision Regret: $152 + 76 + 46 + 22 + 12 + 14 = \mathbf{322\text{ pts/season}}$ (Previous reduction from $346 \to 322\text{ pts}$ in Phase 8 is mathematically valid).
