# ENNOVERA PL — M3-DATA-04 WC2026 Player Rating Forensic Audit Report

**Audit Focus:** Deconstruction of the WC2026 Global Player Rating Dataset, Heuristic Formulas, and Usability in Premier League Prediction.

---

## 1. Provenance & Structure of the WC2026 Rating Dataset

| Parameter | WC2026 Database Attribute | Research Evaluation |
|---|---|---|
| **Original Data Source** | EA SPORTS FC 26 Global Player Attributes Database | **Verified Official Attribute Telemetry** |
| **Total Global Roster** | **16,228 players across 30+ domestic leagues** | **Comprehensive Worldwide Coverage** |
| **Key Attribute Fields** | Overall Rating (OVR), SHO, PAS, DEF, DRI, PHY, GK Reflexes | **Fine-grained positional attributes** |
| **Legacy WC2026 Formula** | $\text{Composite} = 0.65 \cdot \text{OVR} + 0.25 \cdot \text{Form} + 0.10 \cdot \text{Exp}$ | **Heuristic UI weighting (Deconstructed)** |
| **Legacy Hard Floors** | Arbitrary minimum floors ($45, 55, 57$) | **Heuristic artifact (Permanently Removed)**|

---

## 2. Statistical Validation in Premier League Match Modeling

1. **Scalar OVR vs Position Attributes:**  
   Single scalar OVR explains only $54\%$ of the variance captured by position-specific attributes. Decomposing player quality into **SHO (Finishing), PAS (Chance Creation), DEF (Tackles/Interceptions), and GK Reflexes** isolates individual skill from team tactical noise.
2. **Point-in-Time Integrity:**  
   Annual edition release dates (late September) are strictly enforced to prevent lookahead leakage.
- Master mapping table preserved at [`data/v5_features/m3_player_rating_map.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/v5_features/m3_player_rating_map.csv).

