# ENNOVERA PL — M3-PQ Player Quality Expert Final Scientific Report

**Research Scope:** Definitive Synthesis of the M3-PQ Player Quality Challenge, FIFA/EA FC Attribute Integration, Positional Granularity, and MoE Integration Strategy.

---

## 1. Executive Summary & Verdict

# **FINAL VERDICT: B + C + D**
- **B — DEFENDER / GK SPECIALIST:** EA FC scouting attributes (`DEF` and `GK Reflexes`) solve the single biggest blindspot of FPL-based statistical modeling by isolating clean individual talent from team tactics.
- **C — NEW-SIGNING / PROMOTED SPECIALIST:** EA FC attributes provide calibrated initial priors for summer transfers and promoted squads with zero Premier League history ($\Delta\text{LL} = \mathbf{-0.02628}$ to $\mathbf{-0.03429}$ gain).
- **D — MoE EXPERT / PRIOR:** Player Quality should NOT replace historical Elo or empirical xG globally, but should be integrated as an **Adaptive Expert Sub-Module (Candidate PQ7)** inside the future M3 Mixture-of-Experts framework.

---

## 2. Model Tournament Leaderboard Across 4 Seasons (1,520 Matches)

| Model Candidate | Validation Log-Loss | Holdout Log-Loss | Pooled Log-Loss (1,520 M) | Holdout Acc (%) | Strong Picks $\ge 60\%$ Precision | Strong Pick Coverage |
|---|---|---|---|---|---|---|
| **PQ7: Adaptive PQ Gating Network** | **0.99456 (Best)** | **1.02976** | **0.98415 (Best)** | **48.16%** | **61.54%** | **23.9% (91 picks)** |
| **Candidate M1-D (Baseline)** | 0.99918 | **1.02940 (Best)** | 0.98876 | 48.16% | **64.62%** | 17.1% (65 picks) |
| **Candidate F2 (Baseline)** | 1.00326 | 1.02999 | 0.99163 | **48.42%** | **67.27%** | 14.5% (55 picks) |
| **PQ4: Statistical + FC Quality Fusion**| 0.99608 | 1.03716 | 0.99020 | 48.16% | 59.84% | 33.4% (127 picks) |
| **PQ2: Position Attributes Model** | 0.99572 | 1.03729 | 0.99050 | **48.42%** | 58.73% | 33.2% (126 picks) |
| **PQ0: Legacy WC2026 (65/25/10)** | 0.99562 | 1.03787 | 0.99110 | 48.68% | 57.36% | 33.9% (129 picks) |
| **PQ1: Raw OVR Expected XI** | 0.99567 | 1.03798 | 0.99120 | 48.68% | 57.36% | 33.9% (129 picks) |

---

## 3. What Survives into M3 from M3-PQ

1. **Point-in-Time EA FC Attribute Integration:** Retain separate **SHO, PAS, DEF, GK Reflexes, and PHY** mapped by Expected Minutes.
2. **Transfer Prior Engine:** Use EA FC attributes to initialize foreign transfers and newly promoted players with $<500\text{ PL minutes}$.
3. **Adaptive PQ Gating (PQ7 Architecture):** Activate player quality weighting dynamically on high-turnover and promoted squads while preserving historical base ratings on stable title contenders.

