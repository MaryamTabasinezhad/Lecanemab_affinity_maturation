#!/bin/bash
#SBATCH --job-name=lecam
#SBATCH --output=%x-%A_%a.out
# Frontenac defaults below; other clusters override via clusters/<cluster>.env.
#SBATCH --account=def-hpcg6049_gpu     # Frontenac default
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8              # tune per tool
#SBATCH --mem=48G                      # tune per tool
#SBATCH --time=08:00:00                # tune per stage (workers may allow longer)
# NO --partition flag on Frontenac
# module load ...                      # CONFIRM module names per cluster before first submit
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"   # sets $CLUSTER + sources clusters/$CLUSTER.env
# conda activate "$CONDA_ENV_MAIN" (or stage-specific env), then run the stage script.
# Always write results/<stage>/<run-id>/manifest.json (inputs, versions, seeds, job id).
