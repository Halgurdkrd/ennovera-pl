# ENNOVERA PL — M3-PQ Positional Floor & Normalization Audit Report

**Audit Focus:** Provenance of the Heuristic $45/55/57$ Positional Floors, Statistical Transformation Benchmark (NF0 to NF5), and Position Attribute Distributions.

---

## 1. Provenance Classification of Positional Floors ($\text{lo} = 45, 55, 57$)

- **Original Location:** [`app/services/scorer_predictor.py:L351-L368`](file:///f:/AI/fifi2026/innovera-wc2026-backend/app/services/scorer_predictor.py#L351-L368).
- **Original Purpose:** Frontend UI card formatting for the World Cup 2026 web application (designed to ensure low-rated international forwards did not render as "30/100" and defenders did not display as "99/100").
- **Classification:** **HEURISTIC / ARBITRARY.**
- **Finding:** These floors were never fitted, optimized, or validated against Premier League match outcome probabilities. They are **officially removed from the scientific modeling pipeline**.

---

## 2. Normalization Benchmark Tournament (Fitted on Development 2022–24)

| Scheme Code | Normalization Strategy Description | Validation Log-Loss | Holdout Log-Loss | Holdout Accuracy (%) | Scientific Verdict |
|---|---|---|---|---|---|
| **NF0** | Heuristic Positional Floors ($45/55/57$) | 0.99572 | 1.03729 | 48.42% | Inferior Heuristic (REJECTED) |
| **NF1** | Raw Linear Attributes (No Floors) | 0.99567 | 1.03720 | 48.42% | Uncalibrated Scale |
| **NF2** | **Position-Specific Z-Score ($z = \frac{x - \mu_{\text{pos}}}{\sigma_{\text{pos}}}$)** | **0.99467 (Best)** | **1.03019 (Best)** | **48.42%** | **WINNER (OFFICIALLY ADOPTED)** |
| **NF3** | Position-Specific Empirical Percentiles | 0.99580 | 1.03740 | 48.16% | Non-linear Distortion |
| **NF4** | Position-Specific Robust Scaling (Median / IQR) | 0.99510 | 1.03210 | 48.16% | Solid Alternative |
| **NF5** | Monotonic Logistic Transform ($\sigma(z)$) | 0.99505 | 1.03180 | 48.16% | Solid Alternative |

---

## 3. Position-Specific Distribution Parameters (Development Baseline)

| Position Group | Key Attribute Evaluated | Mean ($\mu$) | Median | Std Dev ($\sigma$) | 25th Pct | 75th Pct | Normalization Used |
|---|---|---|---|---|---|---|---|
| **Forwards (ST/FW)** | Shooting / Finishing (SHO) | **76.4** | 76.0 | 6.8 | 72.0 | 81.0 | $z_{\text{SHO}} = \frac{\text{SHO} - 76.4}{6.8}$ |
| **Midfielders (AM/CM/DM)**| Passing / Vision (PAS) | **77.8** | 78.0 | 5.4 | 74.0 | 82.0 | $z_{\text{PAS}} = \frac{\text{PAS} - 77.8}{5.4}$ |
| **Defenders (CB/FB)** | Defending / Tackling (DEF) | **78.2** | 79.0 | 5.9 | 74.0 | 83.0 | $z_{\text{DEF}} = \frac{\text{DEF} - 78.2}{5.9}$ |
| **Goalkeepers (GK)** | Goalkeeper Reflexes (GK\_Ref) | **81.5** | 82.0 | 4.8 | 78.0 | 85.0 | $z_{\text{GK}} = \frac{\text{GK} - 81.5}{4.8}$ |

