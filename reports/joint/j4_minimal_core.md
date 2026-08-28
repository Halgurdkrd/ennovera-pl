# J4: MINIMAL INTELLIGENCE CORE DISCOVERY

## Candidate Architecture: `ENNOVERA_MINIMAL_FOOTBALL_CORE_V1`

### PL Minimal Core Comparison:
- **Full Certified Model:** Accuracy 58.4% | RPS 0.1748 | Log Loss 0.8680 | Active Parameters: 88
- **Minimal Core Architecture:** Accuracy 58.2% | RPS 0.1754 | Log Loss 0.8698 | Active Parameters: 42
- **Performance Retention:** **99.6% of RPS efficiency retained** with a **52.3% reduction in model parameters**.

### FPL Minimal Core Comparison:
- **Full Certified Model:** 2,179.50 pts/season | Active Parameters: 74
- **Minimal Core Architecture:** 2,177.00 pts/season (-2.50 pts/season) | Active Parameters: 36
- **Performance Retention:** **99.9% of manager performance retained** with a **51.4% reduction in parameter complexity**.

### Pruned Low-Utility Modules:
1. Micro-tactical directness clusters (High complexity / Low incremental gain)
2. Standalone penalty generation model (High noise / Low frequency)
3. Separate finishing streak adjustments (Overfitting risk)
4. Minor manager-regime scalar adjustments (Limited sample size)
