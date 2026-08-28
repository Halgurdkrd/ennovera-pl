# PERMANENT SOURCE-OF-TRUTH INGESTION GATE

```
[Incoming Match Result]
  │
  ├── CHECK 1: Fixture ID in Official Schedule
  ├── CHECK 2: Home/Away IDs match official calendar
  ├── CHECK 3: Primary Source (FPL Official Feed) confirms final score
  ├── CHECK 4: Secondary Source (Opta / Official Match Log) confirms final score
  ├── CHECK 5: Status == 'FINISHED'
  ├── CHECK 6: Table arithmetic invariants pass (Sum W == Sum L, Sum GF == Sum GA)
  └── CHECK 7: Immutable Manifest & SHA256 Fingerprint generated
```
