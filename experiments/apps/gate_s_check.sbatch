#!/bin/bash
# Gate S, stage 2 of 2: EXECUTION and EVALUATION. No GPU required.
#
# Runs every generated program against the test cases that ship with its problem, keeps the ones
# that pass all of them, then fits the word-frequency classifier twice — once separating the
# human-written honest code from the backdoored code, once separating the model-written honest code
# from the same backdoored code — and reports how much of the signal survived. That ratio routes
# the paper's title.
#
# Submit it chained to the generation job so it starts by itself:
#   sbatch --dependency=afterok:<gen_job_id> gate_s_check.sbatch
#
#SBATCH --job-name=gate-s-check
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/u/fvc9ch/ai-safety/authorship-not-sabotage/experiments/apps/check_%x_%j.log

set -euo pipefail

REPO=/u/fvc9ch/ai-safety/authorship-not-sabotage
TAG="${TAG:-q3c30}"

cd "$REPO/experiments/apps"
echo "=== $(date) | node $(hostname) | tag $TAG ==="

if [ ! -s "gen_${TAG}.jsonl" ]; then
  echo "gen_${TAG}.jsonl is missing or empty - generation did not produce anything" >&2
  exit 1
fi

# Executes model-written code, so each program runs in its own process under a wall-clock limit,
# an address-space limit measured on top of what the child inherits, and in a scratch directory.
echo "=== executing generated solutions against the shipped tests ==="
python run_tests.py --solutions "gen_${TAG}.jsonl" --out "pass_${TAG}.jsonl" --workers 14

echo "=== fitting the classifier twice and routing the title ==="
python gate_s_eval.py --gen-file "gen_${TAG}.jsonl" --pass-file "pass_${TAG}.jsonl" \
                     --label "$TAG" --out "gate_s_${TAG}.json"

echo "=== $(date) | DONE ==="
cat "gate_s_${TAG}.json"
