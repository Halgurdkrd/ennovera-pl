# ENNOVERA PHASE 5.3 — MODEL-ONLY PREDICTIVE COMPARISON

```csv
model,mae,rmse,spearman,ndcg20,recall_10_plus,recall_15_plus
FPL-03,2.142,2.854,0.284,0.662,0.321,0.345
Phase 4,1.9903,2.682,0.3115,0.7015,0.358,0.382
Phase 5,1.968,2.641,0.324,0.718,0.384,0.415

```

## Scientific Findings
- **Player MAE:** Phase 5 (1.9680) strictly outperforms Phase 4 (1.9903) and FPL-03 (2.1420).
- **Spearman Rank Correlation:** Phase 5 (0.3240) dominates FPL-03 (0.2840) by +14.1%.
- **15+ Haul Recall@20:** Phase 5 captures **41.5%** of double-digit haulers vs FPL-03 **34.5%**.
