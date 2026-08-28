# THRESHOLD RECALL & METRIC CONTAMINATION ROOT CAUSE

1. **Finding:** In the previous V2 report, the single-gameweek GW1 table reported $15+\text{ Recall@20} = 55.8\%$ and $20+\text{ Recall@20} = 50.1\%$.
2. **Forensic Discrepancy:** In real-world GW1, the highest score across the entire league was Bukayo Saka with 12 points. Zero players scored $\ge 15$ or $\ge 20$ points in GW1.
3. **Classification:** `REPORT_METRIC_CONTAMINATION`.
4. **Mechanism:** The report generator accidentally imported the **4-season historical C9 bridge metrics** ($15+\text{ Recall} = 55.8\%, 20+\text{ Recall} = 50.1\%$) into the single-gameweek GW1 section.
5. **Correction:** Correctly recalculated GW1 metrics: $10+\text{ Recall@20} = 100.0\%$ (4 / 4 players scoring $\ge 10$), while $15+$ and $20+$ recalls are correctly reported as **`N/A — NO PLAYERS MET THRESHOLD`**.
