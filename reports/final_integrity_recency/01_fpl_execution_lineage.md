# FPL EXECUTION LINEAGE REPORT

## Root Cause of Prior Mismatch:
- In earlier reporting, the captain optimization score (`11.40` for De Cuyper, `10.80` for Hinshelwood) was colloquially described as 'expected points', causing apparent confusion with raw mean xP (`8.59` and `8.55`).
- **Resolution:** All downstream components now consume the exact same canonical `mean_xp`, with captain utilities explicitly separated and labeled as `CAPTAIN_UTILITY_SCORE`.
