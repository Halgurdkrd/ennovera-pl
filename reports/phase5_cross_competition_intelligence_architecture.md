# ENNOVERA PHASE 5.1 — CROSS-COMPETITION INTELLIGENCE ARCHITECTURE

## 1. Normalized Intelligence Paradigm
Cross-competition statistics are never naively added as raw points. Instead, underlying performance rates are normalized against opponent Elo and competition difficulty:
$$\text{Norm\_xG90} = \text{Observed\_xG90} \times \left(\frac{\text{Opponent\_Elo}}{1500}\right)^{\alpha} \times \text{Comp\_Factor}$$

## 2. 10-Layer Information Hierarchy
1. **Layer 1:** Long-Term Intrinsic Player Quality (Multi-season prior)
2. **Layer 2:** Premier League Recent Form (Rolling 5-GW shifted)
3. **Layer 3:** Cross-Competition Underlying Performance (UCL/UEL/Cup xG90/xA90)
4. **Layer 4:** Expected Minutes & Availability Engine (V2 Probabilistic)
5. **Layer 5:** Positional Matchup & Concession Intelligence (Phase 3 Engine)
6. **Layer 6:** Premier League Team Scoring Environment (V5.1 Expected-XI $\lambda$)
7. **Layer 7:** Workload, Travel & Midweek Congestion (`FixtureLoadIndex`)
8. **Layer 8:** Player-Team Interaction & Role Share
9. **Layer 9:** Additive FPL Component Scoring
10. **Layer 10:** Match Uncertainty & Captain Reservation Value
