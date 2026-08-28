# J1: PL -> FPL BRIDGE VALIDATION

- **Control Baseline:** `ENNOVERA_FPL_FINAL_RESEARCH_V1` (2,179.50 pts/season mean).
- **Tested Bridges:** Calibrated Team xG, Clean-Sheet Distribution, Joint Score Distribution, Tactical States.
- **Key Findings:**
  1. PL Joint Score Distribution (`J1-C`) provides the cleanest incremental lift (+2.6 pts/season) by resolving goal ceiling interactions and clean-sheet probabilities simultaneously.
  2. Tactical matchup vectors (`J1-D`) are largely redundant (+0.3 pts/season) once team strength and expected minutes are accounted for.
  3. Best challenger (`J1-E`): **2,183.00 pts/season** (+3.5 pts/season over frozen control).
  4. 95% Bootstrap CI: `[-47.08, 53.74]`.
  5. Paired bootstrap preference: **56.0% of paired bootstrap resamples favored challenger**.
- **Decision:** **PROMOTE_TO_RESEARCH_CANDIDATE_ONLY** (Frozen control remains unchanged).
