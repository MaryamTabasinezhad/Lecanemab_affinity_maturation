#!/bin/bash
#SBATCH --job-name=stage4-score
#SBATCH --account=def-hpcg6049_gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --array=1-3
#SBATCH --output=%x-%A_%a.out
# NO --partition on Frontenac.
#
# Stage 4 scoring — one array task per T1 variant: 5-seed x 5-sample Boltz-2 co-fold vs
# Aβ1-16 (identical to WT Stage 2.2) -> aggregate_cofold -> compute_ipsae. Delta-vs-WT
# is computed afterward by scripts/stage4_score/collect_scores.py.
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"

LIST="$REPO_ROOT/configs/stage4/variant_yaml_list.tsv"
LINE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LIST")
VID=$(echo "$LINE" | cut -f1); YAML=$(echo "$LINE" | cut -f2)
echo "==== task ${SLURM_ARRAY_TASK_ID}: $VID ===="; hostname; date

source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-fold; unset PYTHONPATH; export PYTHONNOUSERSITE=1
export BOLTZ_CACHE="${BOLTZ_CACHE:-$SCRATCH_ROOT/cache/boltz}"

RUNID="score-${VID}"
SCRATCH_RUN="$SCRATCH_ROOT/results/stage4/$RUNID"
REPO_OUT="$REPO_ROOT/results/stage4/$RUNID"
SEEDS="1 2 3 4 5"; SAMPLES=5
mkdir -p "$SCRATCH_RUN"
for s in $SEEDS; do
  boltz predict "$YAML" --cache "$BOLTZ_CACHE" --out_dir "$SCRATCH_RUN/seed_$s" \
    --accelerator gpu --devices 1 --diffusion_samples "$SAMPLES" \
    --output_format pdb --seed "$s" --num_workers 2 --override || { echo "SEED $s FAIL"; exit 1; }
done
python "$REPO_ROOT/scripts/stage2_model/aggregate_cofold.py" --scratch-dir "$SCRATCH_RUN" \
  --repo-out "$REPO_OUT" --input-yaml "$YAML" --seeds "$SEEDS" --samples "$SAMPLES"
python "$REPO_ROOT/scripts/stage2_model/compute_ipsae.py" --scratch-dir "$SCRATCH_RUN" --repo-out "$REPO_OUT"
echo "STAGE4_SCORE_DONE $VID -> $REPO_OUT"
