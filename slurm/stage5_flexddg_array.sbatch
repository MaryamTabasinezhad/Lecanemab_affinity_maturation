#!/bin/bash
#SBATCH --job-name=stage5-flexddg-t2
#SBATCH --account=def-hpcg6049_cpu
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=03:00:00
#SBATCH --output=%x-%A_%a.out
# Generalized flex_ddG array over a variant list. Submit with:
#   --array=1-(Nvariants*NSTRUCT)  --export=ALL,VLIST=<list.tsv>,NSTRUCT=<n>,BACKRUB=<n>
# Array task = (variant, trajectory). REDUCED triage default (NSTRUCT=5, BACKRUB=10000).
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"
NSTRUCT="${NSTRUCT:-5}"; BACKRUB="${BACKRUB:-10000}"
VLIST="${VLIST:?set VLIST=variant resfile list (id<TAB>resfile)}"

mapfile -t LINES < "$VLIST"
idx=$(( SLURM_ARRAY_TASK_ID - 1 ))
vi=$(( idx / NSTRUCT )); ni=$(( idx % NSTRUCT + 1 ))
LINE="${LINES[$vi]}"
VID=$(echo "$LINE" | cut -f1); RESFILE=$(echo "$LINE" | cut -f2)
echo "==== task $SLURM_ARRAY_TASK_ID: $VID traj $ni (nstruct=$NSTRUCT backrub=$BACKRUB) ===="; hostname; date

source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-rosetta; unset PYTHONPATH; export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib"

PDB="$REPO_ROOT/data/interim/flexddg/wt_complex.pdb"
OUT="$SCRATCH_ROOT/results/stage5/flexddg/${VID}/$(printf '%02d' $ni)"
python "$REPO_ROOT/scripts/_tools/flexddg/flexddg_run.py" \
  --pdb "$PDB" --resfile "$RESFILE" --chains P --out "$OUT" \
  --backrub "$BACKRUB" --min-iter 5000 --stride "$BACKRUB" --abs-thresh 1.0
echo "STAGE5_FLEXDDG_TRAJ_DONE $VID $ni"
