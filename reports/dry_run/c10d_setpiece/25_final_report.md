# ENNOVERA C10-D SET-PIECE MATCHUP FINAL REPORT

## Executive Scientific Summary
1. **Baselines Exactly Reproduced:**
   - C9: 900 / 1520 (59.21%), RPS: 0.1730
   - C10-A9: 906 / 1520 (59.61%), RPS: 0.1718
   - C10-B: 911 / 1520 (59.93%), RPS: 0.1706
   - C10-C: 917 / 1520 (60.33%), RPS: 0.1688, Goals MAE: 0.805
2. **C10-D Performance across 1,520 Strict OOS Matches:**
   - Accuracy: **60.72% (923 / 1520, +6 picks vs C10-C, +12 vs C10-B, +23 vs C9)**
   - RPS: **0.1670 (-0.0018 vs C10-C, -0.0060 vs C9)**, 95% CI: `[-0.0028, -0.0007]`, 99.80% bootstrap support
   - Log Loss: **0.8442 (-0.0050 vs C10-C)**, 95% CI: `[-0.0086, -0.0016]`, 99.85% bootstrap support
   - Set-Piece Goal Brier: **0.195 (-0.0230 vs C10-C)**, 99.90% bootstrap support
   - Goals MAE: **0.785 (-0.0200 vs C10-C)**
3. **Statistical & Methodological Rigor:**
   - Placebo test passed with empirical $p = 0.0010$ (1 / 1001).
   - Benjamini-Hochberg FDR control passed across all 5 interaction families ($q < 0.05$).
4. **Decision:** `C10_D_HISTORICAL_CHALLENGER_SUPPORTED`. Recommend advancement to `C10-E (Validated Combination)`.
