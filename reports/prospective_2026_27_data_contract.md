# ENNOVERA 2026-27 POINT-IN-TIME DATA CONTRACT

- **Premier League:** Predictions strictly frozen at $T - 60	ext{ minutes}$ prior to official kickoff. Actual starting lineups released post-cutoff are forbidden.
- **FPL:** Decisions strictly frozen prior to official FPL deadline.
- **Verification:** Automated assertion $\max(	ext{feature.available\_at}) < 	ext{freeze\_time}$ enforced on every snapshot.
