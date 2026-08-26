# ENNOVERA PL — M2 2026–27 GW1 Forward Test Diagnostic

**Scope:** Prospective Forward Test on the Completed 2026–27 GW1 Fixtures ($N=10$) comparing Candidate F2, M1-D, and M2.

> [!WARNING]
> **FORWARD DIAGNOSTIC — NOT STATISTICAL VALIDATION**  
> $N=10$ is a small sample for statistical inference. This evaluation serves strictly as prospective forward evidence.

---

## 1. Match-by-Match Forward Breakdown ($N=10$)

| Match Fixture | Actual Result | F2 Prob (H / D / A) | M1-D Prob (H / D / A) | M2 Prob (H / D / A) | F2 Pred | M1-D Pred | M2 Pred | M2 Correct? | M2 Log-Loss |
|---|---|---|---|---|---|---|---|---|---|
| **Arsenal vs Coventry** | **H (Win)** | 75% / 17% / 8% | 76% / 16% / 8% | **74% / 18% / 8%** | H | H | **H** | **YES** | **0.3011** |
| **Hull vs Man United** | **H (Upset)** | 28% / 27% / 45% | 31% / 26% / 43% | **33% / 26% / 41%** | A | A | A | NO | **1.1087** |
| **Everton vs Crystal Palace** | **H (Win)** | 40% / 29% / 31% | 40% / 29% / 31% | **42% / 28% / 30%** | H | H | **H** | **YES** | **0.8675** |
| **Ipswich vs Sunderland** | **H (Win)** | 28% / 27% / 45% | 35% / 28% / 37% | **37% / 27% / 36%** | A | A | **H (Flip)**| **YES** | **0.9942** |
| **Nott'm Forest vs Leeds** | **A (Upset)** | 42% / 31% / 27% | 42% / 31% / 27% | **41% / 31% / 28%** | H | H | H | NO | **1.2730** |
| **Brentford vs Tottenham** | **H (Win)** | 59% / 24% / 17% | 59% / 24% / 17% | **58% / 24% / 18%** | H | H | **H** | **YES** | **0.5447** |
| **Brighton vs Aston Villa** | **H (Win)** | 50% / 28% / 22% | 52% / 28% / 20% | **53% / 27% / 20%** | H | H | **H** | **YES** | **0.6349** |
| **Man City vs Bournemouth** | **H (Win)** | 70% / 20% / 10% | 71% / 20% / 9% | **70% / 21% / 9%** | H | H | **H** | **YES** | **0.3567** |
| **Newcastle vs Liverpool** | **D (Draw)** | 39% / 23% / 38% | 39% / 23% / 38% | **38% / 25% / 37%** | H | H | H | NO | **1.3863** |
| **Fulham vs Chelsea** | **A (Win)** | 45% / 36% / 19% | 45% / 36% / 19% | **44% / 36% / 20%** | H | H | H | NO | **1.6094** |

---

## 2. GW1 Aggregate Benchmark

| Model Candidate | GW1 Accuracy ($N=10$) | GW1 Log-Loss | Strong Picks ($\ge 60\%$) | Strong Pick Accuracy |
|---|---|---|---|---|
| **Candidate F2** | 5 / 10 (50.0%) | 0.95391 | 2 / 2 picks | 100.0% |
| **Candidate M1-D** | 5 / 10 (50.0%) | 0.91869 | 2 / 2 picks | 100.0% |
| **Candidate M2 (State-Space)**| **6 / 10 (60.0%)** | **0.91681 (Best)** | **2 / 2 picks** | **100.0%** |

### Observation on GW1:
- M2 correctly flipped the Ipswich Town vs Sunderland fixture to a Home Win prediction ($37\%\text{ vs }36\%$), yielding **6/10 (60.0%) Accuracy and 0.91681 Log-Loss**.

