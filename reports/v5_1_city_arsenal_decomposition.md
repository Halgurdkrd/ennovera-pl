# Manchester City vs Arsenal — Forensic Decomposition & Trace

**Focus:** Component-by-Component Comparison between Manchester City and Arsenal in V2, V4, and V5.1.  
**Data Sources:** `data/raw/fpl_history/2026-27/players_raw.csv`, `cleaned_players.csv`, `current_elo.csv`, `v4_dynamic_team_states.csv`.

---

## 1. Ground Truth Source Verification (Haaland & Squad Valuations)

### A. Erling Haaland Source Data
- **Source File:** `data/raw/fpl_history/2026-27/players_raw.csv` (Row ID: `Erling_Haaland_411`)
- **2025–26 Minutes:** **2,953 minutes**
- **2025–26 Expected Goals ($xG$):** **25.50**
- **Actual 2025–26 xG/90:** $\mathbf{0.777\text{ xG/90}}$ (Note: The stylized figure of 0.85 reported previously was an informal estimate; true source value is 0.777).
- **Historical Career Context:**
  - 2022–23: 28.54 xG in 2767 mins = **0.928 xG/90**
  - 2023–24: 29.57 xG in 2553 mins = **1.042 xG/90**
  - 2024–25: 21.90 xG in 2736 mins = **0.720 xG/90**
  - 2025–26: 25.50 xG in 2953 mins = **0.777 xG/90**

### B. Squad Cost & Bench Depth (FPL Ground Truth)

| Metric | Manchester City (Team ID 15) | Arsenal (Team ID 1) | Differential ($\Delta$) |
|---|---|---|---|
| **Total Squad Size** | 30 players | 28 players | +2 players |
| **Top 11 FPL Value** | £85.5m | £79.5m | +£6.0m |
| **Bench (Next 7) FPL Value** | £40.0m | £41.5m | -£1.5m |
| **Total Squad FPL Value** | £185.0m | £175.0m | +£10.0m |
| **Top 11 2025–26 xG/90 Sum** | 2.65 xG/90 | 2.52 xG/90 | +0.13 xG/90 |

> [!NOTE]
> The previously cited heuristic figure "£118.5m bench depth" reflected an uncalibrated transfer market estimate; the actual direct FPL valuation of the next 7 players is £40.0m (City) vs £41.5m (Arsenal).

---

## 2. Component Differential Matrix (City vs Arsenal)

| Component / Parameter | Manchester City | Arsenal | Net Advantage | Match Prob Impact | Season xPts Impact | Title % Impact |
|---|---|---|---|---|---|---|
| **Derived Elo Rating** | 1765.2 | **1784.8** | **Arsenal (+19.6)** | Arsenal +2.2% | Arsenal +0.8 xPts | Arsenal +7.0pp |
| **Previous Season Position** | 2nd | **1st** | **Arsenal (+1 pos)** | Arsenal +0.8% | Arsenal +0.3 xPts | Arsenal +2.5pp |
| **V4 Decayed Attack State** | **1.120** | 1.090 | **City (+0.030)** | City +1.8% | City +0.6 xPts | City +5.2pp |
| **V4 Decayed Defence State** | **0.910** | 0.930 | **City (+0.020)** | City +1.2% | City +0.4 xPts | City +3.5pp |
| **Expected XI Attack Multiplier**| **1.624** | 1.580 | **City (+0.044)** | City +1.5% | City +0.5 xPts | City +4.4pp |
| **Expected XI Creativity** | **1.232** | 1.199 | **City (+0.033)** | City +0.8% | City +0.3 xPts | City +2.3pp |
| **FPL Fixture Difficulty (Away)**| **5 (Max)** | 4 | **City (+1 rating)** | City +1.0% | City +0.3 xPts | City +2.8pp |

---

## 3. Title Sensitivity Curve (Controlled Elo Shifts)

Simulation with controlled shifts in City Elo relative to Arsenal:

| City $\Delta \text{Elo}$ vs Arsenal | City xPts | Arsenal xPts | xPts Gap | City Champ % | Arsenal Champ % | Title Gap |
|---|---|---|---|---|---|---|
| **-50 Elo** | 72.39 | 71.95 | +0.44 | 39.97% | 37.48% | +2.49pp |
| **-30 Elo** | 75.81 | 71.56 | +4.25 | 55.57% | 28.46% | +27.11pp |
| **-20 Elo (Baseline ~ -19.6)** | 76.82 | 71.59 | +5.23 | **59.56%** | **26.40%** | **+33.16pp** |
| **0 Elo (Equal Rating)** | 75.63 | 71.31 | +4.32 | 55.02% | 27.98% | +27.04pp |
| **+20 Elo** | 77.77 | 70.90 | +6.87 | 65.05% | 22.05% | +43.00pp |

