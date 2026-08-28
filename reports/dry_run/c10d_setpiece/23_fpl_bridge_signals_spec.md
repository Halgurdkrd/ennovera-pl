# C10-D FPL SET-PIECE BRIDGE SIGNALS SPECIFICATION

## Purpose
Specification of continuous set-piece matchup signals for future FPL player valuation.

## Future FPL Bridge Mappings:
1. **SP_ATTACK_ENVIRONMENT:**
   - Multiplier on corner-taker and free-kick taker Expected Assists (xA):
     \[
     	ext{Taker\_xA\_adj} = 	ext{Base\_xA} 	imes (1.0 + 0.25 	imes 	ext{SP\_ATTACK\_ENVIRONMENT})
     \]
2. **AERIAL_ATTACK_ENVIRONMENT:**
   - Multiplier on tall centre-backs / target forwards (e.g. Gabriel, Haaland, Tarkowski) set-piece goal threat.
3. **CS_SETPIECE_RISK:**
   - Specific penalty factor on goalkeeper/defender clean sheet probability against elite set-piece delivery teams.

*Status: Specification only. No FPL modification executed in this research sprint.*
