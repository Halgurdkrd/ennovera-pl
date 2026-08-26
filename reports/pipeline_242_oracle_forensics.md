# ENNOVERA PL — M3-VERIFY-02 Forensic Deconstruction of the 242/380 Oracle Metric

**Audit Focus:** Full Forensic Deconstruction of the Previously Reported "242 / 380 = 63.68% Oracle" Metric.

---

## 1. The Origin & Provenance of the 242/380 Metric

| Parameter | The True 5-Expert Argmax Oracle | The Reported "242/380" Combinatorial Metric |
|---|---|---|
| **Underlying Model Pool** | Exactly the 5 Frozen Base Experts (F2, PQ7, Avail, T7, D7) | **Over 35 experimental sub-variants, candidate versions, and synthetic parameter sweeps** |
| **Model Selection Mechanism**| Single argmax call from 5 frozen models | **Post-hoc retrospective union across all historical test arrays** |
| **Valid Oracle Ceiling for 5 Base Experts?** | **YES (197 / 380 = 51.84%)** | **NO (Scientifically Invalid Terminology)** |
| **Achievable by Pre-Match Gating Router?** | **YES (Near ceiling: 189 / 197 = 95.9%)** | **NO (Requires sweeping dozens of non-existent model variants post-kickoff)** |

---

## 2. Definitive Forensic Verdict

# **WAS CALLING 242/380 A "5-EXPERT ORACLE" SCIENTIFICALLY INCORRECT?**
# **YES, UNEQUIVOCALLY.**

### Scientific Explanation:
1. The metric **242 / 380** was computed by aggregating the union of correct predictions across *dozens of intermediate research experiments* (including unregularized trees, parameter grid searches, and synthetic post-hoc blends).
2. It was mistakenly labeled as a "5-Expert Oracle", creating the false impression that 53 easy routing opportunities existed among the 5 frozen base experts.
3. In reality, the 5 frozen base experts produce an argmax union of **197 / 380 (51.84%)**, of which our deployed router **R7** already captures **189 / 380 (49.74%)**.
- Full fixture-by-fixture provenance ledger preserved at [`data/experiments/pipeline_integrity/m3_oracle_242_provenance.csv`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/data/experiments/pipeline_integrity/m3_oracle_242_provenance.csv).

