#!/bin/bash
# Generation of the open-weight honest class (arm 1). This is the only stage that needs a GPU.
#
# It asks for few CPUs because generation is GPU-bound; the CPU-heavy test execution is a separate
# job on the ordinary compute queue (gate_s_check.sbatch). Submit from experiments/apps, and create
# logs/ there first, since #SBATCH --output cannot expand variables.
#
# The defaults are the paper's arm 1 (Qwen3-Coder-30B-A3B-Instruct, tag q3c30):
#   sbatch gate_s_gen.sbatch
# Another model: sbatch --export=ALL,MODEL=<hf id>,TAG=<tag> gate_s_gen.sbatch
#
# Generation is resumable, so a job that hits the wall clock can be resubmitted to finish the tail.
# Set GRES when submitting if the cluster names its A100s differently:
#   sbatch --gres=gpu:nvidia_a100:2 --export=ALL,TP=2 gate_s_gen.sbatch
#SBATCH --job-name=gate-s-gen
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:2
#SBATCH --cpus-per-task=4
#SBATCH --mem=100G
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

REPO="${REPO:-$SLURM_SUBMIT_DIR/../..}"
MODEL="${MODEL:-Qwen/Qwen3-Coder-30B-A3B-Instruct}"
TAG="${TAG:-q3c30}"
TP="${TP:-2}"          # tensor_parallel_size: the two GPUs requested above

export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export HF_HUB_ENABLE_HF_TRANSFER=1
export PATH="$REPO/.venv-gpu/bin:$PATH"   # vLLM shells out to `ninja`; without this on PATH it
                                          # dies at engine init with FileNotFoundError.

cd "$REPO/experiments/apps"
echo "=== $(date) | node $(hostname) | model $MODEL | tag $TAG ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo "tensor_parallel_size=$TP"

# Resumable: problem_ids already present in the output file are skipped.
python gen_honest.py --model "$MODEL" --out "gen_${TAG}.jsonl" --tp "$TP"

echo "=== $(date) | generation done -> gen_${TAG}.jsonl ==="
wc -l "gen_${TAG}.jsonl"
