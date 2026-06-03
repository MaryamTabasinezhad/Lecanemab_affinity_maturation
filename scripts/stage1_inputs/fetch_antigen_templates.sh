#!/usr/bin/env bash
# fetch_antigen_templates.sh — download the Stage-1 antigen/reference coordinate files.
#
# Pulls the curated PDB coordinate (mmCIF) files listed in
#   data/raw/antigen/antigen_templates.md
# into data/raw/antigen/coords/ for the Stage-2 co-fold / counter-screen.
#
# Policy: coordinate files are git-IGNORED (heavy/fetched; the registry .md is the
#         git-tracked source of truth). This script is the reproducible fetch.
# Design: idempotent (skips files already present unless --force), --dry-run, set -euo.
#
# Usage:
#   bash scripts/stage1_inputs/fetch_antigen_templates.sh [--dry-run] [--force]
set -euo pipefail

# ---------------- locate repo + env ----------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/clusters/frontenac.env" ]] && source "${ROOT}/clusters/frontenac.env"

DEST="${ROOT}/data/raw/antigen/coords"
RCSB="https://files.rcsb.org/download"
DRY_RUN=0
FORCE=0

for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --force)   FORCE=1 ;;
    *) echo "ERROR: unknown arg: $a" >&2; exit 2 ;;
  esac
done

# ---------------- template registry (ID:role) ----------------
# Keep in sync with data/raw/antigen/antigen_templates.md
TEMPLATES=(
  # TARGETS — Aβ protofibril/oligomer/fibril (flexible N-terminus → engaged)
  "9CO4:target_oligomer_conf1"
  "7Q4B:target_fibril_typeI"
  "7Q4M:target_fibril_typeII"
  "8BFZ:target_fibril_arctic"
  # COUNTER-TARGETS — must stay negative (selectivity guardrail #1)
  "9CKI:counter_oligomer_conf2"
  "8QN7:counter_CAA_meningeal_Abeta40"
  "8OLN:counter_SwDI_fixedN"
  "1Z0Q:counter_monomer_Abeta42_ref"   # primary monomer reference (D-009)
  "2LFM:counter_monomer_Abeta40_ctrl"  # Aβ40 monomer control (D-009)
  # REFERENCE — epitope homology (pose ensemble, D-002 / D-010 / OQ-7)
  # Full-length N-terminal anti-Aβ Fab co-structures (primary homology set):
  "6CO3:ref_aducanumab_Abeta"        # aducanumab–Aβ (epitope 3-7)
  "5CSZ:ref_gantenerumab_Abeta1-11"  # gantenerumab Fab + Aβ1-11
  "3BKJ:ref_WO2_Abeta1-16"           # WO2 Fab + Aβ1-16 (closest to lecanemab 1-16 window)
  "4HIX:ref_3D6_bapineuzumab_Abeta"  # humanised 3D6 (bapineuzumab precursor) Fab + Aβ
  # Weak/indirect proxy cited by R-ELIFE (anti-pyroGlu pE3-12, NOT D3 — see caveat):
  "5MY4:ref_c17_pyroGlu_weakproxy"
)

run() { if [[ "$DRY_RUN" == 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

mkdir -p "${DEST}"
MANIFEST="${DEST}/fetch_manifest.tsv"
[[ "$DRY_RUN" == 1 ]] || printf "pdb_id\trole\tfile\tbytes\tstatus\n" > "${MANIFEST}"

echo "Destination: ${DEST}"
fail=0
for entry in "${TEMPLATES[@]}"; do
  id="${entry%%:*}"; role="${entry#*:}"
  lid="$(echo "$id" | tr '[:upper:]' '[:lower:]')"
  out="${DEST}/${lid}.cif"

  if [[ -s "$out" && "$FORCE" == 0 ]]; then
    echo "  [skip] ${id} (${role}) — exists"
    [[ "$DRY_RUN" == 1 ]] || printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$role" "${lid}.cif" "$(stat -c%s "$out")" "cached" >> "${MANIFEST}"
    continue
  fi

  echo "  [get ] ${id} (${role})"
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "[dry-run] curl -fsSL --max-time 120 ${RCSB}/${id}.cif -o ${out}"
    continue
  fi

  if curl -fsSL --max-time 120 "${RCSB}/${id}.cif" -o "${out}.tmp"; then
    # sanity: must contain atom records
    if grep -qE '^ATOM|^HETATM' "${out}.tmp"; then
      mv "${out}.tmp" "$out"
      printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$role" "${lid}.cif" "$(stat -c%s "$out")" "ok" >> "${MANIFEST}"
    else
      echo "    ERROR: ${id} downloaded but has no ATOM records" >&2
      rm -f "${out}.tmp"; printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$role" "${lid}.cif" 0 "no_atoms" >> "${MANIFEST}"
      fail=1
    fi
  else
    echo "    ERROR: fetch failed for ${id}" >&2
    rm -f "${out}.tmp"; printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$role" "${lid}.cif" 0 "fetch_fail" >> "${MANIFEST}"
    fail=1
  fi
done

[[ "$DRY_RUN" == 1 ]] || { echo; echo "Manifest: ${MANIFEST}"; column -t -s$'\t' "${MANIFEST}"; }
exit "$fail"
