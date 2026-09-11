# API spend ledger (append-only; one line per batch; sum the ACTUAL COST lines, never trust a note)

Booked before this file: ~$101.60 (memory note 2026-09-11; $99.36 running total in the monitor log + $2.26 headline monitor... see RESULTS.md §10). Owner reports $83 of credit remaining at 2026-09-11 22:40 UTC. Session cap on NEW spend: $33 (ceiling 135 in the scripts).

| UTC time | agent | batch / command | ACTUAL COST | running total |
|---|---|---|---:|---:|
| 2026-09-11 22:40 | coordinator | (opening balance) | — | 101.60 |
| 2026-09-11 22:44 | Worker C | Haiku 4.5 output-length calibration, 24 problems x 3 prompts, non-batch (full price) — sized the $12 cap before committing 4,332 batch requests | 0.47 | 102.07 |
| 2026-09-11 22:51 | Worker C | Haiku 4.5 honest class, 1,444 requests, batch (gen_honest_haiku.py) | 4.13 | 106.20 |
| 2026-09-11 22:51 | Worker C | Haiku 4.5 independent-arm attacks, 1,444 requests, batch (gen_backdoor_api.py --model claude-haiku-4-5 --independent) | 4.78 | 110.98 |
| 2026-09-11 22:46 | Worker B | Haiku 4.5 monitor, same-generator HEADLINE pairs (623), 1,246 requests, batch (`monitor_samegen.py --model claude-haiku-4-5`) | 1.93 | 112.91 |
| 2026-09-11 22:46 | Worker B | Haiku 4.5 monitor, same-generator STRICT pairs (99), 198 requests, batch | 0.29 | 113.20 |
| 2026-09-11 22:46 | Worker B | Sonnet 5 monitor, STORED pairs on the headline problems (623), 1,246 requests, batch (`monitor_samegen.py --stored`) | 2.39 | 115.59 |
| 2026-09-11 22:46 | Worker B | Sonnet 5 monitor, STORED pairs on the strict problems (99), 198 requests, batch | 0.36 | 115.95 |
| 2026-09-11 22:46 | Worker B | Haiku 4.5 monitor, STORED pairs on the headline problems (623), 1,246 requests, batch | 1.82 | 117.77 |
| 2026-09-11 22:46 | Worker B | Haiku 4.5 monitor, STORED pairs on the strict problems (99), 198 requests, batch | 0.28 | 118.05 |
| 2026-09-11 22:54 | Worker B | Haiku 4.5 truncation control, same-generator strict, `--max-tokens 1024`, 198 requests, batch | 0.33 | 118.38 |
| 2026-09-11 22:54 | Worker B | Haiku 4.5 truncation control, STORED strict, `--max-tokens 1024`, 198 requests, batch | 0.31 | 118.69 |

**Worker B total: $7.71** over eight batches (own cap $10; every batch `--dry-run` first, every
`--spent` the running total at submission). The six main batches were submitted together at
22:40 UTC and all ended by 22:47; the two controls at 22:50. They ran **concurrently with Worker
C's Haiku generation batches above** and were quoted `--spent 101.60`, the balance before either
worker started — so the projected totals printed inside the eight logs understate the true
running total by Worker C's $9.38. The running-total column here is the file-order sum and is the
one to trust. Ceiling $135 was never approached; largest single batch $2.39.
| 2026-09-11 23:06 | Worker C | Haiku 4.5 prompt-matched honest class, 611 requests (the Gate S problem set), batch (gen_honest_haiku.py --matched --problem-ids) | 1.82 | 112.80 |
| 2026-09-11 23:12 | Worker A | Sonnet 5 prompt-matched honest class (arm 3, RESULTS.md §13), 1,112 requests, batch (`gen_honest_api.py --matched`), est. $3.84, cap $12, 12.0 min, 0 errored | 4.48 | 124.99 |

**Worker A total: $4.48** over one batch (`--dry-run` first: 1,112 problems, estimate $3.84, worst
case $23.27 at `max_tokens`; hard cap $12 enforced in the script by the new `--max-cost`). The
running total in my row is the **file-order sum of every ACTUAL COST above it** (101.60 opening +
$18.91 of this session's other batches), which is the column the header says to trust; the
immediately preceding row's own running-total cell (112.80) was computed against a balance that
predates four of the rows above it, so it is not the file-order sum. New spend this session
including mine: **$23.39** against the $33 session cap.
