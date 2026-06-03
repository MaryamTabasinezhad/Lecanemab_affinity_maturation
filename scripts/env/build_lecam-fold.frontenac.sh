#!/usr/bin/env bash
# build_lecam-fold.frontenac.sh — provision the `lecam-fold` env (Boltz-2) on Frontenac.
#
# Role (CLAUDE.md §5, lecam-fold): co-folding oracle. Boltz-2 is the Stage-5 affinity
#   ranker (D-004: multi-sample ipTM+ipSAE consensus). Boltz-2 also ships an AFFINITY
#   model (boltz2_aff.ckpt). Chai-1 is a SEPARATE env (build_lecam-chai.frontenac.sh) —
#   it conflicts with Boltz on shared deps (requests/protobuf/pandas/rdkit), so per the
#   §5 "one isolated env per heavy tool" rule they are not co-installed. AF3 = container.
#
# Frontenac pip gotchas (see docs/env/env_mapping.md): CC wheelhouse + _manylinux shim.
#   -> every pip call uses: env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null
#   PyPI's default `torch` wheel bundles CUDA 12 (proven on this A100) -> install from PyPI.
# Versions pinned in docs/env/lecam-fold.versions.txt.
#
# Usage: bash scripts/env/build_lecam-fold.frontenac.sh [--dry-run]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../../clusters/frontenac.env"
ENV=lecam-fold
CACHE="$SCRATCH_ROOT/cache/boltz"   # weights live on scratch (multi-GB), NOT $HOME
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1
PIP() { env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null \
        conda run -n "$ENV" pip install --no-cache-dir --index-url https://pypi.org/simple "$@"; }
run() { if [[ "$DRY" == 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

# 1) env core (numpy<2 — Boltz pin). 2) Boltz-2 (cap torch<2.7). 3) matplotlib
#    (torchmetrics imports matplotlib.axes via pytorch-lightning).
run "conda create -y -n $ENV -c conda-forge python=3.11 pip 'numpy=1.26'"
run "PIP boltz 'torch<2.7'"
run "PIP matplotlib"

# 4) pre-download weights to scratch on the LOGIN node (compute nodes have no internet):
#    boltz2_conf.ckpt (struct), boltz2_aff.ckpt (affinity), CCD mols.  ~7.9 GB.
run "mkdir -p '$CACHE'"
run "env -u PYTHONPATH PYTHONNOUSERSITE=1 conda run -n $ENV python -c \"from pathlib import Path; from boltz.main import download_boltz2; download_boltz2(Path('$CACHE'))\""

cat <<EOF

Done. lecam-fold (Boltz-2) ready; weights in $CACHE.
GPU fold smoke test (A100 — still owed) runs predict with --cache pointing there:
  boltz predict <input.fasta|yaml> --cache "$CACHE" --use_msa_server  # (or precomputed MSA)
EOF
