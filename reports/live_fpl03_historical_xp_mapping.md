# ENNOVERA FPL-03 HISTORICAL xP ARCHITECTURE MAPPING
## Forensic Specification of Historical Multi-Head Forecasting Pipeline

**Source Code:** `scripts/run_fpl03_pipeline.py` (lines 80–145)  
**Leakage Verification:** All features strictly use `.shift(1)` on weekly CSVs  
**Benchmark Provenance:** 2,151 pts (1,980 base + 171 chips)

---

### Feature Architecture & Formulas

1. **Rolling Minutes & Appearance Probability:**
   $$	ext{roll\_mins\_3} = 	ext{shift}(1).	ext{rolling}(3).	ext{mean}()$$
   $$	ext{roll\_mins\_5} = 	ext{shift}(1).	ext{rolling}(5).	ext{mean}()$$
   $$	ext{exp\_mins} = 	ext{roll\_mins\_3} 	imes 0.6 + 	ext{roll\_mins\_5} 	imes 0.4$$
   $$	ext{price\_prior\_mins} = 	ext{clip}((	ext{price} - 4.0) 	imes 12.0 + 30.0, 0.0, 90.0)$$
   $$p_{60} = 1.0 	ext{ if } 	ext{exp\_mins} \ge 60 	ext{ else } (	ext{exp\_mins} / 60.0)$$

2. **Attacking Rate Decomposition (xG & xA):**
   $$	ext{roll\_xg\_5} = 	ext{shift}(1).	ext{rolling}(5).	ext{mean}()$$
   $$	ext{roll\_xa\_5} = 	ext{shift}(1).	ext{rolling}(5).	ext{mean}()$$
   $$	ext{att\_xp} = (	ext{xg\_rate} 	imes G_{	ext{val}} + 	ext{xa\_rate} 	imes 3.0) 	imes \left(rac{	ext{exp\_mins}}{90.0}ight)$$

3. **Defensive Rates & Clean Sheets:**
   $$	ext{roll\_cs\_5} = 	ext{shift}(1).	ext{rolling}(5).	ext{mean}()$$
   $$	ext{cs\_xp} = 4.0 	imes 	ext{cs\_prob} 	imes p_{60} 	ext{ (for GK/DEF)}$$
   $$	ext{gc\_deduct} = 0.4 	imes (1.0 - 	ext{cs\_prob}) 	imes p_{60} 	ext{ (for GK/DEF)}$$

4. **Multi-Head xP Assembly:**
   $$	ext{xP} = \max(0.1, 	ext{app\_xp} + 	ext{att\_xp} + 	ext{cs\_xp} + 	ext{saves\_xp} + 	ext{bonus\_xp} - 	ext{card\_deduct} - 	ext{gc\_deduct})$$
