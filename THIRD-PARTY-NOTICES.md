# Third-party notices

This repository redistributes one third-party file. Its licence and copyright notice travel
with it, as that licence requires.

---

## `experiments/apps/monitor-summary.json`

**Source:** `https://github.com/anik-jha/challenger-panels`, path `runs/x0/monitor-summary.json`
(repository pushed 2026-08-17; file fetched and verified against the upstream copy).
**Licence:** MIT.
**What it is:** 24 monitors' validation and test AUROC / pAUC on the 1,375-item split, used as the
comparison set for figure F3. Nothing in it is our measurement; the paper cites it as Jha's.

Upstream licence, reproduced in full as MIT requires:

```
MIT License

Copyright (c) 2026 Anik Jha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Not redistributed, but relied on

These are fetched at run time by scripts in `experiments/` and are **not** stored in this
repository. Their licences are recorded in `notes/05-permissibility.md`, including the two that
declare none.

| Artifact | Licence |
|---|---|
| `RoganInglis/apps-control-arena` | MIT |
| `anik-jha/challenger-panels` (`runs/scores/`, `runs/x2`) | MIT |
| `eugenekoran/apps-control-arena-high-quality` | ⚠️ none declared |
| `adityaasinha28/control_arena_{bash,shade,iac,rogue_eval,agentdojo}` | ⚠️ none declared |

> A corpus that declares no licence grants no permission to redistribute. This repository therefore
> stores none of their contents; `experiments/apps/koran_test_code.pkl` did until 2026-09-09 and was
> purged from git history on 2026-09-10 (`notes/05-permissibility.md`).
