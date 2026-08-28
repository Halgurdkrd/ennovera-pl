# ENNOVERA SNAPSHOT LIFECYCLE SPECIFICATION

| Lifecycle Stage | Timing Horizon | Canonical Eligible | Immutable | Outcome Scored |
| :--- | :--- | :--- | :--- | :--- |
| `EARLY_FORECAST` | $> T-75	ext{m}$ (PL) / $> T-90	ext{m}$ (FPL) | **FALSE** | **YES** | Secondary Research Only |
| `FINAL_OFFICIAL` | $T-75	ext{m}$ to $T-60	ext{m}$ (PL) / $T-90	ext{m}$ to $T-30	ext{m}$ (FPL) | **TRUE** | **YES** | Headline Prospective Benchmark |
| `OUTCOME_PENDING` | Post-kickoff / Post-deadline | **TRUE** | **YES** | Awaiting Official Ingestion |
| `EVALUATED` | Post-match official outcome ingestion | **TRUE** | **YES** | Scored in Canonical Metrics |
| `INVALID` | Integrity / cutoff violation | **FALSE** | **YES** | Excluded from Evaluation |
| `MISSED_WINDOW` | Failed execution inside window | **TRUE (as missed)** | **YES** | Operational Reliability Penalty |
