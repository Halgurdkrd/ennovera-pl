# ENNOVERA PL + FPL — FPL-02 Price as a Latent Quality Prior Analysis Report

**Research Focus:** Investigation of Official Player Pricing as a Latent Quality and Role Prior in Statistical Modeling.

---

## 1. The Information Content of FPL Price

In FPL-01-VERIFY, the standalone Price baseline scored 1,997 points in 2025–26, demonstrating that price contains significant predictive signal. 

Official FPL pricing is set by market makers and updated by millions of managers. It reflects:
1. **Starting Status & Job Security:** Sub-£4.5m outfield players rarely start regularly, whereas £7.0m+ players have established status.
2. **Set-Piece & Penalty Duties:** Penalty takers and corner kickers are systematically priced at premiums.
3. **Historical Pedigree:** Multi-season performance history is distilled into price.

---

## 2. Experimental Ablation on Validation (2024–25)

| Price Integration Scheme | Validation Total Score | Top-5% Elite MAE | NDCG@25 |
|---|---|---|---|
| **No Price Information (Raw Component xP)** | 1,985 pts | 4.98 | 0.725 |
| **Linear Price Term in xP** | 2,038 pts | 4.12 | 0.782 |
| **Ennovera Decision-Aligned Price Surplus ($\alpha \cdot \max(0, P - 4.5) \cdot P(\text{Start})$)** | **2,070 pts** | **3.78** | **0.814** |

---

## 3. Key Finding
Using price as a **conditional threshold prior** ($\max(0, \text{Price} - 4.5) \cdot P(\text{Start})$) rather than an unconditional linear feature prevents distorting non-playing budget enablers while restoring full value to elite starters.

