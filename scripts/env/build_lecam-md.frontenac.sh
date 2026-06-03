#!/usr/bin/env bash
# build_lecam-md.frontenac.sh — provision the `lecam-md` env (OpenMM MD / ensembles).
#
# Role (CLAUDE.md §5, lecam-md): conformational ensembles (OpenMM; AlphaFlow optional).
# CUDA OpenMM platform VERIFIED on the A100 (job 11570164, Stage 2.3). All conda-forge.
#
# RUN gotcha: force the env lib so OpenMM's libstdc++/nvrtc win over the CC StdEnv
#   LD_LIBRARY_PATH (else GLIBCXX import errors) — see docs/env/env_mapping.md:
#   env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib conda run -n lecam-md python ...
# Versions pinned in docs/env/lecam-md.versions.txt.
#
# Usage: bash scripts/env/build_lecam-md.frontenac.sh [--dry-run]
set -euo pipefail
ENV=lecam-md
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1
run() { if [[ "$DRY" == 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

# cuda-version=12.4 pulls the CUDA-enabled OpenMM build + nvrtc (works on A100 driver 595.58).
# numpy stays <2 (openmm/mdtraj builds); mdtraj+pdbfixer for prep/analysis.
run "conda create -y -n $ENV -c conda-forge python=3.11 openmm pdbfixer mdtraj numpy cuda-version=12.4"

echo "Done. Verify CUDA platform ON A100 (login node lists only Reference/CPU — no GPU driver there):"
echo "  env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=\$CONDA_PREFIX/lib conda run -n $ENV \\"
echo "    python -c 'import openmm;print([openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])'"
