# ENNOVERA TRIPLE CAPTAIN THRESHOLD CONSISTENCY AUDIT
## Forensic Root-Cause Analysis of 0% Counterfactual TC Trigger

**Question:** Why did Haaland at 8.4 xP trigger Triple Captain in the 0%-GW1 counterfactual when the primary xP threshold is $\ge 9.5$?

### Root Cause Isolated
In `app/services/fpl_optimizer.py` (lines 222–230):
```python
if "triple_captain_1" in chips_rules and "triple_captain_1" not in chips_used and gameweek <= 19:
    if captain["expected_points"] >= 9.5 or captain.get("haul_prob", 0) >= 0.50:
        return {"action": "USE", "chip_name": "Triple Captain", ...}
```
Notice the compound boolean condition:
$$	ext{captain\_xp} \ge 9.5 \quad \mathbf{OR} \quad P(	ext{Haul}) \ge 0.50$$

In the baseline formula:
$$P(	ext{Haul}) = 	ext{clip}((	ext{xP} - 2.5) 	imes 0.08 + 0.10, 0.01, 0.65)$$
When Haaland had $	ext{xP} = 8.4$:
$$P(	ext{Haul}) = (8.4 - 2.5) 	imes 0.08 + 0.10 = 0.572 \ge 0.50$$
Because the haul probability exceeded 0.50, the second branch evaluated to `True`, triggering Triple Captain despite $	ext{xP} < 9.5$.

### Recommendation
In future chip policy refinements, require compound conjunction:
$$	ext{captain\_xp} \ge 9.5 \quad \mathbf{AND} \quad P(	ext{Haul}) \ge 0.50$$
