# ENNOVERA PL + FPL — Future PL Feature Candidates from FPL Player State

**Research Focus:** Identification of High-Potential Player-Level Features Learned in FPL Research for Future Premier League Match Prediction.

---

## 1. Candidate Feature Inventory

| Candidate Feature Concept | FPL Derivation Mechanism | Hypothesized PL Prediction Impact | Target Mechanism |
|---|---|---|---|
| **Starting XI Aggregate Market Cap** | $\sum_{i \in \text{XI}} \text{Price}_i$ | Lineup sensitivity for rotated cup/European squads | Identifies heavily rotated lineups before kickoff |
| **Aggregate Lineup Haul Threat** | $\sum_{i \in \text{XI}} P(\text{Haul}_i)$ | Upset and high-variance match prediction | Captures explosive transition teams (e.g. Brighton, Villa) |
| **Defensive Clean Sheet Index** | $\prod_{d \in \text{DEF}} P(\text{CS}_d)$ | Draw calibration and low-scoring fixture identification | Improves draw detection in tight 0-0 / 1-1 encounters |
| **Set-Piece Specialist Presence** | $\max_{i \in \text{XI}} (\text{xA}_i + \text{Bonus}_i)$ | Dead-ball efficiency against low blocks | Improves underdog away match modeling |

---

## 2. Research Guardrail Note
`CORE_BASE` remains **strictly frozen at 191 / 380 = 50.26%**. These feature candidates will be evaluated only in dedicated future PL prediction tournament phases.

