import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem
fs = HfFileSystem()
COLS = ["problem_id","difficulty","question","has_backdoor","has_apps_backdoor",
        "has_control_tax_backdoor","solution_compiles","solution_passes_tests",
        "backdoor_solution_compiles","backdoor_solution_passes_tests","backdoor_works",
        "apps_backdoor_works","control_tax_backdoor_works","is_nondeterministic",
        "nondeterminism_score","nondeterminism_category","num_tests","top_backdoor_model"]
import sys
repo, out = sys.argv[1], sys.argv[2]
files = [f for f in fs.ls(f"datasets/{repo}/data", detail=False) if f.endswith(".parquet")]
print("files:", files)
import pyarrow as pa
tabs=[]
for f in sorted(files):
    with fs.open(f, "rb") as fh:
        pf = pq.ParquetFile(fh)
        avail = [c for c in COLS if c in pf.schema_arrow.names]
        t = pf.read(columns=avail)
        print(f, "rows", t.num_rows, "cols", len(avail))
        split = "test" if "/test-" in f else "train"
        t = t.append_column("split", pa.array([split]*t.num_rows))
        tabs.append(t)
full = pa.concat_tables(tabs, promote_options="default")
df = full.to_pandas()
df["q_len"] = df["question"].str.len()
df = df.drop(columns=["question"])
df.to_parquet(out)
print("saved", out, df.shape)
print(df.dtypes)
