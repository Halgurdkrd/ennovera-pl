# ENNOVERA CURRENT-SEASON STATE UPDATE AUDIT

| Module | Input Variable | Current-Season Source | Source Type | Available At | Frozen Fallback? | Prospective Valid? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DynamicTeamState** | Scoreline (Home/Away Goals) | Completed Official Fixtures | `INTERNAL_DATABASE` | Post-Match | Decoupled Bayesian Prior | `EXACT_PARITY` |
| **Attack Intelligence** | Team Goals & Form | Official Match Outcomes | `INTERNAL_DATABASE` | Post-Match | Historical Prior | `EXACT_PARITY` |
| **Defensive / DefCon** | Role Resistance State | Official Minutes & Cards | `INTERNAL_DATABASE` | Post-Match | Role Resistance Prior | `VALID_FROZEN_FALLBACK` |
| **Expected XI** | Starter Frequency | Shared Football Core | `INTERNAL_FROZEN_MODEL` | T-60 | Starter Prior | `EXACT_PARITY` |
| **Fatigue / Congestion** | Days Rest / Workload | Official Calendar DB | `INTERNAL_FROZEN_REGISTRY` | Pre-Match | Rest Decay Prior | `EXACT_PARITY` |
| **Tactical Matchups** | Style Vectors | Event Aggregator | `INTERNAL_DERIVED_TRACKER` | Pre-Match | Style Matrix | `VALID_FROZEN_FALLBACK` |
| **Set Pieces** | Takers & Penalties | Role Tracker | `INTERNAL_DERIVED_TRACKER` | Pre-Match | Hierarchy Prior | `EXACT_PARITY` |
| **European Workload** | UEFA Fixtures | UEFA Registry DB | `INTERNAL_FROZEN_REGISTRY` | Pre-Match | Calendar Prior | `EXACT_PARITY` |
| **Joint Score State** | Poisson Parameters | Dixon-Coles Model | `OFFLINE_HISTORICAL` | Pre-Match | Dixon-Coles Prior | `VALID_FROZEN_FALLBACK` |
| **FPL Expected Minutes** | Starts & Baseline Mins | Official FPL Ingestion | `INTERNAL_DATABASE` | Post-Match | Appearance Model | `EXACT_PARITY` |
