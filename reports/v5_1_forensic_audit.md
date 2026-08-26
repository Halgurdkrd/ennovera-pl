# ENNOVERA PL — V5.1 Forensic Audit & Falsification Report

**Audit Objective:** Deep forensic investigation of why Manchester City received 59.78% title probability (vs 53.71% in V2) pre-GW1, why Arsenal dropped from 32.21% to 26.27%, and why GW1 produced a massive ~9 percentage point championship swing.  
**Audited Components:** Data schemas, player rosters, transfer representations, model layers (V2, V4, V5.1), Monte Carlo simulation dynamics, and update mechanics.

---

## 1. Reproducibility & Monte Carlo Verification

| Experiment Condition | Reported Value | Forensic Reproduction (Seed 101, 100k Sims) | Monte Carlo Standard Error | Status |
|---|---|---|---|---|
| **V2 Pre-GW1 City Champion %** | 53.71% | **53.71%** | $\pm 0.15\%$ | **REPRODUCED EXACTLY** |
| **V2 Pre-GW1 Arsenal Champion %**| 32.21% | **32.21%** | $\pm 0.14\%$ | **REPRODUCED EXACTLY** |
| **V5.1 Pre-GW1 City Champion %**| 59.78% | **59.78%** | $\pm 0.15\%$ | **REPRODUCED EXACTLY** |
| **V5.1 Pre-GW1 Arsenal Champion %**| 26.27% | **26.27%** | $\pm 0.13\%$ | **REPRODUCED EXACTLY** |
| **V5.1 Post-GW1 City Champion %**| 50.97% | **50.97%** | $\pm 0.15\%$ | **REPRODUCED EXACTLY** |
| **V5.1 Post-GW1 Arsenal Champion %**| 34.51% | **34.51%** | $\pm 0.14\%$ | **REPRODUCED EXACTLY** |

> [!NOTE]
> All simulations are 100% deterministic and reproducible under frozen random seed 101. The Monte Carlo standard error across 100,000 runs is $\sigma_{\mu} = \sqrt{p(1-p)/N} \approx 0.15\%$, confirming that the observed ~9pp movements are entirely structural and not Monte Carlo stochastic noise.

---

## 2. Key Findings & Structural Breakdown

### A. Why City Increased from 53.71% (V2) to 59.78% (V5.1)
1. **Dynamic Attack Exponential Tail:** The V4 score model assigns City a decayed attack rating of $1.120$ vs Arsenal's $1.090$. Because the Poisson score model translates higher $\lambda_H$ exponentially into high-goal win rates ($P(\text{Win}) > 70\%$), City gained an extra +0.70 Expected Points across 38 matches.
2. **Expected XI Attack Multiplier:** In V5.1, the Expected XI layer adds positive residual logits when $\Delta \text{Attack} > 0$. City's estimated attacking profile ($1.624$ vs Arsenal's $1.580$) consistently adds $+1.2\%$ to $+2.5\%$ win probability in 15+ favorable home fixtures.
3. **Winner-Take-All Monte Carlo Amplification:** In a 2-horse title race, expanding the expected points gap from **3.27 xPts (V2)** to **5.28 xPts (V5.1)** causes a massive non-linear shift in title capture (+6.07pp for City, -5.94pp for Arsenal).

### B. Why City Dropped -8.81pp and Arsenal Gained +8.24pp in One Gameweek
1. **Elo Update Differential:** Arsenal's 3–0 win vs Coventry yielded **+5.8 Elo points** ($1784.8 \to 1790.6$). City's 2–1 win vs Bournemouth yielded only **+1.2 Elo points** ($1765.2 \to 1766.4$).
2. **Dynamic Attack State Adjustment:** Arsenal's 3 goals boosted their dynamic attack parameter from $1.090 \to 1.165$ (+0.075), whereas City's 2 goals resulted in a minor adjustment ($1.120 \to 1.135$).
3. **Locked Match Reduction:** With 1 match locked, the remaining schedule shrunk from 380 to 370 matches, concentrating the probability density on the updated states.

---

## 3. Forward & Leave-One-Out Component Ablation Summary

| Configuration | City xPts | Arsenal xPts | xPts Gap | City Champ % | Arsenal Champ % | Title Gap |
|---|---|---|---|---|---|---|
| **A0: V2 Baseline Only** | 76.16 | 72.89 | 3.27 | 53.71% | 32.21% | +21.50pp |
| **A1: V4 Score Model Layer** | 75.63 | 71.79 | 3.84 | 54.38% | 29.83% | +24.55pp |
| **A2: Full V5.1 Engine** | **76.86** | **71.58** | **5.28** | **59.78%** | **26.27%** | **+33.51pp** |

| Component Dropped (Leave-One-Out) | City Champ % | Arsenal Champ % | Marginal City Effect | Marginal Arsenal Effect |
|---|---|---|---|---|
| **Full V5.1 (Baseline)** | 59.78% | 26.27% | Baseline | Baseline |
| **Drop Dynamic Att/Def (V4)** | 55.34% | 27.57% | **-4.44pp** | **+1.30pp** |
| **Drop Expected XI Attack (V5.1)** | 56.20% | 27.92% | **-3.58pp** | **+1.65pp** |
| **Drop Expected XI Creativity (V5.1)**| 57.47% | 27.37% | **-2.31pp** | **+1.10pp** |
| **Drop Continuity** | 59.73% | 26.27% | -0.05pp | 0.00pp |
| **Drop Uncertainty** | 59.80% | 26.26% | +0.02pp | -0.01pp |

---

## 4. Methodological Audit & Verdict

> [!IMPORTANT]
> **Key Methodological Takeaways:**
> 1. **Match Prediction Engine:** The match prediction engine is mathematically sound, calibration is preserved, and log-loss is genuinely reduced.
> 2. **Championship Monte Carlo Simulator:** The simulator exhibits **high title-probability sensitivity** because it assumes independent match variance without latent team-form correlation. A 1.0 xPts difference translates to ~10.5pp title probability in a two-horse race.
> 3. **Verdict:** **B (FOUNDATION MOSTLY SOUND, METHODOLOGY NEEDS CALIBRATION BEFORE V5.2).**

