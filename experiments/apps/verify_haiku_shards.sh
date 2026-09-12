#!/bin/bash
# Verify each Haiku independent-arm draw file separately, as verify_all_shards.sh does for Sonnet.
#
# Within a shard problem_id is unique, so the verifier's output maps 1:1 onto draws; pooling first
# would make a success unattributable to the draw that produced it. But `merge_draws.py select`
# joins draws to verdicts by the `draw` key, and `gen_backdoor_api.py` does not write one - only
# `merge` does. So the order is: merge (tags every draw), split the tagged pool back out by source,
# verify each tagged shard, concatenate the verdicts. Verifying the raw pre-merge files instead
# would produce verdicts with `draw: null` and `select` would refuse them.
#
# Writes only *_haiku45* names. The Sonnet pool files are frozen inputs and are never touched.
set -euo pipefail
cd "$(dirname "$0")"

DRAWS=(bdind_haiku45.jsonl bdind_haiku45_r2.jsonl bdind_haiku45_r3.jsonl)
PRESENT=()
for f in "${DRAWS[@]}"; do [ -s "$f" ] && PRESENT+=("$f"); done
echo "draw files present: ${PRESENT[*]}"

python3 merge_draws.py merge "${PRESENT[@]}" --out bdind_haiku45_retry.jsonl

python3 - <<'PY'
import json, collections
by = collections.OrderedDict()
for l in open("bdind_haiku45_retry.jsonl"):
    if l.strip():
        r = json.loads(l)
        by.setdefault(r["source"], []).append(r)
for src, recs in by.items():
    path = f"shard_{src}.jsonl"
    with open(path, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    pids = [r["problem_id"] for r in recs]
    assert len(pids) == len(set(pids)), f"{src}: problem_id repeats within a shard"
    print(f"  wrote {path}: {len(recs)} draws")
PY

for f in shard_*.jsonl; do
  out="vp_${f%.jsonl}.jsonl"
  [ -s "$out" ] && { echo "  $out exists, skipped"; continue; }
  python3 verify_backdoor.py --backdoors "$f" --honest-gen gen_haiku45.jsonl --out "$out" \
    2>/dev/null | grep -a "USABLE" | sed "s|^|${f}: |"
done

cat vp_shard_*.jsonl > bdindpass_haiku45_retry.jsonl
echo "pooled verdicts: $(wc -l < bdindpass_haiku45_retry.jsonl) lines"
echo "ALL HAIKU SHARDS VERIFIED"
