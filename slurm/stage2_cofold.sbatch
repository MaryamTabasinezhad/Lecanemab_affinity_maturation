#!/bin/bash
#SBATCH --job-name=stage2-cofold-wt
#SBATCH --account=def-hpcg6049_gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=%x-%j.out
# NO --partition on Frontenac (auto-routes to gpubase_*; verified 2026-06-03).
#
# Stage 2.2 — multi-seed Boltz-2 co-fold: WT lecanemab Fv + Aβ N-terminal 1-16 peptide.
# D-004 discipline: multiple seeds, multiple diffusion samples, fixed seeds, KEEP ALL SAMPLES.
# Establishes the WT iptm/ptm baseline that unblocks metrics.yaml thresholds.
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"   # CLUSTER + clusters/$CLUSTER.env (BOLTZ_CACHE, SCRATCH_ROOT)

echo "==== node ===="; hostname; date; nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true

source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-fold
unset PYTHONPATH; export PYTHONNOUSERSITE=1
export BOLTZ_CACHE="${BOLTZ_CACHE:-$SCRATCH_ROOT/cache/boltz}"

YAML="$REPO_ROOT/configs/stage2/cofold_wt_Abeta1-16.yaml"
RUNID="cofold-wt-Abeta1-16-${SLURM_JOB_ID}"
SCRATCH_RUN="$SCRATCH_ROOT/results/stage2/$RUNID"
REPO_OUT="$REPO_ROOT/results/stage2/$RUNID"
SEEDS="1 2 3 4 5"
SAMPLES=5
mkdir -p "$SCRATCH_RUN"

for s in $SEEDS; do
  echo "==== boltz predict seed $s ($SAMPLES samples) ===="
  boltz predict "$YAML" --cache "$BOLTZ_CACHE" --out_dir "$SCRATCH_RUN/seed_$s" \
    --accelerator gpu --devices 1 --diffusion_samples "$SAMPLES" \
    --output_format pdb --seed "$s" --num_workers 2 --override || { echo "SEED $s FAILED"; exit 1; }
done

echo "==== aggregate ===="
python "$REPO_ROOT/scripts/stage2_model/aggregate_cofold.py" \
  --scratch-dir "$SCRATCH_RUN" --repo-out "$REPO_OUT" --input-yaml "$YAML" \
  --seeds "$SEEDS" --samples "$SAMPLES"
echo "STAGE2_COFOLD_DONE  (summary -> $REPO_OUT/summary.json ; all samples -> $SCRATCH_RUN)"
