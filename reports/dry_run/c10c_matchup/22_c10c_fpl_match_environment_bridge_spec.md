# C10-C FPL MATCH ENVIRONMENT BRIDGE SPECIFICATION

## Purpose
Translate continuous match environment latent states into tactical multipliers for FPL player expected points (xP).

## Latent Bridge Mappings:
1. **ATTACK_ENVIRONMENT:**
   - Multiplier on Attacker expected goal involvement (xGI) and bonus point expectation:
     \[
     	ext{Attacker\_Multiplier} = 1.0 + 0.15 	imes 	ext{ATTACK\_ENVIRONMENT}
     \]
   - Enables picking explosive attackers in high-tempo mid-table clashes even if teams are not globally elite.

2. **DEFENCE_ENVIRONMENT:**
   - Multiplier on Goalkeeper / Defender Clean Sheet probability:
     \[
     P(	ext{CS\_adj}) = P(	ext{CS\_base}) 	imes (1.0 + 0.20 	imes 	ext{DEFENCE\_ENVIRONMENT})
     \]
   - Enables identifying high-probability clean sheets in low-scoring tactical stalemates.

3. **TRANSITION_ENVIRONMENT:**
   - Multiplier on counter-attacking forward ceiling and haul probability.

4. **CONTROL_ENVIRONMENT:**
   - Multiplier on central midfielder baseline floor points (passes, baseline bonus).

*Status: Specification only. No FPL modification executed in this research sprint.*
