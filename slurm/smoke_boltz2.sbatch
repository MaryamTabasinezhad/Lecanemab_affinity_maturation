#!/bin/bash
#SBATCH --job-name=boltz2-smoke
#SBATCH --account=def-hpcg6049_gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=%x-%j.out
# NO --partition flag on Frontenac (CLAUDE.md §5).
#
# Phase-0 GPU smoke test for lecam-fold / Boltz-2:
#   - confirms the A100 is visible + records driver (R-MODULES: torch bundles CUDA,
#     so no system CUDA module is loaded — only the node driver is needed),
#   - confirms torch sees CUDA,
#   - runs a 1-sample single-sequence Boltz-2 fold from the OFFLINE scratch weights.
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"   # sets CLUSTER + sources clusters/$CLUSTER.env

echo "==== node / gpu ===="; hostname; date
nvidia-smi || echo "WARN: nvidia-smi failed"

source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-fold
unset PYTHONPATH                      # drop CC StdEnv shim (see docs/env/env_mapping.md)
export PYTHONNOUSERSITE=1
export BOLTZ_CACHE="${BOLTZ_CACHE:-$SCRATCH_ROOT/cache/boltz}"

echo "==== torch CUDA check ===="
python - <<'PY'
import torch
print("torch", torch.__version__, "| cuda", torch.version.cuda,
      "| avail", torch.cuda.is_available(),
      "| device", torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
assert torch.cuda.is_available(), "CUDA not available on this node"
PY

OUT="$SCRATCH_ROOT/results/phase0_smoke/boltz2_${SLURM_JOB_ID}"
mkdir -p "$OUT"
echo "==== boltz predict (1 sample, single-seq GB1) -> $OUT ===="
time boltz predict "$REPO_ROOT/slurm/smoke/boltz2_gb1.yaml" \
  --cache "$BOLTZ_CACHE" --out_dir "$OUT" \
  --accelerator gpu --devices 1 --diffusion_samples 1 \
  --output_format pdb --seed 42 --num_workers 2 --override
rc=$?

echo "==== outputs ===="
find "$OUT" -type f \( -name '*.pdb' -o -name '*.json' \) | sort
[ $rc -eq 0 ] && echo "BOLTZ2_SMOKE_DONE" || { echo "BOLTZ2_SMOKE_FAILED rc=$rc"; exit $rc; }
