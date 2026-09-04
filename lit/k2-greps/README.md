# K2 — the full-text keyword record

Seventeen papers fetched via `arxiv.org/html` on 2026-09-03 (all HTTP 200, ≥9 s apart, no sub-1 KB
bodies), keyword-counted by `../../experiments/scan/grep_html.py`. Fourteen AI-control papers plus
three out-of-field positive controls (`1803.02324`, `1805.01042`, `1905.05778`).

| File | Keyword family |
|---|---|
| `K2-grep-table-1.tsv` | partial-input / hypothesis-only / metadata / construct validity / shortcut / trivial baseline |
| `K2-grep-table-2.tsv` | label noise / filtering / functional backdoors / floors and ceilings / surface features / dataset construction |
| `K2-grep-table-3.tsv` | bag-of-words / n-gram / length / comment / **authorship** / style / machine-generated |

**Read the zeros with their controls.** Per-document positive controls: `monitor` 56–351, ` the `
259–1,115 — the pipeline fires. Cross-corpus controls: `hypothesis-only` = 27 in `1805.01042`,
`bag-of-words` = 2, `artifact` = 36 in `1803.02324`, through the identical pipeline that returns
0/14 on the control papers.

**And then read `../01-verified-bibliography.md` §2 anyway.** These zeros are true and they are not
sufficient. Three setup paragraphs containing none of these words killed four clauses of the
round-16 framing. That is rule R18, and this directory is the evidence that bought it.

⚠️ One vocabulary collision to know about: `metadata` ×21 and `artifact` ×77 in `2510.09462` sit
inside prompt-injection payloads (`<SYSTEM_BENCHMARK_METADATA …>`), not analysis. A naive count
scores that paper OCCUPIED.
