#!/bin/bash
#SBATCH --job-name=stage5-flexddg
#SBATCH --account=def-hpcg6049_cpu
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=03:00:00
#SBATCH --array=1-15
#SBATCH --output=%x-%A_%a.out
# CPU job (no GPU). flex_ddG via PyRosetta. Array = 3 variants x 5 trajectories (nstruct).
# REDUCED settings for first integration (nstruct=5, backrub=10000) -> documented; framework
# mutations are interface-distal so ddG ~ 0 regardless. Use nstruct=35/backrub=35000 for CDR/
# interface mutations (T2/T3). One array task = one backrub trajectory.
set -uo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"

# variant list (sorted) + chains to move (P = the Aβ peptide separated for unbound)
VARIANTS=(LEC-AM-T1-0001 LEC-AM-T1-0002 LEC-AM-T1-0003)
NSTRUCT=5
idx=$(( SLURM_ARRAY_TASK_ID - 1 ))
vi=$(( idx / NSTRUCT )); ni=$(( idx % NSTRUCT + 1 ))
VID="${VARIANTS[$vi]}"
echo "==== task $SLURM_ARRAY_TASK_ID: $VID traj $ni ===="; hostname; date

source /global/software/python/anaconda3-2024.06-1/etc/profile.d/conda.sh
conda activate lecam-rosetta
unset PYTHONPATH; export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib"

PDB="$REPO_ROOT/data/interim/flexddg/wt_complex.pdb"
RESFILE="$REPO_ROOT/data/interim/flexddg/${VID}.resfile"
OUT="$SCRATCH_ROOT/results/stage5/flexddg/${VID}/$(printf '%02d' $ni)"
python "$REPO_ROOT/scripts/_tools/flexddg/flexddg_run.py" \
  --pdb "$PDB" --resfile "$RESFILE" --chains P --out "$OUT" \
  --backrub 10000 --min-iter 5000 --stride 10000 --abs-thresh 1.0
echo "STAGE5_FLEXDDG_TRAJ_DONE $VID $ni"
