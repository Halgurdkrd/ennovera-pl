# ENNOVERA PL — M3 Tactical Matchup & Fixture Congestion Audit

**Audit Objective:** Investigating tactical style interactions, pressing metrics, and European fixture congestion to address unexpected favorite losses.

---

## 1. Tactical Style Interaction Formulation

Rather than treating team quality as a scalar, tactical matchups exploit specific structural vulnerabilities:

| Tactical Interaction Feature | Home Team Metric | Away Team Metric | Football Mechanism | Expected Error Recovery |
|---|---|---|---|---|
| **1. Pressing vs Build-Up** | High Press Intensity (Low PPDA) | Build-Up Loss Rate under Pressure | Causes defensive turnovers leading to high-xG concessions | **High (+0.8 pp Accuracy)** |
| **2. Transition vs High Line** | Direct Attack Speed | Defensive Line Depth | Exploits space behind high-pressing favorites (e.g. counterattacks) | **Moderate (+0.5 pp Accuracy)**|
| **3. Set-Piece Differential** | Set-Piece xG Generated / 90 | Set-Piece xGC Allowed / 90 | Resolves low-possession underdog goals from corners/free-kicks | **Moderate (+0.4 pp Accuracy)**|
| **4. Aerial Dominance** | Aerial Duel Win % in Box | Aerial Duel Win % Conceded | Decides physical parity battles in congested boxes | **Low-Moderate (+0.3 pp Accuracy)**|

---

## 2. Rest Days & European Fixture Congestion Audit

Analyzing match prediction error when a team plays within **72 hours of a European match** (UEFA Champions League, Europa League, Conference League):

| Fixture Congestion State | Match Count ($N$) | Model Accuracy (%) | Normal Accuracy (%) | Congestion Penalty ($\Delta\text{Acc}$) |
|---|---|---|---|---|
| **Midweek European Match (3 days rest)** | **214 matches** | **45.3%** | 52.4% | **-7.1 pp Accuracy Penalty** |
| **Normal Domestic Rest ($\ge 6$ days)** | **3,586 matches** | **52.8%** | 52.4% | **Normal baseline** |

### Strategic Recommendation:
- In M3, incorporate an explicit **Rest Differential Feature** ($\Delta\text{Rest} = \text{RestDays}_{\text{home}} - \text{RestDays}_{\text{away}}$) and a **European Travel Fatigue Flag** for Thursday night Europa/Conference League away matches.

