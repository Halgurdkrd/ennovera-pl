# ENNOVERA PHASE 1 — FPL-03 ARCHITECTURE RECONSTRUCTION
## Comprehensive Forensic Specification of Historical Multi-Head Forecasting Pipeline

**Source Code:** `scripts/run_fpl03_pipeline.py` (lines 80–165)  
**Leakage Verification:** All features strictly use `.shift(1)` on weekly CSVs  
**Benchmark Provenance:** 2,151 pts (1,980 base + 171 chips across 2025-26)

---

### Multi-Head Component Architecture

1. **Minutes & Appearance Model:**
   - Multi-head EWMA: roll_mins = 0.60 * roll_mins_3 + 0.40 * roll_mins_5
   - Price prior baseline: price_mins = clip((price - 4.0) * 12 + 30, 0, 90)
   - p60 = 1.0 if exp_mins >= 60 else (exp_mins / 60.0)
   - Appearance points: 2.0 * p60

2. **Attacking Rate Model (xG & xA):**
   - Position Goal Values: FWD = 4.0, MID = 5.0, DEF/GK = 6.0
   - Attacking xP: (xG_rate * G_val + xA_rate * 3.0) * (exp_mins / 90.0)

3. **Defensive Rate Model (Clean Sheets):**
   - Clean Sheet Probability CS_prob scaled by FDR and home/away factor
   - Defensive xP: 4.0 * CS_prob * p60 - 0.40 * (1 - CS_prob) * p60 (for GK/DEF)

4. **Bonus & Deductions:**
   - Bonus points: clip((xG * 1.8 + xA * 1.2 + CS * 0.7) * p60, 0, 2.5)
   - Yellow/Red card deduction: -0.15 * p60

5. **Temporal Shift Integrity:**
   - For every player i at Gameweek t, all inputs are computed strictly on matchweeks <= t-1. Current-GW realized points are never accessible.
