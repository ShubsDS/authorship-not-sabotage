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
#SBATCH --job-name=gate-s-gen
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_h100_nvl:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=100G
#SBATCH --time=03:30:00
#SBATCH --output=/u/fvc9ch/ai-safety/authorship-not-sabotage/experiments/apps/gen_%x_%j.log

set -euo pipefail

REPO=/u/fvc9ch/ai-safety/authorship-not-sabotage
MODEL="${MODEL:-Qwen/Qwen3.8-27B}"
TAG="${TAG:-q38}"

export HF_HOME=/bigtemp/fvc9ch/hf
export HF_HUB_ENABLE_HF_TRANSFER=1
export PATH="$REPO/.venv-gpu/bin:$PATH"   # vLLM shells out to `ninja`; without this on PATH it
                                          # dies at engine init with FileNotFoundError.

cd "$REPO/experiments/apps"
echo "=== $(date) | node $(hostname) | model $MODEL | tag $TAG ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Resumable: problem_ids already present in the output file are skipped, so a job that hits the
# wall clock can simply be resubmitted and will pick up the tail.
python gen_honest.py --model "$MODEL" --out "gen_${TAG}.jsonl"

echo "=== $(date) | generation done -> gen_${TAG}.jsonl ==="
wc -l "gen_${TAG}.jsonl"
