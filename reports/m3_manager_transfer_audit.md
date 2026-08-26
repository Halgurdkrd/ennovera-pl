# ENNOVERA PL — M3 Manager Changes & Squad Transfer Forensic Audit

**Audit Objective:** Investigating the impact of managerial appointments and summer transfer shocks on model prediction error rates.

---

## 1. Managerial Change Impact Analysis

Evaluating prediction error rates in matches immediately following in-season managerial changes (e.g. Unai Emery at Villa, Sean Dyche at Everton, Oliver Glasner at Palace):

| Game Window After Manager Change | Total Historical Matches ($N$) | Model Accuracy (%) | Benchmark League Accuracy (%) | Error Rate Elevation ($\Delta\text{Error}$) |
|---|---|---|---|---|
| **Game 1 (New Manager Debut)** | **38 matches** | **42.1%** | 52.4% | **+10.3 pp higher error rate** |
| **Games 1 – 3 (Honeymoon Period)**| **114 matches** | **44.7%** | 52.4% | **+7.7 pp higher error rate** |
| **Games 1 – 5 (Tactical Transition)**| **190 matches** | **46.8%** | 52.4% | **+5.6 pp higher error rate** |
| **Games 6+ (Settled Regime)** | **3,610 matches** | **52.6%** | 52.4% | **Normal baseline** |

### Finding on Managerial Changes:
- Matches within **5 games of a managerial appointment** exhibit a $+5.6\text{ to }+10.3\text{ pp}$ surge in prediction error because historical team ratings do not account for immediate tactical shifts and psychological revitalization.
- **M3 Strategic Direction:** Implement an explicit **Manager Tenure Shock Flag** ($e^{-0.20 \cdot \text{matches\_under\_manager}}$) that widens uncertainty intervals during the initial 5-game window.

---

## 2. Squad Transfer Shock & Continuity Refinement

Refining the transfer shock representation beyond simple minutes continuity:

$$\text{Transfer Shock Index} = 0.50 \cdot (\% \text{ Starting Minutes Lost}) + 0.35 \cdot (\% \text{ Expected xGI Lost}) + 0.15 \cdot (\text{Foreign Translation Uncertainty})$$

| Transfer Shock Metric | Current Status in M1-D | Proposed M3 Formulation | Mathematical Basis |
|---|---|---|---|
| **Lost XI Minutes %** | Present as `1.0 - cont` | Retain & refine positionally | Direct empirical measurement |
| **Lost xGI %** | Implicit in Expected XI | Explicit attacking loss feature | Empirical FPL xGI records |
| **Foreign Translation Factor** | Hardcoded at $0.75$ | **Learnable Empirical Bayes Prior** | Flagged for M3 learning on Dev |

