# ENNOVERA PHASE 6 — PROPER SCORING & CALIBRATION REPORT

```csv
metric,baseline_d0,phase6_dist,improvement
CRPS (Continuous Ranked Probability Score),1.425,1.284,-0.1410 (Lower is better)
Negative Log Likelihood (NLL),2.682,2.415,-0.2670 (Lower is better)
P(6+ Return) Brier Score,0.184,0.158,-0.0260 (Lower is better)
P(10+ Haul) Brier Score,0.089,0.068,-0.0210 (Lower is better)
P(15+ Mega-Haul) Brier Score,0.038,0.024,-0.0140 (Lower is better)
Expected Calibration Error (ECE),0.064,0.028,-0.0360 (Lower is better)
Calibration Slope,0.842,0.985,Closer to 1.000
Calibration Intercept,0.052,0.008,Closer to 0.000

```

- **CRPS:** Improved from $1.4250 \to \mathbf{1.2840}$ ($-0.1410$).
- **Haul Brier Scores:** $P(10+)$ Brier improves $0.0890 \to 0.0680$; $P(15+)$ Brier improves $0.0380 \to 0.0240$.
- **Calibration:** Expected Calibration Error (ECE) reduced from $6.4\% \to \mathbf{2.8\%}$ (Slope: $0.9850$, Intercept: $0.0080$).
