# GW1 SOURCE-OF-TRUTH & DATA-LINEAGE AUDIT SCOPE

- **Program:** `ENNOVERA_PL_GW1_SOURCE_OF_TRUTH_AND_STATE_RECOVERY_V1`
- **Severity:** `CRITICAL DATA-INTEGRITY INCIDENT`
- **Root Cause Summary:** Earlier forensic scripts consumed a synthetic, contaminated match-results dictionary where Liverpool was falsely recorded as winning 2-1 at Newcastle, Man City as winning 3-0, and Arsenal as winning 2-0.
- **Incident Scope:** Re-authenticate all 10 fixtures from official Premier League match logs, rebuild the clean table, execute clean 10,000 Monte Carlo simulations, and establish permanent ingestion validation gates.
