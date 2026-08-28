# R1: J1 BOOTSTRAP STATISTICAL RECONCILIATION

## Root Cause of Apparent Inconsistency
The previously reported interval `[+1.85, +5.15]` was an analytical/normal approximation interval on aggregated season-level totals ($N=4$ seasons), while the `89.4%` preference rate was computed on gameweek-level resampling units ($N=152$ gameweeks).

## Recomputed Gameweek-Block Bootstrap Distribution (10,000 Resamples)
- **Resampling Unit:** Gameweek ($N=152$ gameweeks across 4 historical seasons)
- **Observed Season Delta:** **+3.50 pts/season**
- **Bootstrap Mean Delta:** **+3.47 pts/season**
- **Bootstrap Median (p50):** **+3.44 pts/season**
- **Bootstrap Standard Deviation:** 2.80 pts/season
- **Percentile 95% Bootstrap CI:** **`[-1.93, 8.98]`**
- **Proportion $\Delta > 0$:** **89.3% of paired bootstrap resamples favored challenger**
- **Proportion $\Delta \le 0$:** **10.7%**

## Final Scientific Phrasing & Classification
The J1 challenger achieves a **MODEST_POSITIVE / DIRECTIONAL_POSITIVE** improvement (+3.50 pts/season mean, +0.16% total points). Because the lower 2.5% tail crosses zero (`-1.93`), the result is directionally favorable but not statistically transformative. Frozen FPL control remains 100% preserved.
