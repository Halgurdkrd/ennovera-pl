# Historical FPL Data Audit — for V3 Validation

**Headline: the V3 blocker is PARTIALLY LIFTED.** Historical FPL data exists for **2022-23 →
2025-26 (4 seasons, 1,520 matches)** with real **team strength AND per-GW xG/xA**. This makes
**Layer 2 (strength) and Layer 3 (xG form) genuinely backtestable** on 2 real test seasons.
**Only Layer 4 (injury/availability) remains un-backtestable** — that data was never recorded
historically.

## 1. Seasons available (targeted download; full clone skipped — too large)
`players_raw.csv`, `teams.csv`, `fixtures.csv`, `gws/merged_gw.csv` for **2022-23, 2023-24,
2024-25, 2025-26** (~5 MB merged_gw each). Older seasons (2016-2022): **no FPL data** here.

| Season | Players | Teams | GWs | xG? | xA? | price? |
|---|---|---|---|---|---|---|
| 2022-23 | 778 | 20 | 37 | ✅ | ✅ | ✅ |
| 2023-24 | 865 | 20 | 38 | ✅ | ✅ | ✅ |
| 2024-25 | 804 | 20 | 38 | ✅ | ✅ | ✅ |
| 2025-26 | 841 | 20 | 38 | ✅ | ✅ | ✅ |

## 2. Critical columns in `merged_gw.csv` (all 4 seasons)
| Column | 2022-26 | | Column | 2022-26 |
|---|---|---|---|---|
| expected_goals | ✅ | | clean_sheets | ✅ |
| expected_assists | ✅ | | ict_index | ✅ |
| value (price) | ✅ | | transfers_in / out | ✅ |
| minutes | ✅ | | **chance_of_playing_this_round** | **❌** |
| team | ✅ | | **chance_of_playing_next_round** | **❌** |
| GW / round | ✅ | | **status** (avail/injured) | **❌** |
| was_home | ✅ | | total_points | ✅ |

**The three availability columns are absent from *every* historical season.** `merged_gw` records
what *happened* (minutes played), never the *pre-match* injury/doubt status — that's only in the
live snapshot. So Layer 4's true pre-match availability signal **cannot be reconstructed** (only a
post-hoc "who played" proxy, which is itself a leak if used as a pre-match feature).

## 3. Team strength history (Layer 2) — ✅ AVAILABLE and it *moves*
`teams.csv` carries real per-season `strength_attack/defence_home/away` (non-zero for all 20
teams every season) — and the values track reality:

| Season | Man City atk (h/a) | Arsenal atk (h/a) |
|---|---|---|
| 2022-23 | 1340 / 1340 | 1250 / 1250 |
| 2023-24 | 1350 / 1360 | 1370 / 1370 |
| **2024-25** | **1160 / 1170** | **1390 / 1400** |
| 2025-26 | 1220 / 1310 | 1340 / 1390 |

**FPL genuinely downgraded City's attack in 2024-25 (1340→1160)** and rated Arsenal above them —
exactly the "did City change?" signal Layer 2 was designed to catch. This is contemporaneous,
leak-free, per-season → **Layer 2 is now validatable.** (Note: this is very different from the
*current pre-season snapshot*, where these fields are 0 — that's why the live V3 overlay had
nothing to work with.)

## 4. Per-GW team features (Layer 3) — ✅ computable
From `merged_gw` we can build per-team, per-gameweek `team_xG`, `team_xA`, `squad_value`, and
dependency. Sample (2024-25 GW1): Arsenal xG 1.3 / xA 0.9 / £116M / dep 0.36; Nott'm Forest xG
1.4 / dep 0.51. Rolling 5-GW xG form is therefore **real, not a goals proxy**, for 2022-23+.

## 5. Player availability history (Layer 4) — ❌ NOT available
No `status` / `chance_of_playing` historically (see §2). Only `minutes > 0` (post-match) exists —
a retrospective proxy, unusable as a leak-free pre-match feature. **Layer 4 stays un-validatable.**

## 6. Backtestable matches
| Seasons | Matches | FPL team data | FPL player xG | Usable |
|---|---|---|---|---|
| 2016-17 → 2021-22 | 2,280 | ❌ | ❌ | ❌ (pre-FPL-xG) |
| 2022-23 → 2025-26 | **1,520** | ✅ | ✅ | ✅ |

**1,520 xG-backtestable matches.** For the V3 4-way split, that's **train 2022-23 (380) → cal
2023-24 → validate 2024-25 → holdout 2025-26**. The regular-Elo base still trains on all 3,800;
**FPL-augmented models, if they *train* on FPL features, get only 380 training matches** (overfit
risk). As *heuristic overlays* validated on the 2 test seasons (760 matches), the data is enough.

## 7. Data quality
- **xG missing: 0.0%** (2022-23), full 37-38 GW coverage per season.
- Team names **join cleanly** to `pl_features` (20/20 match after `canonicalize()`, zero
  mismatches) — no name-mapping work needed.
- The only quality gap is the structural one: **no availability/status columns** (§2, §5).

## 8. RECOMMENDATION — can we properly validate V3?
**Partially — and it's a real step forward:**
- ✅ **Layer 2 (FPL strength)** and ✅ **Layer 3 (real xG/xA form)** can now be validated on
  **2024-25 + 2025-26** with contemporaneous, leak-free data. This is the concrete unlock the V3
  report called for — we can finally test whether these layers beat V2 on the holdout.
- ❌ **Layer 4 (availability/dependency-under-injury)** cannot — the historical injury data does
  not exist. It stays a live-season-only, unvalidated overlay.
- ⚠️ **Caveat:** only 4 FPL seasons. Keep the layers as *lightweight corrections* (few
  coefficients, tuned on 2022-23+validation, tested on holdout) rather than retraining big models
  on 380 FPL-labelled matches — otherwise overfit is likely.

**Next step (separate task, model changes):** re-run the V3 layer tests using this **historical**
FPL strength + xG (not the pre-season snapshot) for 2024-25/2025-26, and see whether Layer 2 and
Layer 3 finally clear V2 on the holdout. If they do, V3 becomes real; if not, V2 stands.

### Files
Downloaded to `data/raw/fpl_full/data/{season}/` (gitignored — not committed). Audit script:
`scripts/audit_fpl_data.py`.
