#!/usr/bin/env bash
# build_lecam-rosetta.frontenac.sh — provision `lecam-rosetta` (PyRosetta physics scoring).
#
# Role (CLAUDE.md §5): PyRosetta, Rosetta flex_ddG, AbLIFT, FoldX. This env provides PyRosetta
# (academic license auto-accepted by the installer) and runs the flex_ddG ΔΔG protocol via
# PyRosetta's RosettaScriptsParser (no compiled rosetta_scripts binary needed) — see
# scripts/_tools/flexddg/. FoldX (separate licensed binary) + AbLIFT protocol are TODO.
#
# PyRosetta comes from pip (pyrosetta-installer), NOT the slow rosettacommons conda channel.
# distributed=True -> the cxx11thread.serialization build required by BackrubProtocol/flex_ddG.
# RUN gotcha: LD_LIBRARY_PATH=$CONDA_PREFIX/lib (PyRosetta compiled libs vs CC StdEnv).
# Versions pinned in docs/env/lecam-rosetta.versions.txt.
#
# Usage: bash scripts/env/build_lecam-rosetta.frontenac.sh [--dry-run]
set -euo pipefail
ENV=lecam-rosetta
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1
run() { if [[ "$DRY" == 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

run "conda create -y -n $ENV -c conda-forge python=3.10 pip numpy pandas"
run "env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null conda run -n $ENV \
      pip install --no-cache-dir --index-url https://pypi.org/simple pyrosetta-installer"
# ~1.5 GB download of the PyRosetta wheel:
run "env -u PYTHONPATH PYTHONNOUSERSITE=1 conda run -n $ENV \
      python -c 'import pyrosetta_installer; pyrosetta_installer.install_pyrosetta(distributed=True)'"

echo "Verify: env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=\$CONDA_PREFIX/lib conda run -n $ENV \\"
echo "  python -c 'import pyrosetta; pyrosetta.init(\"-mute all\"); print(\"pyrosetta OK\")'"
