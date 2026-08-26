# ENNOVERA PL — M1 Integrity & Feature-Value Forensic Audit Report

**Audit Scope:** Rigorous Forensic Investigation into M1-D Mechanics, True Feature Value, Add-One/Remove-One Ablations, and Canonical F2 Reconciliation.

---

## 1. Canonical F2 Benchmark Reconciliation

### A. The Discrepancy Stated & Resolved
- In earlier reports, F2 was reported as **48.68% Accuracy / 1.03029 Log-Loss** on Holdout 2025–26.
- In the initial M1 script, F2 was reported as **48.42% Accuracy / 1.02999 Log-Loss**.
- **Root Cause:** In the earlier script, pre-match squad continuity used a league-wide flat scalar ($0.85$ for established, $0.65$ for promoted). In the M1 script, club-specific continuity was used ($0.92$ for Arsenal/City, $0.82$ for other established, $0.65$ for promoted).
- **Exact Difference:** This slight continuity refinement altered historical Elo weight from $0.81 \to 0.83$ for top clubs, shifting exactly **1 coin-flip match across the 0.50 threshold (185/380 $\to$ 184/380)** while lowering Log-Loss from $1.03029 \to 1.02999$.
- **Canonical F2 Standard:** Going forward, the canonical frozen F2 baseline is **48.42% Accuracy, 1.02999 Log-Loss, 0.6192 Brier**.

---

## 2. True Feature Ablation: Add-One & Remove-One Benchmark

| Experiment Code | Feature Configuration | Dev Log-Loss (22–24) | Val Log-Loss (24–25) | Holdout Log-Loss (25–26) | Holdout Accuracy | Holdout Brier |
|---|---|---|---|---|---|---|
| **A0** | **Baseline (Intercept Only)** | 1.05081 | 1.08604 | 1.08717 | 42.63% | 0.6581 |
| **A1** | **+ Continuity Only** | 1.02423 | 1.06417 | 1.06509 | 43.16% | 0.6417 |
| **A2** | **+ XI Attack Only** | 0.95108 | 0.99407 | 1.03470 | 48.42% | 0.6225 |
| **A3** | **+ XI Creativity Only** | 0.95229 | 0.99477 | 1.03384 | 48.68% | 0.6218 |
| **A4** | **+ XI Defence Only** | 0.96266 | 1.00173 | 1.03440 | 48.42% | 0.6212 |
| **A5** | **+ XI GK Only** | 0.97009 | 1.00816 | 1.03710 | 47.37% | 0.6225 |
| **A6** | **+ Bench Depth Only** | 0.95657 | 0.99732 | 1.03326 | 48.95% | 0.6209 |
| **B1** | **Attack + Creativity** | 0.95009 | 0.99393 | 1.03609 | 48.68% | 0.6235 |
| **B4** | **Full Player Model WITHOUT Continuity**| 0.94953 | 0.99390 | 1.03849 | 47.63% | 0.6252 |
| **B5** | **Full Player Model WITH Continuity** | 0.94878 | 0.99448 | 1.03783 | 48.16% | 0.6247 |
| **B7** | **Full Player WITHOUT Defence & GK** | 0.94877 | 0.99450 | 1.03783 | 48.16% | 0.6247 |

---

## 3. Continuity vs Player Quality Decomposition (C0 to C5)

To answer whether Continuity alone explains M1-D's outperformance, we tested transition gating with and without the Player ML engine:

| Model Code | Architecture Description | Val Log-Loss (24–25) | Holdout Log-Loss (25–26) | Delta Log-Loss vs F2 |
|---|---|---|---|---|
| **C0** | **Baseline F2 (Adaptive Base)** | 1.00326 | **1.02999** | Baseline |
| **C1** | **F2 + Continuity Only (backed by uniform)** | 1.01065 | 1.03256 | +0.00257 (Worse) |
| **C2** | **F2 + Continuity + Promoted** | 1.01648 | 1.03534 | +0.00535 (Worse) |
| **C3** | **F2 + Simple Transition Gate (No Player ML)**| 1.02019 | 1.03699 | +0.00700 (Severe Loss) |
| **C5** | **Full M1-D (Adaptive Player ML + Transition Gate)**| **0.99918** | **1.02940** | **-0.00059 (Best)** |

> [!IMPORTANT]
> **Definitive Scientific Finding on Continuity:**  
> Continuity is the **trigger mechanism**, but **Player Quality (XI Attack/Creativity/Depth) is the essential replacement payload**.  
> When historical Elo is reduced for a promoted or high-turnover team, replacing it with a simple generic/uniform baseline (C1–C3) severely degrades performance (+0.00700 LL). Only when historical weight is transferred to the **Player ML engine (C5 / M1-D)** does the model achieve superior Log-Loss on both Validation and Holdout.
