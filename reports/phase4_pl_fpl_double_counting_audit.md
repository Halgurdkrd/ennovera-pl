# ENNOVERA PHASE 4 — PL <-> FPL DOUBLE-COUNTING AUDIT

## Signal Redundancy & Integration Audit
| Candidate PL Signal | Phase 3 Analog | Classification | Integration Treatment |
|---|---|---|---|
| Match H/D/A Probability | Elo Difference | UNIQUE | Integrated as match tempo / environment modulator |
| PL Team Expected Goals | Heuristic Venue + FDR | UNIQUE REPLACEMENT | Replaces heuristic FDR with calibrated Poisson rate lambda |
| PL Clean Sheet Probability | Rolling CS_5 | UNIQUE REPLACEMENT | Replaces trailing clean sheet rate with Poisson zero-goal probability |
| Expected XI Lineup Index | None | UNIQUE | Scales team attacking/defensive capacity |
| Player-Aware Team Value | Player Prior | PARTIALLY REDUNDANT | Constrained within player-share allocation |

**Audit Finding:** PASS (Zero Double-Counting). All heuristic fixture multipliers are superseded by calibrated PL rate engines.
