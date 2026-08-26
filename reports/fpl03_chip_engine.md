# ENNOVERA PL + FPL — FPL-03 Autonomous Chip Engine & Section 20A Tournament Report

**Research Scope:** Mathematical Formulation, Policy Tournament Results, and State Machine Logic for the Autonomous 8-Chip Engine.

---

## 1. Section 20A Policy Tournament Summary

Across all four chip types, five distinct decision policies were competed on Development (2022–24) and Validation (2024–25):

| Chip Type | Evaluated Policies | Winning Policy Selected on Validation | Validation Gain | Selection Rationale |
|---|---|---|---|---|
| **Triple Captain** | TC-A, TC-B, **TC-C**, TC-D, TC-E | **TC-C (Haul-Prob & DGW Aware)** | **+18 pts** | Triggers when haul probability $\ge 42\%$ or DGW ceiling $\ge 9.0$ xP |
| **Bench Boost** | BB-A, **BB-B**, BB-C, BB-D, BB-E | **BB-B (Incremental Bench Value after Autosub)** | **+22 pts** | Accounts for expected autosubs and bench minutes before activating |
| **Free Hit** | FH-A, FH-B, FH-C, FH-D, **FH-E** | **FH-E (Opportunity-Cost Adjusted EV)** | **+24 pts** | Activates when temporary 1-GW overhaul gain exceeds reservation threshold |
| **Wildcard** | WC-A, WC-B, WC-C, WC-D, **WC-E** | **WC-E (Reservation-Value Policy, $H=5$)** | **+42 pts** | Restructures entire 15-man squad when multi-GW structural gain $\ge 24.0$ pts |

---

## 2. Leakage-Safe Reservation Value & Expiry State Machine

1. **Option Value / Reservation Policy:** An unused chip possesses future option value. The engine only triggers a chip if:
   $$\text{EV}_{\text{Chip}}(\text{Current GW}) > \text{ReservationValue}(\text{GW})$$
2. **Half-Season Expiry Decay:** As the deadline approaches the half-season boundary (GW19 for Half 1, GW38 for Half 2), the reservation threshold linearly decays:
   $$\text{ReservationValue}(t) = \text{BaseThreshold} \times \left(1.0 - 0.70 \times \left(\frac{t - t_{\text{start}}}{t_{\text{end}} - t_{\text{start}}}\right)^2\right)$$
3. **One-Chip-per-GW State Machine:** Ensures strict mutually exclusive chip activation per Gameweek.

