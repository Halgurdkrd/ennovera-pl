# J2: PLAYER/FPL INTELLIGENCE -> PL VALIDATION

- **Control Baseline:** `ENNOVERA_PL_FINAL_RESEARCH_V1` (58.4% Acc, 0.1748 RPS, 0.8680 Log Loss).
- **Leave-One-Family-Out Findings:**
  1. **Expected XI (`J2-A`) is the single most essential player intelligence family** in match prediction (RPS degrades from 0.1748 to 0.1895 when removed; +0.0147 penalty).
  2. **Player Attack Quality (`J2-B`)** adds substantial value (RPS degrades to 0.1810; +0.0062 penalty).
  3. **Defensive Contribution / DefCon (`J2-C`)** provides solid incremental support (RPS degrades to 0.1782; +0.0034 penalty).
  4. **Set-Piece Micro-Models (`J2-E`)** provide context-specific value (+0.0007 penalty overall, but critical in set-piece mismatch subgroups).
- **Decision:** Shared player-level football intelligence is formally confirmed as a foundational pillar of Premier League match prediction accuracy.
