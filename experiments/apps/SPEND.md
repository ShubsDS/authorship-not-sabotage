# API spend ledger (append-only; one line per batch; sum the ACTUAL COST lines, never trust a note)

Booked before this file: ~$101.60 (memory note 2026-09-11; $99.36 running total in the monitor log + $2.26 headline monitor... see RESULTS.md §10). Owner reports $83 of credit remaining at 2026-09-11 22:40 UTC. Session cap on NEW spend: $33 (ceiling 135 in the scripts).

| UTC time | agent | batch / command | ACTUAL COST | running total |
|---|---|---|---:|---:|
| 2026-09-11 22:40 | coordinator | (opening balance) | — | 101.60 |
| 2026-09-11 22:44 | Worker C | Haiku 4.5 output-length calibration, 24 problems x 3 prompts, non-batch (full price) — sized the $12 cap before committing 4,332 batch requests | 0.47 | 102.07 |
