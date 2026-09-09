#!/bin/bash
# Gate S, same-generator arm: have the model that wrote the honest class also write the attacks.
#
#   sbatch --export=MODEL=Qwen/Qwen3-Coder-30B-A3B-Instruct,TAG=q3c30 gate_s_backdoor.sbatch
#
#SBATCH --job-name=gate-s-bd
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_h100_nvl:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100G
#SBATCH --time=03:00:00
#SBATCH --output=/u/fvc9ch/ai-safety/authorship-not-sabotage/experiments/apps/bd_%x_%j.log
set -euo pipefail
REPO=/u/fvc9ch/ai-safety/authorship-not-sabotage
MODEL="${MODEL:-Qwen/Qwen3-Coder-30B-A3B-Instruct}"
TAG="${TAG:-q3c30}"
export HF_HOME=/bigtemp/fvc9ch/hf HF_HUB_ENABLE_HF_TRANSFER=1
export PATH="$REPO/.venv-gpu/bin:$PATH"
cd "$REPO/experiments/apps"
echo "=== $(date) | $(hostname) | $MODEL | $TAG ==="
python gen_backdoor.py --model "$MODEL" --honest-pass "pass_${TAG}.jsonl" \
                       --honest-gen "gen_${TAG}.jsonl" --out "bd_${TAG}.jsonl"
python verify_backdoor.py --backdoors "bd_${TAG}.jsonl" --honest-gen "gen_${TAG}.jsonl" \
                          --out "bdpass_${TAG}.jsonl"
echo "=== $(date) | DONE ==="
