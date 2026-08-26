# ENNOVERA PL + FPL — FPL-03 Historical Chip Rules Audit Report

**Research Scope:** Audit and Encoding of Historical Season-by-Season FPL Chip Regulations.

---

## 1. Season-by-Season Chip Inventory & Regulations

| Season | Chip Inventory Available | Half-Season Expiry Rules | Banked FT Limit | Special Historical Rules |
|---|---|---|---|---|
| **2022–23** | WC1, WC2, FH (1), BB (1), TC (1) | WC1 expires GW16; WC2 available GW17–38 | Max 2 Banked | Unlimited free transfers during World Cup 2022 (GW17) |
| **2023–24** | WC1, WC2, FH (1), BB (1), TC (1) | WC1 expires GW19; WC2 available GW20–38 | Max 2 Banked | Standard rules |
| **2024–25** | WC1, WC2, FH (1), BB (1), TC (1) | WC1 expires GW19; WC2 available GW20–38 | **Max 5 Banked** | Rule change: Accumulate up to 5 Free Transfers |
| **2025–26** | **8 Chips Total:** WC1/2, FH1/2, BB1/2, TC1/2 | **First Half (GW1–19) expires GW19; Second Half (GW20–38)** | **Max 5 Banked** | **8-Chip Autonomous Season Format** |

---

## 2. Definitive Verification Finding
All season-specific rules have been formalized in [`config/fpl_rules_by_season.json`](file:///f:/AI/fifi2026/innovera-wc2026-backend/ennovera-pl/config/fpl_rules_by_season.json), preventing retrospective application of 2025–26 rules to earlier seasons.

