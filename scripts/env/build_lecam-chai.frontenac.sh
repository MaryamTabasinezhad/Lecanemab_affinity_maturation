#!/usr/bin/env bash
# build_lecam-chai.frontenac.sh — provision the `lecam-chai` env (Chai-1) on Frontenac.
#
# Chai-1 is the SECONDARY co-folding oracle (consensus member alongside Boltz-2/AF3 for
# the D-004 multi-sample ipTM+ipSAE ranking). It lives in its OWN env because chai_lab
# conflicts with Boltz on shared deps (requests/protobuf/pandas/rdkit) — see
# docs/env/env_mapping.md and the §5 "one isolated env per heavy tool" rule.
#
# Frontenac pip gotchas: CC wheelhouse + _manylinux shim -> env -u PYTHONPATH ... (as below).
# Weights (incl a traced ESM2-3B, ~6 GB) cache to scratch via CHAI_DOWNLOADS_DIR.
# Versions pinned in docs/env/lecam-chai.versions.txt.
#
# Usage: bash scripts/env/build_lecam-chai.frontenac.sh [--dry-run]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../../clusters/frontenac.env"
ENV=lecam-chai
CACHE="$SCRATCH_ROOT/cache/chai"
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1
PIP() { env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null \
        conda run -n "$ENV" pip install --no-cache-dir --index-url https://pypi.org/simple "$@"; }
run() { if [[ "$DRY" == 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

run "conda create -y -n $ENV -c conda-forge python=3.11 pip 'numpy=1.26'"
run "PIP chai_lab 'torch<2.7'"

# pre-fetch ALL weights to scratch on the login node (CHAI_DOWNLOADS_DIR read at import):
#   conformers + 6 model components (trunk/diffusion_module/confidence_head/...) + ESM2-3B.
run "mkdir -p '$CACHE'"
cat > /tmp/_dl_chai.py <<'PY'
from chai_lab.utils.paths import cached_conformers, chai1_component, download_if_not_exists, downloads_path
from chai_lab.data.dataset.embeddings.esm import ESM_URL
cached_conformers.get_path()
for k in ["feature_embedding.pt","bond_loss_input_proj.pt","token_embedder.pt","trunk.pt","diffusion_module.pt","confidence_head.pt"]:
    chai1_component(k)
download_if_not_exists(ESM_URL, downloads_path.joinpath("esm","traced_sdpa_esm2_t36_3B_UR50D_fp16.pt"))
print("CHAI_WEIGHTS_DONE")
PY
run "env -u PYTHONPATH PYTHONNOUSERSITE=1 CHAI_DOWNLOADS_DIR='$CACHE' conda run -n $ENV python /tmp/_dl_chai.py"

cat <<EOF

Done. lecam-chai (Chai-1) ready; weights in $CACHE.
At run time export CHAI_DOWNLOADS_DIR="$CACHE" so chai_lab finds the offline weights.
GPU smoke test (A100 — owed): chai_lab fold on a small complex.
EOF
