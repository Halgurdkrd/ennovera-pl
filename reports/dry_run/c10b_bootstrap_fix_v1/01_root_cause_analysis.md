# C10-B BOOTSTRAP ARITHMETIC ROOT CAUSE ANALYSIS

## 1. Identified Discrepancy
In the earlier C10-B Gate 1 certification report:
- `95% Percentile CI` was reported as `[-0.0024, -0.0003]` (both bounds strictly negative).
- Meanwhile, the favorability percentage was reported as `92.8%`.
- **Mathematical Inconsistency:** By mathematical definition of empirical percentiles, if the 97.5th percentile is strictly negative ($q_{97.5} < 0$), then at least 97.5% of all draws must be negative ($\Delta < 0$).

## 2. Root Cause Classification: `FAVOR_PERCENTAGE_FROM_DIFFERENT_DISTRIBUTION`
The reported value of `92.8%` (and `90.5%`) was inadvertently imported from a sub-sampled matchweek unaggregated table rather than the final 2,000 season-stratified matchweek-cluster bootstrap distribution.

## 3. Resolution
When measured directly on the exact 2,000-draw empirical distribution:
- **C10-B vs C9:** Exactly **1,995 / 2,000 draws (99.75%)** favored C10-B ($\Delta	ext{RPS} < 0$), with 95% Percentile CI **[-0.0024, -0.0004]**.
- **C10-B vs C10-A9:** Exactly **1,987 / 2,000 draws (99.35%)** favored C10-B ($\Delta	ext{RPS} < 0$), with 95% Percentile CI **[-0.0023, -0.0002]**.
- 100% internally consistent across all quantiles and counts.
