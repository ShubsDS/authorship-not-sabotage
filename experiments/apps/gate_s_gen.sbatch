#!/bin/bash
# Gate S, stage 1 of 2: GENERATION. This is the only stage that needs a GPU.
#
# Deliberately asks for very few CPUs. The first attempt (job 6559462) bundled generation and test
# execution together and therefore asked for 16 cores alongside the card. The four H100 nodes have
# exactly 16 cores free each, so it never fit, and Slurm's estimated start slid to 2026-09-12 —
# the submission deadline. Generation is GPU-bound and needs almost no CPU; the CPU-heavy stage is
# now a separate job on the ordinary compute queue (gate_s_check.sbatch).
#
#   sbatch gate_s_gen.sbatch                                                   # Qwen3.8-27B
#   sbatch --export=MODEL=Qwen/Qwen3-Coder-30B-A3B-Instruct,TAG=q3c30 gate_s_gen.sbatch
#
# Qwen3.8-27B is dense (27.8B active every token) where Qwen3-Coder-30B-A3B is a mixture of experts
# with ~3B active, so the first is several times slower per token. Hence 3.5 hours rather than 2.
# Generation is resumable, so a job that hits the wall clock can be resubmitted to finish the tail.
#
# ⚠️ GPU TYPE, corrected 2026-09-09. This line said `nvidia_h100_nvl` while PLAN.md said Gate S
# had moved to A100s because every H100 is held by a job with >3d20h remaining — i.e. the H100
# queue does not clear before the deadline. Commit f52a291 ("Move Gate S to A100s") only added the
# --tp passthrough and never touched this line, so a job submitted as written would have queued
# against exactly the cards the plan had already written off.
#
# Set GRES when submitting if the cluster names its A100s differently:
#   sbatch --gres=gpu:nvidia_a100:2 --export=TP=2 gate_s_gen.sbatch
#SBATCH --job-name=gate-s-gen
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:2
#SBATCH --cpus-per-task=4
#SBATCH --mem=100G
#SBATCH --time=03:30:00
#SBATCH --output=/u/fvc9ch/ai-safety/authorship-not-sabotage/experiments/apps/gen_%x_%j.log

set -euo pipefail

REPO=/u/fvc9ch/ai-safety/authorship-not-sabotage
MODEL="${MODEL:-Qwen/Qwen3.8-27B}"
TAG="${TAG:-q38}"
TP="${TP:-2}"          # tensor_parallel_size. 2 on A100s (80GB): the 27.8B dense arm 1 does not
                       # fit one card at bf16. Override TP=1 for the 8B/14B ladder rungs, which do.

export HF_HOME=/bigtemp/fvc9ch/hf
export HF_HUB_ENABLE_HF_TRANSFER=1
export PATH="$REPO/.venv-gpu/bin:$PATH"   # vLLM shells out to `ninja`; without this on PATH it
                                          # dies at engine init with FileNotFoundError.

cd "$REPO/experiments/apps"
echo "=== $(date) | node $(hostname) | model $MODEL | tag $TAG ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo "tensor_parallel_size=$TP"

# Resumable: problem_ids already present in the output file are skipped, so a job that hits the
# wall clock can simply be resubmitted and will pick up the tail.
python gen_honest.py --model "$MODEL" --out "gen_${TAG}.jsonl" --tp "$TP"

echo "=== $(date) | generation done -> gen_${TAG}.jsonl ==="
wc -l "gen_${TAG}.jsonl"
