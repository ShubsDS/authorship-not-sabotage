import fsspec, pyarrow.parquet as pq, pandas as pd, numpy as np, collections
fs=fsspec.filesystem("https"); B="https://huggingface.co/datasets/"
def rd(urls,cols):
    o=[]
    for u in urls:
        pf=pq.ParquetFile(fs.open(u)); o.append(pf.read(columns=[c for c in cols if c in pf.schema_arrow.names]).to_pandas())
    return pd.concat(o,ignore_index=True)
print("########## RoganInglis/apps-control-arena")
df=rd([f"{B}RoganInglis/apps-control-arena/resolve/main/data/train-0000{i}-of-00003.parquet" for i in range(3)],
      ["backdoors","has_backdoor","solutions"])
mc=collections.Counter()
for bl in df["backdoors"]:
    for b in (bl if bl is not None else []): mc[b.get("source"),b.get("model")]+=1
print("  backdoor (source,model) counts:", dict(mc))
print("  honest `solutions` struct fields:", df['solutions'].iloc[0][0].keys() if len(df['solutions'].iloc[0]) else None,
      "-> NO model/author field (honest = codeparrot/apps human solutions)")
print("\n########## RoganInglis/control-tax")
pf=pq.ParquetFile(fs.open(f"{B}RoganInglis/control-tax/resolve/main/data/train-00000-of-00001.parquet"))
print("  rows",pf.metadata.num_rows); print("  cols",pf.schema_arrow.names)
print("\n########## RoganInglis/apps-backdoors")
pf2=pq.ParquetFile(fs.open(f"{B}RoganInglis/apps-backdoors/resolve/main/data/train-00000-of-00003.parquet"))
print("  cols",pf2.schema_arrow.names)
