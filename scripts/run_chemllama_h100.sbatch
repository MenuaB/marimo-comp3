#!/usr/bin/env bash
#SBATCH --job-name=chemllama-1b-pilot
#SBATCH --partition=research
#SBATCH --gres=gpu:h100:1
#SBATCH --exclude=ap-rtx
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=/mnt/weka/mbedrosian/code/marimo/outputs/chemllama/slurm/%x-%j.out
#SBATCH --error=/mnt/weka/mbedrosian/code/marimo/outputs/chemllama/slurm/%x-%j.err
set -euo pipefail
cd /mnt/weka/mbedrosian/code/marimo
args=(--config config/chemllama_generation.json --run-id "chemllama-${SLURM_JOB_ID}")
if [[ "${CHEMLLAMA_SMOKE_ONLY:-0}" == "1" ]]; then
  args+=(--smoke-only)
fi
exec .venv-inference/bin/python scripts/generate_chemllama.py "${args[@]}"
