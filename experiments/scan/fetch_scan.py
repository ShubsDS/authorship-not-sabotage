"""Pull the five ControlArena agentic settings as `ca_<setting>.parquet`.

`matched.py`, `floors.py`, `floors2.py` and `cot.py` all read these and **nothing produced them** —
the same missing-producer hole that `../apps/fetch_inputs.py` fixes on the APPS side. Run this first.

    python fetch_scan.py

⚠️ None of the five declares a licence (`../../notes/05-permissibility.md`). We redistribute nothing:
this fetches them at run time and `.gitignore` keeps the parquets out. The paper reports aggregates
only and says the licences are absent.

⚠️ `rogue_eval` ships its 1,500 rows under a **`test`** split where the other four use `train`.
"""

from __future__ import annotations

import io

import pandas as pd
import requests

SETTINGS = ["bash", "shade", "iac", "rogue_eval", "agentdojo"]
INFO = "https://datasets-server.huggingface.co/parquet?dataset=adityaasinha28/control_arena_{}"


def main() -> None:
    for s in SETTINGS:
        r = requests.get(INFO.format(s), timeout=60)
        r.raise_for_status()
        files = r.json()["parquet_files"]
        frames = []
        for f in files:
            with requests.get(f["url"], timeout=600) as rr:
                rr.raise_for_status()
                frames.append(pd.read_parquet(io.BytesIO(rr.content)))
        df = pd.concat(frames, ignore_index=True)
        out = f"ca_{s}.parquet"
        df.to_parquet(out, index=False)
        splits = {f["split"] for f in files}
        print(f"{s:11s} {len(df):5d} rows  splits={sorted(splits)}  "
              f"attack={int(df.ground_truth.astype(int).sum())}  -> {out}")


if __name__ == "__main__":
    main()
