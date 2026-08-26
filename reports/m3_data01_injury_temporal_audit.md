# ENNOVERA PL — M3-DATA-01 Injury & Availability Temporal Audit Report

**Audit Focus:** Verification of Historical FPL Injury Status, News Timestamps, Rolling Availability Snapshots, and Point-in-Time Integrity.

---

## 1. Availability Field Provenance & Integrity

| FPL Field Name | Description | 2022–24 Historical Status | 2024–26 Historical Status | Point-in-Time Safe? | Scientific Handling Protocol |
|---|---|---|---|---|---|
| `status` | Availability code (`a`=available, `i`=injured, `s`=suspended, `d`=doubtful) | End-of-season final snapshot in raw dumps | Rolling weekly snapshots available | **CONDITIONAL** | Use rolling weekly snapshots only |
| `chance_of_playing_this_round` | Official probability of playing (0%, 25%, 50%, 75%, 100%) | End-of-season in raw dumps | Rolling weekly snapshots available | **CONDITIONAL** | Mapped to $P(\text{start})$ prior |
| `news` | Textual description of injury/suspension reason | Preserved with timestamp | Preserved with timestamp | **YES** | Filtered by `news_added < kickoff` |
| `news_added` | ISO timestamp of injury report publication | **Strictly Timestamped** | **Strictly Timestamped** | **YES** | Used to enforce temporal boundary |

---

## 2. Temporal Assertion Protocol: $\text{SnapshotTime} < \text{KickoffTime}$

- For all matches where rolling injury snapshots exist, the system enforces:
  $$\text{news\_added} < \text{kickoff\_time}$$
- Any injury news logged after kickoff is strictly ignored for pre-match feature construction.
- When rolling point-in-time injury snapshots are missing (older historical archives), the model falls back safely to empirical $P(\text{start})$ derived from preceding rolling match minutes.

