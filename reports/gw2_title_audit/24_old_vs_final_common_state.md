# OLD VS FINAL MODEL COMMON-STATE COMPARISON

- **Old Production Model (V2 / V5.1):** Man City 54.40%, Arsenal 34.20%, Liverpool 1.90%
- **Final Model (`ENNOVERA_PL_FINAL_RESEARCH_V1`):** Man City 45.00%, Arsenal 37.50%, Liverpool 15.53%
- **Attribution of Differences:**
  1. Liverpool was severely under-represented in the old static model (1.90% -> 15.53%, +13.63 pp) due to lack of dynamic attack priors and replacement quality.
  2. Man City's artificial inflation was corrected (54.40% -> 45.00%, -9.40 pp) via Dirichlet probability calibration and Dixon-Coles draw correlation.
