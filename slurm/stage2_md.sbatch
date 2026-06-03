#!/bin/bash
#SBATCH --job-name=stage2-md-flex
#SBATCH --account=def-hpcg6049_gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=%x-%j.out
# NO --partition on Frontenac.
#
# Stage 2.3 — short implicit-solvent MD of the best-ipSAE WT co-fold pose to test the
# B3 'flexible Aβ N-terminus' hypothesis (per-residue RMSF + DSSP coil fraction).
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"

echo "==== node ===="; hostname; date; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || true
source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-md
unset PYTHONPATH; export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib"      # force env libstdc++/nvrtc (CC StdEnv trap); libcuda via system

SEED_POSE="$SCRATCH_ROOT/results/stage2/cofold-wt-Abeta1-16-11544623/seed_2/boltz_results_cofold_wt_Abeta1-16/predictions/cofold_wt_Abeta1-16/cofold_wt_Abeta1-16_model_3.pdb"
MDDIR="$SCRATCH_ROOT/results/stage2/md-flex-${SLURM_JOB_ID}"
REPO_OUT="$REPO_ROOT/results/stage2/md-flex-${SLURM_JOB_ID}"

python "$REPO_ROOT/scripts/stage2_model/md_flexibility.py" --pdb "$SEED_POSE" --repo-out "$MDDIR" --ns 5
rc=$?
mkdir -p "$REPO_OUT"
cp "$MDDIR/md_flexibility.json" "$MDDIR/manifest_md.json" "$REPO_OUT/" 2>/dev/null || true
[ $rc -eq 0 ] && echo "STAGE2_MD_DONE (summary -> $REPO_OUT ; traj -> $MDDIR)" || { echo "STAGE2_MD_FAILED rc=$rc"; exit $rc; }
