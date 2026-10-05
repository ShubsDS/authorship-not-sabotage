"""Download the RoganInglis/apps-control-arena parquet shards (MIT, 5,000 rows).

Writes train_0000{0,1,2}.parquet in the working directory. Most scripts in this directory read
these shards.

Usage:
    python fetch.py
"""
import requests, json, sys
r = requests.get("https://datasets-server.huggingface.co/parquet?dataset=RoganInglis/apps-control-arena", timeout=60)
print(r.status_code)
j = r.json()
for f in j.get("parquet_files", []):
    print(f["split"], f["url"], f["size"])
    u = f["url"]
    out = f"{f['split']}_{f['filename']}"
    with requests.get(u, stream=True, timeout=300) as rr:
        rr.raise_for_status()
        with open(out, "wb") as fh:
            for ch in rr.iter_content(1<<20): fh.write(ch)
    print("saved", out)
