#!/bin/bash
#SBATCH --job-name=s6-dock
#SBATCH --account=def-hpcg6049_cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=%x-%j.out
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"
source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-rosetta; unset PYTHONPATH; export PYTHONNOUSERSITE=1; export LD_LIBRARY_PATH="$CONDA_PREFIX/lib"
python "$REPO_ROOT/scripts/stage6_select/dock_fv_protofibril.py" --mode dock \
  --receptor-cif "$REPO_ROOT/$RECEPTOR" --receptor-chains "$CHAINS" --epitope-res "$EPIRES" \
  --out "$REPO_ROOT/$OUTDIR" --ndecoys "${NDECOYS:-20}"
echo "S6_DOCK_DONE $OUTDIR"
