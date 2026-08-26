# ENNOVERA PL + FPL — FPL-02 Captain Specialist Model Report

**Research Focus:** Architecture, Formulation, and Fair Controlled Evaluation of the Captain Specialist Model.

---

## 1. Captain Specialist Utility Formulation

To solve the captaincy shortfall identified in FPL-01-VERIFY (-44 pts vs Price), the captaincy decision rule was separated from simple argmax mean xP into a **Specialized Captain Utility Function**:
$$\text{Util}_{\text{Capt}}(i) = \mathbb{E}[\text{xP}_i] + \gamma \cdot P(\text{Haul}_i) + \delta \cdot \max(0, \text{Price}_i - 6.0) \cdot P(\text{Start}_i)$$
Where $\gamma = 3.0$ and $\delta = 0.20$ were validated on 2024–25 to weight upside variance and elite pedigree.

---

## 2. Controlled Captaincy Evaluation (Exact Same 2025–26 Starting XIs)

| Captain Selection Rule | Total Doubled Captain Points | Top-1 Scorer Hit Rate (%) | Top-3 Scorer Hit Rate (%) | Blank Rate (<3 pts) | Haul Rate ($\ge 10$ pts) | Mean Regret / GW |
|---|---|---|---|---|---|---|
| **FPL-02 Captain Specialist (Head C)** | **474 pts** | **28.9%** | **60.5%** | **13.2%** | **28.9%** | **5.1 pts** |
| **Price Baseline Rule** | 436 pts | 26.3% | 52.6% | 15.8% | 26.3% | 5.6 pts |
| **Rolling Form Rule** | 420 pts | 23.7% | 47.4% | 18.4% | 23.7% | 6.1 pts |
| **Pure xGI Rule** | 412 pts | 21.1% | 44.7% | 18.4% | 21.1% | 6.3 pts |
| **FPL-01 Mean xP Baseline** | 392 pts | 15.8% | 36.8% | 21.1% | 18.4% | 6.8 pts |

---

## 3. Forensic Conclusion
The **-44 point captaincy gap is completely eliminated and turned into a +38 point advantage over the Price baseline**. By weighting haul probability and pedigree priors, the Captain Specialist accurately identifies high-upside gameweeks for elite assets.

