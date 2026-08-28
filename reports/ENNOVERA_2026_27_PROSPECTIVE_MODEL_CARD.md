# ENNOVERA 2026-27 PROSPECTIVE SHADOW MODEL CARD

- **System Version:** `1.0.0-prospective-shadow`
- **FPL Candidate:** `ENNOVERA_FPL_FINAL_RESEARCH_V1` (2,179.50 pts/season mean)
- **PL Candidate:** `ENNOVERA_PL_FINAL_RESEARCH_V1` (58.4% Acc, 0.1748 RPS, 0.8680 Log Loss, 33.8% Draw Recall, 0.9% ECE)
- **Shared Core:** ExpectedXIEngine, PlayerAttackEngine, DefensiveActionEngine, SetPieceAerialEngine, CongestionFatigueEngine.
- **Production Status:** PRODUCTION UNCHANGED / RESEARCH SHADOW ONLY.

## 2026-27 Prospective Validation Governance Appendix (v2 Protocol)
- **PL Canonical Evaluation Horizon:** Official predictions must be frozen inside the $T-75	ext{m}$ to $T-60	ext{m}$ operational window (preferred target $T-70	ext{m}$). Predictions generated earlier are tagged as `EARLY_FORECAST` and evaluated in secondary research only.
- **FPL Canonical Evaluation Horizon:** Official pre-deadline decisions must be frozen between $T-90	ext{m}$ and $T-30	ext{m}$ before official deadline (preferred target $T-60	ext{m}$).
- **Timing Invariant:** `official_freeze_at <= snapshot_created_at`. Future freeze timestamps are prohibited.
