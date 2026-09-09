#!/bin/bash
# Gate S end to end through the Anthropic Batch API, both classes from one model.
#
#   . /path/to/.anthropic_env && nohup ./run_gate_s_api.sh > gate_s_api.log 2>&1 &
#
# Runs unattended for hours - batch latency dominates, not compute. Every stage is resumable:
# the generators skip problem_ids already on disk and reconnect to an in-flight batch via their
# state file, so an interrupted run is re-launched with the same command.
set -uo pipefail
cd "$(dirname "$0")"
TAG=sonnet5
say() { echo; echo "=============== $(date '+%H:%M:%S')  $*"; echo; }

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then echo "ANTHROPIC_API_KEY not set" >&2; exit 1; fi

# ---- 1. honest class, all 5,000 problems -------------------------------------------------
say "1/5  honest generation"
python3 gen_honest_api.py --out "gen_${TAG}.jsonl" --poll-seconds 60 || exit 1

# ---- 2. execute them against the shipped tests -------------------------------------------
say "2/5  executing honest solutions"
python3 run_tests.py --solutions "gen_${TAG}.jsonl" --out "pass_${TAG}.jsonl" --workers 12 \
  2>&1 | grep -vE "SyntaxWarning|^\s+[a-z_(\[]|\^" || exit 1

# ---- 3. attack class, from the SAME model, only where the honest solution passed ----------
# --spent carries the honest arm's real cost so the $100 ceiling is enforced on the total.
SPENT=$(python3 -c "
import json
t=sum(json.loads(l).get('n_output_tokens',0) for l in open('gen_${TAG}.jsonl'))
i=sum(json.loads(l).get('n_prompt_tokens',0) for l in open('gen_${TAG}.jsonl'))
print(f'{(i/1e6*2.0 + t/1e6*10.0)*0.5:.2f}')" 2>/dev/null || echo 0)
say "3/5  backdoor generation (honest arm cost so far: \$${SPENT})"
python3 gen_backdoor_api.py --honest-pass "pass_${TAG}.jsonl" --honest-gen "gen_${TAG}.jsonl" \
        --out "bd_${TAG}.jsonl" --spent "${SPENT}" --poll-seconds 60 || exit 1

# ---- 4. a backdoor counts only if it passes the tests AND diverges on its own trigger -----
say "4/5  verifying backdoors"
python3 verify_backdoor.py --backdoors "bd_${TAG}.jsonl" --honest-gen "gen_${TAG}.jsonl" \
        --out "bdpass_${TAG}.jsonl" 2>&1 | grep -vE "SyntaxWarning|^\s+[a-z_(\[]|\^" || exit 1

# ---- 5. the comparison that has no authorship gap in it ----------------------------------
say "5/5  same-generator evaluation"
python3 gate_s_samegen.py --tag "${TAG}" || exit 1

say "DONE - results in gate_s_samegen_${TAG}.json"
