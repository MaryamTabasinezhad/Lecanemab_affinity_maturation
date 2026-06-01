#!/usr/bin/env bash
# 00_init.sh — Phase-0 bootstrap for the lecanemab-am AM pipeline (multi-cluster).
#
# Creates: repo skeleton (CLAUDE.md §6), git remote, the clusters/ + coordination/
#          multi-agent scaffold (per the lab's MULTI_AGENT_COORDINATION_GUIDE),
#          config + SLURM + doc stubs, and the DuckDB variant ledger.
#          With --with-envs it also creates the conda env shells (CLAUDE.md §5).
#
# Design: idempotent (never clobbers existing files), supports --dry-run.
#         Deterministic steps are automated; licensed/container tools and
#         unconfirmed cluster details are SCAFFOLDED with CONFIRM markers, not guessed.
#
# Coordinator: Frontenac. Workers (Narval/Nibi) are stubbed, activate when hired.
# Intended final location: scripts/stage1_inputs/00_init.sh
#
# First run on Frontenac (login node; tree does not exist yet):
#   mkdir -p /global/project/hpcg6049/lecanemab-am && cd /global/project/hpcg6049/lecanemab-am
#   bash /path/to/00_init.sh            # self-copies into scripts/stage1_inputs/ afterward
#
set -euo pipefail

# ---------------- defaults ----------------
ROOT="/global/project/hpcg6049/lecanemab-am"
GIT_REMOTE="git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git"
GIT_BRANCH="main"
DRY_RUN=0
WITH_ENVS=0
PYVER="3.11"
TS="$(date +%Y%m%d-%H%M%S)"

usage() {
  cat <<USAGE
Usage: bash 00_init.sh [--root DIR] [--dry-run] [--with-envs] [-h|--help]
  --root DIR     repo root to bootstrap (default: ${ROOT})
  --dry-run      print every action without changing anything
  --with-envs    also create conda env shells (needs conda or mamba)
USAGE
}

# ---------------- arg parse ----------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    --with-envs) WITH_ENVS=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

# ---------------- helpers ----------------
log() { printf '[init] %s\n' "$*"; }
run() { if [[ $DRY_RUN -eq 1 ]]; then printf '[dry-run] %s\n' "$*"; else eval "$*"; fi; }
write_if_absent() {           # write_if_absent <path> ; body on stdin; writes only if absent
  local path="$1"
  if [[ -e "$path" ]]; then
    log "exists, skip: $path"; cat > /dev/null
  elif [[ $DRY_RUN -eq 1 ]]; then
    log "[dry-run] would write: $path"; cat > /dev/null
  else
    mkdir -p "$(dirname "$path")"; cat > "$path"; log "wrote: $path"
  fi
}

log "root=$ROOT  dry_run=$DRY_RUN  with_envs=$WITH_ENVS  python=$PYVER  branch=$GIT_BRANCH"

# ---------------- 1. directory tree ----------------
DIRS=(
  configs
  data/raw/antigen data/interim data/processed
  scripts/stage1_inputs scripts/stage2_modeling scripts/stage3_paratope
  scripts/stage4_generate scripts/stage5_score scripts/stage6_select_dev
  scripts/stage7_format scripts/stage8_validate
  slurm db db/exports results notebooks container
  docs/decisions docs/sources docs/env
  clusters clusters/frontenac
  coordination coordination/manifests coordination/globus
  coordination/inbox coordination/inbox/frontenac coordination/inbox/narval coordination/inbox/nibi
)
for d in "${DIRS[@]}"; do run "mkdir -p '$ROOT/$d'"; done

for d in data/raw/antigen data/interim data/processed results notebooks db db/exports container \
         coordination/manifests coordination/inbox/frontenac coordination/inbox/narval coordination/inbox/nibi; do
  write_if_absent "$ROOT/$d/.gitkeep" < /dev/null
done

# ---------------- 2. git repo + remote ----------------
if [[ $DRY_RUN -eq 1 ]]; then
  log "[dry-run] would: git init + remote origin=$GIT_REMOTE (branch $GIT_BRANCH)"
elif command -v git >/dev/null 2>&1; then
  if [[ ! -d "$ROOT/.git" ]]; then
    git -C "$ROOT" init -q
    git -C "$ROOT" symbolic-ref HEAD "refs/heads/$GIT_BRANCH" 2>/dev/null || true
    log "git init (branch $GIT_BRANCH): $ROOT"
  fi
  if git -C "$ROOT" remote | grep -qx origin; then
    git -C "$ROOT" remote set-url origin "$GIT_REMOTE"
  else
    git -C "$ROOT" remote add origin "$GIT_REMOTE"
  fi
  log "git remote origin = $GIT_REMOTE"
else
  log "WARN: git not found; skipping repo init (set remote manually: $GIT_REMOTE)."
fi

write_if_absent "$ROOT/.gitignore" <<'EOF'
# Heavy artifacts live on scratch + move via Globus — NOT git.
*.sif
*.duckdb
*.duckdb.wal
__pycache__/
*.pyc
.ipynb_checkpoints/
data/interim/
results/**/samples/
results/**/*.pdb
results/**/*.cif
# The variant ledger binary is git-ignored (unmergeable across agents);
# the git-shared form is db/exports/*.csv + coordination/manifests/*.tsv.
EOF

# ---------------- 3. config stubs ----------------
write_if_absent "$ROOT/configs/objective.yaml" <<'EOF'
# objective.yaml — locked design objective (see CLAUDE.md §2, decision D-001)
target_antibody: "lecanemab (Leqembi / BAN2401); humanized mAb158 IgG1"
optimize_for: "avidity-adjusted affinity for Aβ protofibrils/oligomers"
preserve_or_improve:
  - selectivity vs Aβ monomer
  - selectivity vs fixed-N-terminus / CAA-type Aβ40 fibrils
  - developability (stability, aggregation, viscosity)
  - humanness
do_not_optimize: "raw monovalent KD to the Aβ N-terminal epitope"
target_species:
  primary: "Aβ42 protofibril / fibril (type I, type II, Arctic)"
counter_targets:
  - "Aβ monomer / peptide"
  - "fixed-N-terminus / CAA-type Aβ40 fibril"
internal_structures: [9CO4, 9CKI, 5MY4]
decisions: [D-001, D-002, D-003, D-004, D-005, D-006]
notes: >
  Epitope register is uncertain (OQ-1); structure-based steps use a pose
  ensemble, not a single docked complex (D-002).
EOF

write_if_absent "$ROOT/configs/metrics.yaml" <<'EOF'
# metrics.yaml — success metrics (CLAUDE.md §2). All deltas are vs WT lecanemab.
# Thresholds marked TODO must be set WITH a recorded rationale (docs/decisions/)
# before they are used as gates — do not invent cutoffs.
reference: lecanemab_WT
metrics:
  - id: M1_affinity
    stage: 5
    definition: "multi-sample Boltz-2/AF3 ipTM + ipSAE on Fv–protofibril complex"
    comparator: ">= WT (consensus improvement on >=2 independent scorers)"
    threshold: TODO
    source: R-MOSAIC
  - id: M2_selectivity_monomer
    stage: 6
    definition: "Δprotofibril - Δmonomer"
    comparator: "> 0 AND >= WT"
    threshold: TODO
    source: R-ANA
  - id: M2b_selectivity_cafibril
    stage: 6
    definition: "Δprotofibril - ΔCAA-fibril"
    comparator: "> 0 AND >= WT"
    threshold: TODO
    source: R-TG
  - id: M3_developability
    stage: 6
    definition: "TAP flags, Aggrescan3D, NetSolP, viscosity"
    comparator: "no new liabilities vs WT"
    threshold: TODO
    source: R-AMTRADE
  - id: M4_humanness
    stage: 6
    definition: "BioPhi OASis percentile"
    comparator: ">= WT"
    threshold: TODO
  - id: M5_experimental
    stage: 8
    definition: "BLI/SPR KD/koff to protofibril; monomer counter-screen"
    comparator: "improved vs WT AND monomer screen negative"
    threshold: TODO
    source: R-YSD
EOF

# ---------------- 4. cluster detection helper + portable SLURM ----------------
write_if_absent "$ROOT/scripts/_detect_cluster.sh" <<'EOF'
#!/usr/bin/env bash
# Detect the current cluster and source its env file.
# Usage:  source scripts/_detect_cluster.sh   (sets $CLUSTER and exports env vars)
_REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
case "$(hostname -f 2>/dev/null || hostname)" in
  *frontenac*|frnt*) CLUSTER=frontenac ;;   # COORDINATOR
  *nibi*)            CLUSTER=nibi ;;         # worker (when activated)
  *narval*)          CLUSTER=narval ;;       # worker (when activated)
  *) echo "ERROR: unknown cluster: $(hostname -f 2>/dev/null || hostname)" >&2; return 1 2>/dev/null || exit 1 ;;
esac
export CLUSTER
# shellcheck disable=SC1090
source "${_REPO_ROOT}/clusters/${CLUSTER}.env"
EOF

write_if_absent "$ROOT/slurm/_template.sbatch" <<'EOF'
#!/bin/bash
#SBATCH --job-name=lecam
#SBATCH --output=%x-%A_%a.out
# Frontenac defaults below; other clusters override via clusters/<cluster>.env.
#SBATCH --account=def-hpcg6049_gpu     # Frontenac default
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8              # tune per tool
#SBATCH --mem=48G                      # tune per tool
#SBATCH --time=08:00:00                # tune per stage (workers may allow longer)
# NO --partition flag on Frontenac
# module load ...                      # CONFIRM module names per cluster before first submit
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"   # sets $CLUSTER + sources clusters/$CLUSTER.env
# conda activate "$CONDA_ENV_MAIN" (or stage-specific env), then run the stage script.
# Always write results/<stage>/<run-id>/manifest.json (inputs, versions, seeds, job id).
EOF

# ---------------- 5. DuckDB variant ledger ----------------
write_if_absent "$ROOT/db/schema.sql" <<'EOF'
-- variant ledger (single source of truth on the coordinator).
-- The binary .duckdb is git-ignored; the git-shared form is db/exports/*.csv.
CREATE TABLE IF NOT EXISTS variants (
  variant_id        TEXT PRIMARY KEY,   -- e.g. LEC-AM-T1-0042
  parent            TEXT,               -- 'lecanemab_WT'
  track             TEXT,               -- T1 | T2 | T3 | T4
  chain             TEXT,               -- HC | LC | both
  mutations         TEXT,               -- 'HC:Y32F;LC:S56T' (IMGT numbering)
  n_mut             INTEGER,
  edit_dist_to_wt   INTEGER,
  cluster           TEXT,               -- which cluster produced/scored it
  -- Stage 5 (affinity, vs WT)
  boltz_iptm        DOUBLE,
  boltz_ipsae       DOUBLE,
  af3_iptm          DOUBLE,
  flexddg_kcal      DOUBLE,
  consensus_rank    INTEGER,
  -- Stage 6 (selectivity + developability)
  sel_monomer_delta DOUBLE,             -- Δprotofibril - Δmonomer  (want >0, >= WT)
  sel_cafib_delta   DOUBLE,             -- Δprotofibril - ΔCAA-fibril
  oasis_humanness   DOUBLE,
  agg3d_score       DOUBLE,
  netsolp           DOUBLE,
  viscosity_flag    BOOLEAN,
  tap_flags         TEXT,
  -- Stage 8 (experimental)
  kd_protofibril_M  DOUBLE,
  koff_protofibril  DOUBLE,
  monomer_screen    TEXT,               -- 'negative' (desired) | 'positive'
  -- provenance
  stage_reached     INTEGER,
  status            TEXT,               -- generated|scored|gated|rejected|tested|hit
  source_config     TEXT,
  created_at        TIMESTAMP
);
EOF

DB="$ROOT/db/variants.duckdb"
SCHEMA="$ROOT/db/schema.sql"
if [[ $DRY_RUN -eq 1 ]]; then
  log "[dry-run] would apply schema → $DB"
elif command -v duckdb >/dev/null 2>&1; then
  duckdb "$DB" < "$SCHEMA" && log "ledger initialized (duckdb CLI): $DB"
elif python -c "import duckdb" >/dev/null 2>&1; then
  python -c "import duckdb; c=duckdb.connect('$DB'); c.execute(open('$SCHEMA').read()); c.close()" \
    && log "ledger initialized (python duckdb): $DB"
else
  log "WARN: no duckdb CLI and python 'duckdb' not importable."
  log "      schema written to $SCHEMA — apply after creating the 'lecam' env (--with-envs)."
fi

# ---------------- 6. clusters/ scaffold ----------------
write_if_absent "$ROOT/clusters/frontenac.env" <<'EOF'
# Frontenac (CAC, Queen's) — COORDINATOR
CLUSTER_NAME="frontenac"
CLUSTER_ROLE="coordinator"
# Paths
PROJECT_ROOT="/global/project/hpcg6049/lecanemab-am"
SCRATCH_ROOT="/global/scratch/hpc6049/lecanemab-am"
# SLURM (NO --partition on Frontenac)
SLURM_ACCOUNT="def-hpcg6049_gpu"
GPU_TYPE="a100"
GPU_GRES="gpu:a100:1"
MAX_WALLTIME="08:00:00"          # tune per job
MAIN_MEM="48G"
# Conda envs (canonical names on this cluster)
CONDA_ENV_MAIN="lecam"
CONDA_ENV_AB="lecam-ab"
CONDA_ENV_FOLD="lecam-fold"
CONDA_ENV_DESIGN="lecam-design"
CONDA_ENV_ROSETTA="lecam-rosetta"
CONDA_ENV_MD="lecam-md"
CONDA_ENV_DEV="lecam-dev"
# Containers
CONTAINER_DIR="${PROJECT_ROOT}/container"
# Globus
GLOBUS_ENDPOINT="CONFIRM"        # Frontenac personal endpoint UUID
GLOBUS_BASE_PATH="${PROJECT_ROOT}"
EOF

write_if_absent "$ROOT/clusters/narval.env" <<'EOF'
# Narval (Calcul Québec / DRAC) — WORKER (activate when hired)
CLUSTER_NAME="narval"
CLUSTER_ROLE="worker"
PROJECT_ROOT="CONFIRM"           # e.g. /home/<user>/projects/def-ghaedi/<user>/lecanemab-am
SCRATCH_ROOT="CONFIRM"           # e.g. /scratch/<user>/lecanemab-am
SLURM_ACCOUNT="def-ghaedi"       # confirm allocation for THIS project
GPU_TYPE="a100"
GPU_GRES="gpu:a100:1"
MAX_WALLTIME="6-23:00:00"
MAIN_MEM="64G"
CONDA_ENV_MAIN="lecam"           # names may differ; confirm on cluster
CONTAINER_DIR="${PROJECT_ROOT}/container"
APPTAINER_MODULE="apptainer"
GLOBUS_ENDPOINT="a1713da6-098f-40e6-b3aa-034efe8b6e5b"   # Narval institutional (confirm still valid)
GLOBUS_BASE_PATH="${PROJECT_ROOT}"
# Scratch purge ~60 days — touch files monthly.
EOF

write_if_absent "$ROOT/clusters/nibi.env" <<'EOF'
# Nibi (DRAC) — WORKER (activate when hired)
CLUSTER_NAME="nibi"
CLUSTER_ROLE="worker"
PROJECT_ROOT="CONFIRM"
SCRATCH_ROOT="CONFIRM"
SLURM_ACCOUNT="CONFIRM"
GPU_TYPE="CONFIRM"               # e.g. h100 / a100
GPU_GRES="CONFIRM"
MAX_WALLTIME="CONFIRM"
MAIN_MEM="64G"
CONDA_ENV_MAIN="lecam"
CONTAINER_DIR="${PROJECT_ROOT}/container"
APPTAINER_MODULE="apptainer"
GLOBUS_ENDPOINT="CONFIRM"
GLOBUS_BASE_PATH="${PROJECT_ROOT}"
EOF

write_if_absent "$ROOT/clusters/_cluster.env.template" <<'EOF'
# <Cluster> (<Institution>) — <coordinator|worker>
CLUSTER_NAME="<cluster>"
CLUSTER_ROLE="<coordinator|worker>"
PROJECT_ROOT="<abs path to repo on this cluster>"
SCRATCH_ROOT="<scratch path>"
SLURM_ACCOUNT="<allocation>"
GPU_TYPE="<a100|h100|v100>"
GPU_GRES="gpu:<type>:1"
MAX_WALLTIME="<max walltime>"
MAIN_MEM="64G"
CONDA_ENV_MAIN="<env>"
CONTAINER_DIR="${PROJECT_ROOT}/container"
GLOBUS_ENDPOINT="<endpoint UUID>"
GLOBUS_BASE_PATH="${PROJECT_ROOT}"
EOF

write_if_absent "$ROOT/clusters/frontenac/CLAUDE.md" <<'EOF'
# Frontenac — Coordinator (Agent F)

You are on **Frontenac**. You are the **central coordinator** for lecanemab-am.

## Coordinator responsibilities
1. Assign work to worker clusters via `coordination/manifests/` and `coordination/inbox/<worker>/` (exact command, thresholds, output path).
2. Update `coordination/DASHBOARD.md` (summary lines + the Frontenac row) each session.
3. Merge worker results into the DuckDB ledger; keep it the single source of truth; export `db/exports/variants.csv`.
4. Make campaign decisions with the PI (proceed/hold/reassign); log ADRs in `docs/decisions/`.
5. Maintain `PROJECT_STATUS.md` + `HANDOFF.md`.

## Do NOT
- Start sessions on other clusters (the PI does this manually).
- Transfer large files inline (Globus is a separate manual step).

## HPC details
Source `clusters/frontenac.env`.
- GPU account: `def-hpcg6049_gpu` (MUST specify)
- **Never** specify `--partition` — scheduler auto-routes
- Primary GPU: A100-PCIE-40GB
- Project root `/global/project/hpcg6049/lecanemab-am` ; scratch `/global/scratch/hpc6049/lecanemab-am`
EOF

write_if_absent "$ROOT/clusters/_worker_CLAUDE.template.md" <<'EOF'
# <Cluster> — Worker (Agent <Cluster>)

You are on **<Cluster>**. You are a **worker agent** coordinated from Frontenac.

## Worker responsibilities
1. `git pull origin main` at session start; read `coordination/DASHBOARD.md` + your inbox.
2. Execute the assigned task EXACTLY (inbox message or manifest).
3. Commit small results (CSVs, status, scored ledger-row CSVs) to git; push with a `[<cluster>]` prefix.
4. Move large data to the coordinator via Globus.
5. Delete inbox messages after actioning them.

## Do NOT
- Make campaign decisions or change parameters/configs without coordinator approval.
- Edit other clusters' DASHBOARD rows.

## HPC details
Source `clusters/<cluster>.env` (account, GRES, walltime, env names, Globus). Confirm module names before first submit.
EOF

write_if_absent "$ROOT/clusters/README.md" <<'EOF'
# clusters/ — per-cluster config & how to add a worker

Each cluster has `clusters/<name>.env` (sourceable paths/SLURM/Globus) and
`clusters/<name>/CLAUDE.md` (agent role). Scripts detect the cluster via
`scripts/_detect_cluster.sh` and source the right `.env`.

## Activate a new worker (~5 min)
1. `cp clusters/_cluster.env.template clusters/<name>.env` and fill it in (CONFIRM all paths/accounts).
2. `mkdir -p clusters/<name> && cp clusters/_worker_CLAUDE.template.md clusters/<name>/CLAUDE.md` (set <Cluster>).
3. `mkdir -p coordination/inbox/<name> && touch coordination/inbox/<name>/.gitkeep`.
4. Add a row for <name> in `coordination/DASHBOARD.md` and the registry in `coordination/COORDINATION.md`.
5. Add the hostname pattern to the `case` in root `CLAUDE.md` §0 AND `scripts/_detect_cluster.sh`.
6. Add the Globus endpoint to `coordination/globus/endpoints.md`.
7. On the worker: clone `git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git`; run `hostname -f` to verify detection.

Candidates (from the lab's prior bispecific project): **Narval**, **Nibi** — env stubs present, marked CONFIRM.
EOF

# ---------------- 7. coordination/ scaffold ----------------
write_if_absent "$ROOT/coordination/COORDINATION.md" <<'EOF'
# Multi-Cluster Coordination Protocol — lecanemab-am

**Coordinator:** Frontenac (Agent F). **This repo is the only channel.**

## Agent registry
| Agent | Cluster | Role | Working dir | GPU | Status |
|---|---|---|---|---|---|
| F | Frontenac | coordinator | /global/project/hpcg6049/lecanemab-am | A100-40GB | ACTIVE |
| Narval | Narval | worker | CONFIRM | A100 | not activated |
| Nibi | Nibi | worker | CONFIRM | CONFIRM | not activated |

## Communication
1. Coordinator pushes instructions/status to `main`.
2. Workers pull `main` at session start, execute, commit results, push.
3. Large data via Globus (not git) — see `globus/`.

## Commit convention
Prefix every commit with the cluster: `[frontenac] ...`, `[narval] ...`, `[nibi] ...`.

## Conflict avoidance
Each cluster edits ONLY its own DASHBOARD row + its own inbox + its own manifest;
the coordinator edits the summary lines. Resolve DASHBOARD merge conflicts by keeping
both rows and the most recent "Last updated" line.

## Rules for all agents
1. Pull before work; push after.
2. Use ONLY provided settings/configs — no changes without coordinator approval.
3. Scripts use `set -euo pipefail`, absolute paths, and `source clusters/<cluster>.env`.
4. Log all SLURM job IDs in DASHBOARD.md.
5. Variants live in the DuckDB ledger (single source of truth, on the coordinator).
   Workers report rows as CSV; the coordinator merges and re-exports `db/exports/variants.csv`.
   The binary `.duckdb` is git-ignored (unmergeable across agents).
EOF

write_if_absent "$ROOT/coordination/DASHBOARD.md" <<'EOF'
# Campaign Dashboard — lecanemab-am

**Last updated:** 2026-05-30 by frontenac — Phase 0 scaffold created; no jobs running.

## Cluster status
| Cluster | Agent | Current work | SLURM jobs | Last update |
|---|---|---|---|---|
| Frontenac | F | Phase 0 provisioning | — | 2026-05-30 |
| Narval | Narval | not activated | — | — |
| Nibi | Nibi | not activated | — | — |

## Recent actions
| Date | Agent | Action |
|---|---|---|
| 2026-05-30 | frontenac | Repo scaffold + coordination layer created |
EOF

write_if_absent "$ROOT/coordination/inbox/README.md" <<'EOF'
# Agent Inbox System

Inter-agent messaging via git. Each agent has an inbox directory.

## Protocol
1. To send a message: write a `.md` file in `inbox/<recipient>/`.
2. Commit with a `[<sender>] msg: <subject>` prefix and push.
3. The recipient picks it up on the next `git pull`.
4. The recipient DELETES the file after reading and commits (delete on read, always).

## Filename
`YYYY-MM-DD_from-<sender>_<subject-slug>.md`

## Message template
```
# Message from <Sender>

**Date:** YYYY-MM-DD
**From:** <sender cluster>
**To:** <recipient cluster>
**Subject:** <one-line summary>

---

<body — be specific: exact command, thresholds, and output paths>
```
EOF

write_if_absent "$ROOT/coordination/manifests/README.md" <<'EOF'
# Manifests — batch work assignments

For batch work (e.g. score N variants × M targets), the coordinator writes a TSV
assigning tasks to a cluster. Workers update `status` pending → complete | failed.

## Format — manifest_stage<N>_<cluster>.tsv
```tsv
variant_id           target            cluster   status
LEC-AM-T1-0042       abeta_protofibril narval    pending
LEC-AM-T1-0042       abeta_monomer     narval    pending
LEC-AM-T1-0042       caa_fibril        narval    pending
```

Use manifests only for concrete parallelizable lists; use inbox messages for
instructions/decisions/questions.
EOF

write_if_absent "$ROOT/coordination/globus/endpoints.md" <<'EOF'
# Globus endpoints — lecanemab-am

Large files (PDBs, model weights, MD/diffusion samples, containers) move via Globus, NOT git.

| Cluster   | Endpoint UUID | Type          | Base path |
|-----------|---------------|---------------|-----------|
| Frontenac | CONFIRM       | personal      | /global/project/hpcg6049/lecanemab-am |
| Narval    | a1713da6-...  | institutional | CONFIRM (.../lecanemab-am) |
| Nibi      | CONFIRM       | institutional | CONFIRM (.../lecanemab-am) |

Initiate transfers via the `globus transfer` CLI or web UI; store reusable
commands in `transfer_recipes.sh`.
EOF

write_if_absent "$ROOT/coordination/globus/transfer_recipes.sh" <<'EOF'
#!/usr/bin/env bash
# Reusable Globus transfer recipes for lecanemab-am. Fill endpoint UUIDs from endpoints.md.
# Requires: globus-cli (`pip install globus-cli`; `globus login`).
set -euo pipefail

FRONTENAC_EP="CONFIRM"
NARVAL_EP="a1713da6-098f-40e6-b3aa-034efe8b6e5b"   # confirm
NIBI_EP="CONFIRM"

# Example: push antigen templates Frontenac -> Narval
# globus transfer "$FRONTENAC_EP:/global/project/hpcg6049/lecanemab-am/data/raw/antigen" \
#                 "$NARVAL_EP:<narval lecanemab-am path>/data/raw/antigen" \
#                 --recursive --label "antigen->narval"

# Example: pull worker model samples Narval -> Frontenac
# globus transfer "$NARVAL_EP:<path>/results" \
#                 "$FRONTENAC_EP:/global/scratch/hpc6049/lecanemab-am/results" \
#                 --recursive --label "narval-results->frontenac"
echo "Edit this file with concrete endpoint UUIDs + paths before use."
EOF

# ---------------- 8. docs stubs ----------------
write_if_absent "$ROOT/docs/sources/README.md" <<'EOF'
# docs/sources/ — load-bearing source extracts

Store the EXACT supporting sentence(s) (not just URLs) for every biological
claim and every threshold, so each is traceable (CLAUDE.md §8).

Keys map to CLAUDE.md §11:
- B1 R-NMR   : humanized mAb158, protofibril-selective
- B2 R-ANA   : >10^6-fold protofibril vs Aβ1-16 monomer selectivity
- B3 R-TG/SD : conformational N-terminal epitope; requires flexible N-terminus
- B4 R-TG    : spares fixed-N-terminus / CAA Aβ40 fibrils (low ARIA-E link)
- B5 R-ELIFE/R-REV : no public co-structure; modeled via D3 (5MY4)
- B6         : epitope register uncertainty (internal hotspots vs lit)
- B7 R-HEXA  : multivalency raises aggregate binding (Hexa-RmAb158)

One file per claim: e.g. B2_selectivity.md (quote + citation + URL + date).
EOF

write_if_absent "$ROOT/docs/env/README.md" <<'EOF'
# docs/env/ — environment provisioning

Pin exact versions + git commit hashes here after install (CLAUDE.md §5/§8).
`00_init.sh --with-envs` creates the `lecam` base env fully and the others as
SHELLS only — several tools need manual / licensed / container installs.
Env names may differ per cluster — the canonical name is in clusters/<cluster>.env.

| env            | install method        | core tools |
|----------------|-----------------------|------------|
| lecam          | pip/conda (automated) | duckdb, pandas, biopython, pyyaml, ANARCI* |
| lecam-ab       | pip/conda             | ImmuneBuilder, IgFold, AbLang2, AntiBERTy, BioPhi/Sapiens |
| lecam-fold     | pip + WEIGHTS         | Boltz-2, Chai-1  (AlphaFold3 = CONTAINER) |
| lecam-design   | repo installs         | ProteinMPNN, SolubleMPNN, LigandMPNN, ColabDesign, BindCraft, RFantibody |
| lecam-rosetta  | LICENSED              | PyRosetta, Rosetta flex_ddG, AbLIFT, FoldX |
| lecam-md       | conda                 | OpenMM (and/or GROMACS), AlphaFlow (opt) |
| lecam-dev      | mixed                 | Aggrescan3D, NetSolP, SoluProt, TAP/SAbDab-TAP, DeepViscosity, DE-STRESS |

*ANARCI needs HMMER; install via conda (confirm).

## Manual / licensed / container checklist (do NOT guess install commands)
- [ ] PyRosetta license + install
- [ ] FoldX license + binary
- [ ] AlphaFold3 container + model params (access-gated)
- [ ] Boltz-2 + Chai-1 model weights
- [ ] RFantibody + BindCraft repos + weights (isolate envs)
- [ ] Confirm CUDA/cuDNN + module names per cluster (Frontenac A100; workers TBD)
EOF

# ---------------- 9. conda env shells (optional) ----------------
if [[ $WITH_ENVS -eq 1 ]]; then
  CONDA="$(command -v mamba || command -v conda || true)"
  if [[ -z "$CONDA" ]]; then
    log "WARN: conda/mamba not found; skipping env creation."
  else
    log "using conda binary: $CONDA"
    run "$CONDA create -y -n lecam python=$PYVER"
    run "$CONDA run -n lecam pip install duckdb pandas biopython pyyaml"
    for e in lecam-ab lecam-fold lecam-design lecam-rosetta lecam-md lecam-dev; do
      run "$CONDA create -y -n $e python=$PYVER"
    done
    log "env shells created. Populate per docs/env/README.md (licensed/container tools are NOT auto-installed)."
  fi
fi

# ---------------- 10. provisioning manifest ----------------
if [[ $DRY_RUN -eq 0 ]]; then
  MDIR="$ROOT/results/_provisioning/$TS"; mkdir -p "$MDIR"
  GIT_SHA="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo no-git)"
  cat > "$MDIR/manifest.json" <<EOF
{
  "step": "phase0_init",
  "timestamp": "$TS",
  "root": "$ROOT",
  "git_remote": "$GIT_REMOTE",
  "git_branch": "$GIT_BRANCH",
  "git_sha": "$GIT_SHA",
  "with_envs": $WITH_ENVS,
  "python": "$PYVER",
  "dry_run": $DRY_RUN
}
EOF
  log "manifest: $MDIR/manifest.json"
fi

# ---------------- 11. self-install into scripts/stage1_inputs/ ----------------
SELF="$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")"
DEST="$ROOT/scripts/stage1_inputs/00_init.sh"
if [[ "$SELF" != "$DEST" && ! -e "$DEST" && $DRY_RUN -eq 0 ]]; then
  cp "$SELF" "$DEST"; chmod +x "$DEST"; log "copied self → $DEST"
fi

# ---------------- next steps ----------------
cat <<'NEXT'

[init] DONE (Phase 0). Next:
  A. Push to GitHub:
       git add -A && git commit -m "[frontenac] Phase 0: scaffold + coordination layer"
       git push -u origin main
  B. Stage 1 (Frontenac):
       1. Source + verify lecanemab VH/VL (Thera-SAbDab / IMGT / WHO-INN / patent, >=2 sources)
            -> data/raw/lecanemab_fv.fasta ; number with ANARCI (IMGT/Kabat/Chothia)
       2. Collect antigen templates -> data/raw/antigen/
            target: Aβ42 protofibril/fibril (type I/II/Arctic)
            counter-targets: Aβ monomer/peptide + fixed-N / CAA-type Aβ40 fibril
            internal: 9CO4, 9CKI, 5MY4
       3. Fill docs/sources/ (B1–B7); set metrics.yaml thresholds once WT baseline exists.
       4. Update coordination/DASHBOARD.md + PROJECT_STATUS.md + HANDOFF.md.
  C. To hire a worker later: see clusters/README.md (Narval/Nibi stubs are ready, marked CONFIRM).
NEXT
