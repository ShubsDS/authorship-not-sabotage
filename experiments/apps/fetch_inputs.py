"""Produce the three intermediate files the rest of `apps/` reads but nothing here created.

Before this existed the pipeline had a hole: `bow.py` opened `koran_test_code.pkl`,
`koran_split_eval.py` opened `koran_meta.parquet` and `monitor-summary.json`, and no script in
the repo wrote any of them — they were made by hand in the round-17 session. Run order is now:

    python fetch.py          # the three RoganInglis parquet shards
    python fetch_inputs.py   # koran_meta, rogan_meta, koran_test_code, monitor-summary
    python bow.py            # writes koran_samples.pkl
    python koran_split_eval.py / auroc.py / analyse.py / analyse2.py

`floors.py`, `matched.py`, `exact.py`, `transfer.py` and `koran.py` need only `fetch.py`.
Nothing is redistributed: every byte below is fetched from a public source at run time.
"""

import subprocess
import sys

import pandas as pd
import pyarrow.parquet as pq
import requests
from huggingface_hub import HfFileSystem

KORAN = "eugenekoran/apps-control-arena-high-quality"
ROGAN = "RoganInglis/apps-control-arena"
MONITOR_SUMMARY = (
    "https://raw.githubusercontent.com/anik-jha/challenger-panels/main/runs/x0/monitor-summary.json"
)


def koran_meta():
    """Column-projected metadata for both Koran splits, with a `split` column."""
    subprocess.run([sys.executable, "fetch_cols.py", KORAN, "koran_meta.parquet"], check=True)
    df = pd.read_parquet("koran_meta.parquet")
    print("koran_meta.parquet", df.shape, dict(df.split.value_counts()))


def rogan_meta():
    """Column-projected metadata for the full 5,000-row artifact (`auroc.py` reads this)."""
    subprocess.run([sys.executable, "fetch_cols.py", ROGAN, "rogan_meta.parquet"], check=True)
    df = pd.read_parquet("rogan_meta.parquet")
    print("rogan_meta.parquet", df.shape)


def koran_test_code():
    """The Koran test split with the code-bearing structs `bow.py` needs.

    `fetch_cols.py` drops `solutions`/`backdoors` on purpose (they are what makes the artifact
    744 MB). This pulls them for the test split only.
    """
    fs = HfFileSystem()
    files = sorted(f for f in fs.ls(f"datasets/{KORAN}/data", detail=False) if f.endswith(".parquet"))
    test = [f for f in files if "/test-" in f]
    if not test:
        raise SystemExit(f"no test shard among {files}")
    cols = ["problem_id", "solutions", "backdoors", "top_backdoor_model", "backdoor_works"]
    parts = []
    for f in test:
        with fs.open(f, "rb") as fh:
            parts.append(pq.ParquetFile(fh).read(columns=cols).to_pandas())
    df = pd.concat(parts, ignore_index=True)
    df.to_pickle("koran_test_code.pkl")
    print("koran_test_code.pkl", df.shape, "attack", int(df.backdoor_works.sum()))


def monitor_summary():
    """Jha's 24-monitor per-split summary (`2608.16190`, MIT)."""
    r = requests.get(MONITOR_SUMMARY, timeout=60)
    r.raise_for_status()
    with open("monitor-summary.json", "wb") as fh:
        fh.write(r.content)
    print("monitor-summary.json", len(r.content), "bytes")


if __name__ == "__main__":
    koran_meta()
    rogan_meta()
    koran_test_code()
    monitor_summary()
