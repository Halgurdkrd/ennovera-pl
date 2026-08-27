# ENNOVERA PHASE 5.0 — CODE LINEAGE AUDIT

- **FPL-03 Historical Training Pipeline:** Reads only `data/raw/fpl_full/data/[season]/gws/merged_gw.csv` (Premier League).
- **Live / Shadow xP Pipeline:** Ingests live Premier League bootstrap elements (`fpl_ingestor.py`).
- **Premier League Match Engine (CORE_BASE, V2, V5.1):** Consumes Premier League historical match results and Elo ratings.
- **Cross-Competition Status:** Completely uncoupled. No active model depends on or reads European/domestic cup data.
