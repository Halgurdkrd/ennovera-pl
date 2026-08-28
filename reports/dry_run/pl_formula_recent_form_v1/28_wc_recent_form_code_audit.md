# WC 2026 RECENT FORM CODE AUDIT

- **Source:** `innovera-wc2026-backend/scripts/build_qualification_features.py` (lines 250–313).
- **Core Formula:** `qual_recent_form_points` computed from last 3 matches + momentum trend (`late_win_rate - early_win_rate`).
- **Adaptation for PL:** Extended to 10-match opponent-adjusted xG residual window (`RF10`).
