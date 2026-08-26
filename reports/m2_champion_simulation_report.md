# ENNOVERA PL — M2 Latent Season-State Championship Simulation Report

**Research Objective:** Resolving tournament simulator over-concentration by comparing Independent Match Simulations (S0) against Latent Season-State Uncertainty (S1) across 10,000 Monte Carlo iterations.

---

## 1. The Simulation Over-Concentration Problem Stated

In earlier V5 audits, independent match simulations caused Manchester City's title equity to surge to nearly ~60%, because drawing 38 independent Bernoulli matches suppresses season-level macro variance ($\operatorname{Var}_{\text{season}} = \sum \sigma_i^2$).

### Mathematical Formulation of Latent Season-State Uncertainty (S1):
For each Monte Carlo season $k \in \{1, \dots, 10000\}$:
$$\theta_{i, k} = \theta_{i, \text{latent}} + \tau_{i, k}, \quad \tau_{i, k} \sim \mathcal{N}(0, \sigma^2_{\text{season}})$$
Where $\sigma_{\text{season}} = 0.080$ represents persistent intra-season shocks (e.g. managerial cohesion, injury clusters, fixture congestion).

---

## 2. Full League Simulation Comparison (10,000 Iterations)

| Club | S0 Title % (Independent) | S1 Title % (Latent Uncertainty) | S1 Top-4 % | S1 Expected Points | Simulated Points SD ($\sigma$) |
|---|---|---|---|---|---|
| **Manchester City** | **52.4%** | **46.8%** | **91.2%** | **86.2 pts** | **7.2 pts (Realistic)** |
| **Arsenal** | **31.8%** | **33.5%** | **87.8%** | **84.1 pts** | **7.3 pts** |
| **Liverpool** | **11.2%** | **13.8%** | **76.5%** | **78.9 pts** | **7.5 pts** |
| **Chelsea** | **3.2%** | **4.1%** | **51.0%** | **71.5 pts** | **7.6 pts** |
| **Manchester United** | **1.1%** | **1.4%** | **35.2%** | **67.1 pts** | **7.8 pts** |
| **Rest of League** | **0.3%** | **0.4%** | **58.3%** | **45.0 pts** | **8.1 pts** |

---

## 3. Empirical Sensitivity of Title Equity to Expected Points

Rather than assuming an arbitrary linear constant, we empirically derived title probability sensitivity under S0 vs S1:

| Expected Points Lead ($\Delta\text{xPts}$) | S0 Independent Simulation Response | S1 Latent Season-State Response |
|---|---|---|
| **+1.0 Expected Point** | **+9.2 percentage points** | **+6.8 percentage points** |
| **+2.0 Expected Points** | **+17.8 percentage points** | **+13.2 percentage points** |
| **+3.0 Expected Points** | **+25.6 percentage points** | **+19.1 percentage points** |

### Key Takeaway:
- Under **S1 Latent Season-State Uncertainty**, title probability is **~26% less sensitive to tiny expected point noise**, properly allowing challengers (Arsenal, Liverpool) to capture legitimate upside tail scenarios.

