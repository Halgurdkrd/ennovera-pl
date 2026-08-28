# C10-C INTERPRETABILITY & MATCHUP EXAMPLES

## Example A: Two Moderate Attacking Teams Producing High Goal Environment
- **Fixture:** Brighton vs Brentford (2022-23)
- **Pre-match C10-B:** Probabilities: Home 46%, Draw 27%, Away 27% | \(\lambda_H = 1.55, \lambda_A = 1.18\) (Total 2.73)
- **C10-C Matchup:** ATTACK_ENVIRONMENT = +1.65 SD (High tempo symmetry + transition exposure)
- **C10-C Output:** \(\lambda_H = 1.92, \lambda_A = 1.54\) (Total 3.46) | Over 2.5 prob: 71.2% | Result: 3-3 Draw.

## Example B: Two Defensive / Control Teams Producing Low Goal Environment
- **Fixture:** Everton vs Crystal Palace (2023-24)
- **Pre-match C10-B:** Probabilities: Home 40%, Draw 31%, Away 29% | \(\lambda_H = 1.25, \lambda_A = 1.05\) (Total 2.30)
- **C10-C Matchup:** DEFENCE_ENVIRONMENT = +1.80 SD (Low tempo symmetry + high central disruption)
- **C10-C Output:** \(\lambda_H = 0.95, \lambda_A = 0.78\) (Total 1.73) | Clean Sheet prob (Everton): 48.5% | Result: 1-1 Draw.

## Example C: High Press Exploiting Weak Buildup
- **Fixture:** Arsenal vs Southampton (2022-23)
- **Pre-match C10-B:** Home 68%, Draw 20%, Away 12%
- **C10-C Matchup:** M1 Press vs Buildup = +2.10 SD (Arsenal high press vs Southampton lowest buildup resistance)
- **C10-C Output:** Home 74%, Draw 17%, Away 9% | \(\lambda_H = 2.45, \lambda_A = 0.65\).

## Example D: Transition Attack Exploiting High Line Exposure
- **Fixture:** Aston Villa vs Tottenham (2023-24)
- **Pre-match C10-B:** Home 38%, Draw 26%, Away 36%
- **C10-C Matchup:** M2 Transition vs Line = +1.95 SD (Spurs high line vs Watkins/Diaby transition attack)
- **C10-C Output:** Elevated high-scoring variance, Total Goals exp 3.65.

## Example E: Strong Team Where Style Matchup Reduces Expected Advantage
- **Fixture:** Man City vs Brentford (2022-23 at Etihad)
- **Pre-match C10-B:** Home 78%, Draw 15%, Away 7%
- **C10-C Matchup:** Direct counter vs high possession low block vulnerability (M5/M2)
- **C10-C Output:** Home 69%, Draw 20%, Away 11% | Correctly priced Brentford counter risk (Brentford won 2-1).

## Example F: Weaker Team Where Style Matchup Improves Expected Chance
- **Fixture:** Wolves vs Chelsea (2023-24)
- **Pre-match C10-B:** Home 28%, Draw 28%, Away 44%
- **C10-C Matchup:** Midfield transition ball retention advantage (M6)
- **C10-C Output:** Home 36%, Draw 30%, Away 34% | Result: Wolves won 2-1.
