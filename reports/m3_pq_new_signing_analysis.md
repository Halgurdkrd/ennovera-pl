# ENNOVERA PL — M3-PQ New-Signing & Promoted Team Prior Analysis

**Audit Focus:** Benchmarking Prior Initialization Strategies for Foreign Transfers and Newly Promoted Squads with Zero Premier League History.

---

## 1. New-Signing Prior Benchmark Experiment (N0 to N4)

Evaluated across all 114 historical player transfers entering the Premier League with $<500\text{ minutes}$ of prior domestic match history (e.g. Erling Haaland 2022, Dominik Szoboszlai 2023, Riccardo Calafiori 2024):

| Prior Strategy Code | Prior Initialization Description | Player Future xGI Error (MAE) | Team Match Log-Loss (First 5 Matches) | Strategic Quality Status |
|---|---|---|---|---|
| **N0** | Generic Positional Baseline (0.25 FW / 0.12 MF) | 0.185 | 1.01850 | Uninformative / High Noise |
| **N1** | Cross-League Statistical Translation Only | 0.124 | 0.98540 | Solid Empirical Baseline |
| **N2** | EA FC OVR Prior Only | 0.118 | 0.97820 | Informative General Quality |
| **N3** | EA FC Position-Specific Attribute Prior (SHO/PAS/DEF) | 0.105 | 0.96540 | High Positional Fidelity |
| **N4** | **Cross-League Statistics + EA FC Quality Fusion** | **0.089 (Best)** | **0.95780 (Best)** | **OPTIMAL TRANSFER ENGINE** |

---

## 2. Promoted & High-Turnover Squad Performance

| Subgroup Category | Match Count (Holdout 2025–26) | Canonical F2 Log-Loss | Candidate M1-D Log-Loss | Candidate PQ7 Log-Loss | Delta Log-Loss ($\Delta\text{LL}$ vs F2) |
|---|---|---|---|---|---|
| **Promoted Teams** | **19 matches** | 0.72748 | 0.70383 | **0.70120** | **-0.02628 (Substantial Gain)** |
| **High Squad Turnover ($\text{Cont} < 0.75$)**| **13 matches** | 0.65619 | 0.62522 | **0.62190** | **-0.03429 (Substantial Gain)** |
| **Foreign Transfer Heavy Matches** | **22 matches** | 0.98540 | 0.96210 | **0.95780** | **-0.02760 (Substantial Gain)** |
| **Stable Top-6 Contenders** | **155 matches** | 0.94210 | 0.94190 | **0.94160** | **-0.00050 (Safe / Robust)** |

### Core Finding on New Signings & Promoted Teams:
- **Where Player Quality Shines:** For foreign signings and promoted squads with zero PL history, EA FC position attributes provide immediate, calibrated quality metrics that save **$-0.02628\text{ to }-0.03429$ Log-Loss**, bridging the gap while empirical match data accumulates.

