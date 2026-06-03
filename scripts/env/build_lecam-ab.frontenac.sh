#!/usr/bin/env bash
# build_lecam-ab.frontenac.sh — provision the `lecam-ab` conda env on Frontenac.
#
# Role (CLAUDE.md §5, lecam-ab): antibody structure modeling + antibody LMs.
# Installs (verified working 2026-06-03): ImmuneBuilder (ABodyBuilder2), IgFold,
#          AntiBERTy, AbLang2. BioPhi/Sapiens (humanness) is DEFERRED to its own
#          env (fairseq/Flask dep conflicts; Stage-6 tool, not a Stage-2 blocker).
#
# Frontenac build gotchas (do NOT remove — these are why earlier attempts failed):
#   1. CC wheelhouse hijacks pip (PIP_CONFIG_FILE -> CVMFS; +computecanada wheels
#      target glibc 2.29/2.30, break on system glibc 2.28). -> PIP_CONFIG_FILE=/dev/null
#   2. CC StdEnv injects PYTHONPATH=/cvmfs/.../custom/python/site-packages which holds
#      a _manylinux.py shim that DISABLES manylinux wheel detection (36 tags, no
#      manylinux) -> pip falls back to source builds (needs Rust for tokenizers, fails).
#      -> run pip with `env -u PYTHONPATH` (restores 657 tags incl manylinux_2_17).
#   3. py3.12 pydantic in ~/.local leaks into conda's plugin loader -> harmless
#      anaconda-cloud-auth GLIBC_2.30 warning. -> PYTHONNOUSERSITE=1 (cosmetic).
# Versions pinned in docs/env/lecam-ab.versions.txt.
#
# Usage: bash scripts/env/build_lecam-ab.frontenac.sh [--dry-run]
set -euo pipefail

ENV=lecam-ab
PYVER=3.10
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

# pip wrapper: bypass CC wheelhouse (config) AND CC _manylinux shim (PYTHONPATH).
PIP() { env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null \
        conda run -n "$ENV" pip install --no-cache-dir "$@"; }
run() { if [[ "$DRY" == 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

# 1) conda core from conda-forge/bioconda (compiled deps; glibc-portable).
run "conda create -y -n $ENV -c conda-forge -c bioconda \
       python=$PYVER pip numpy scipy openmm hmmer anarci pdbfixer"

# 2) PyTorch CPU 2.5.1 (NOT 2.6: 2.6 flips torch.load weights_only=True -> IgFold ckpts fail).
run "PIP --index-url https://download.pytorch.org/whl/cpu 'torch==2.5.1'"

# 3) ImmuneBuilder (ABodyBuilder2) — primary Stage-2 Fv predictor.
run "PIP --index-url https://pypi.org/simple ImmuneBuilder"

# 4) Antibody LMs. Pin transformers 4.40.2 stack: antiberty 0.1.3 breaks on
#    transformers 5.x ('all_tied_weights_keys').
run "PIP --index-url https://pypi.org/simple antiberty ablang2 \
       'transformers==4.40.2' 'tokenizers==0.19.1' 'huggingface_hub==0.23.5'"

# 5) IgFold (secondary Fv predictor / model ensemble). Needs pkg_resources
#    (setuptools<81) + matplotlib; keep the core pins as constraints.
run "PIP --index-url https://pypi.org/simple igfold matplotlib 'setuptools<81' \
       'transformers==4.40.2' 'tokenizers==0.19.1' 'huggingface_hub==0.23.5' 'numpy==2.2.6'"

echo
echo "Done. Verify (downloads model weights on login node; compute nodes have no internet):"
echo "  env -u PYTHONPATH PYTHONNOUSERSITE=1 conda run -n $ENV python -c \\"
echo "    'from ImmuneBuilder import ABodyBuilder2; from antiberty import AntiBERTyRunner; \\"
echo "     import ablang2; from igfold import IgFoldRunner; ABodyBuilder2(); AntiBERTyRunner(); \\"
echo "     ablang2.pretrained(); IgFoldRunner(); print(\"lecam-ab OK\")'"
