# ENNOVERA PHASE 1 — CAPTAIN & CHIP LOGIC AUDIT

### 1. Captain Selection Utility Function
$$U_i = \text{xP}_i + 3.0 \cdot P(\text{Haul}_i) - 0.20 \cdot \max(0, 6.0 - \text{Price}_i)$$
- Validated: Balances mean expected points with ceiling explosive potential and high-price penalty resistance.

### 2. Triple Captain Disjunctive Bug Fixed
- **Old Buggy Condition:** `if captain["expected_points"] >= 9.5 or captain.get("haul_prob", 0) >= 0.50:`
- **Phase 1 Corrected Condition:** `if captain["expected_points"] >= 9.5 and captain.get("haul_prob", 0) >= 0.50:`
- **Impact:** Prevents mid-tier xP (8.4) with high linear haul prob from firing Triple Captain inappropriately in non-double gameweeks.
