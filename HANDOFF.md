# HANDOFF.md — lecanemab-am

Coordinator (Frontenac) session-to-session state for the **git-coordinated, multi-cluster** loop. **Update at the END of every working session.** This complements `coordination/DASHBOARD.md` (live cross-cluster status); HANDOFF is the coordinator's continuity log.

**Read order for a new session:** `git pull` → `CLAUDE.md` (incl. §0) → `clusters/<cluster>/CLAUDE.md` → `coordination/DASHBOARD.md` → `coordination/COORDINATION.md` → `PROJECT_STATUS.md` → `DEVELOPMENT_PLAN.md` → `HANDOFF.md` (this file).

---

## Resume here (next action)

**Phase / Stage:** Phase 0 (scaffold+ledger+`lecam` done) → Stage 1 (research deliverables done; only metrics thresholds remain for the gate)

**Env note:** `conda activate lecam`; **always set `PYTHONNOUSERSITE=1`** (a py3.12 pydantic in `~/.local` leaks into conda's plugin loader → noisy `anaconda-cloud-auth`/GLIBC warnings; harmless, just suppress). Env built from **conda-forge/bioconda** (NOT the CC wheelhouse — glibc 2.28 mismatch, D-007). Versions pinned in `docs/env/lecam.versions.txt`.

**Next commands (Frontenac):**
```bash
cd /global/project/hpcg6049/lecanemab-am
git pull origin main
# OPEN DECISION (OQ-7): expand epitope-homology template set (6CO3/5CSZ/3BKJ/3D6) +
#                       demote 5MY4 (= anti-pyroGlu Fab c#17, NOT D3) to weak proxy? -> PI sign-off.
# DONE 2026-06-03: monomer template = 1Z0Q (D-009); antigen coords fetched to data/raw/antigen/coords/
#                  (fetch_antigen_templates.sh, git-ignored); B5 D3/5MY4 sentence pinned + caveat.
# Stage 1 leftover: set configs/metrics.yaml thresholds once a Stage-2 WT baseline exists.
# Phase 0 finish: MAP existing envs (colabfold/mpnn/rfdiffusion/rfd_clean/BindCraft/SE3nv already exist)
#                 to lecam-* roles; build only what's missing; A100 smoke tests; confirm SLURM modules.
# Stage 2 start: Fv model (ImmuneBuilder/IgFold) + multi-seed co-fold vs protofibril epitope.
```
Re-run Fv numbering anytime: `PYTHONNOUSERSITE=1 conda run -n lecam python scripts/stage1_inputs/number_fv.py`.

---

## In-flight jobs

_None yet._

| SLURM job id | Stage / step | Submitted | Outputs → | Status |
|---|---|---|---|---|
| — | — | — | — | — |

---

## Paste-back template (fill after each run, paste into chat)

```
STAGE / STEP:
RUN-ID (results/<stage>/<id>):
SLURM JOB ID + EXIT STATUS:
WHAT RAN (tool + env + config path):
KEY NUMBERS (metrics / counts / KD vs WT):
OUTPUT PATHS:
MANIFEST PATH:
LOG TAIL (last ~20 lines / any errors):
ANOMALIES / DEVIATIONS FROM PLAN:
```

On paste-back, Claude will: interpret → update the DuckDB ledger → update `PROJECT_STATUS.md` (status + decision log) → draft the next prompt.

---

## Awaiting decision (needs data first)

- **OQ-1** epitope register → resolve at Stage 2 via the pose ensemble (do not pre-commit a register).
- **OQ-2** display platform (yeast vs phage) + protofibril reagent prep → needed before Stage 8.
- **OQ-3** avidity-adjusted-affinity metric definition → before Stage 6.
- **metrics.yaml `TODO` thresholds** → set (with rationale → `docs/decisions/`) once the Stage-2 WT baseline scores exist.

---

## Gotchas / environment notes

- SLURM (Frontenac): `--account=def-hpcg6049_gpu --gres=gpu:a100:1`, **no `--partition`**. Other clusters: source `clusters/<cluster>.env`.
- **Confirm CUDA/module names per cluster** before first submit — placeholder in `slurm/_template.sbatch`.
- AF3 / Boltz-2 / RFantibody / BindCraft → isolated envs/containers; **PyRosetta + FoldX need licenses** (see `docs/env/README.md`).
- Boltz/AF3 diffusion is stochastic → fixed seeds + multi-sample; **store all samples**.
- Do **not** rank by unnormalized ESM2 pseudo-log-likelihood (guardrail 4).
- Storage: working data on `/global/scratch/hpc6049/lecanemab-am`; repo + curated inputs/results on `/global/project/hpcg6049/lecanemab-am`.
- **git is the channel:** small files only; PDBs/weights/samples via Globus (`coordination/globus/`). Commit prefix `[<cluster>]`; push to `origin main`.
- **Adding a worker:** copy `clusters/_cluster.env.template` → `clusters/<name>.env`, `clusters/_worker_CLAUDE.template.md` → `clusters/<name>/CLAUDE.md`, add inbox dir + DASHBOARD row, clone repo on that cluster, verify hostname detection (`clusters/README.md`).

---

## Session log (most recent first)

### 2026-06-03 — Stage-1/2 prep: monomer template + antigen coords + 5MY4 discrepancy
- **D-009:** Aβ-monomer counter-target resolved — **1Z0Q** (Aβ42 aqueous NMR, 30 models) primary; **1IYT rejected** (RCSB citation: solved "in an apolar microenvironment" → helical); **2LFM** (Aβ40) kept as Aβ40-matched control. All RCSB-grounded (no memory-typing). ADR → `docs/decisions/D-009-...md`.
- **Antigen coords fetched:** new idempotent `scripts/stage1_inputs/fetch_antigen_templates.sh` pulled 10 mmCIFs (targets 9CO4/7Q4B/7Q4M/8BFZ; counters 9CKI/8QN7/8OLN/1Z0Q/2LFM; ref 5MY4) → `data/raw/antigen/coords/` (git-ignored; `.gitignore` updated; manifest in `coords/fetch_manifest.tsv`).
- **5MY4 discrepancy (OQ-7):** verified via RCSB that PDB **5MY4 = anti-pyroglutamate-Aβ Fab "c#17" (pE3-12 epitope), NOT antibody "D3"** as R-ELIFE/CLAUDE.md B5 state. Our B5 faithfully quotes R-ELIFE (now **pinned**), but 5MY4 is a weak/indirect homology proxy. Proposed (PI sign-off): add full-length N-terminal anti-Aβ Fab co-structures (aducanumab 6CO3, gantenerumab 5CSZ, 3D6/bapineuzumab, WO2 3BKJ) to the pose ensemble; demote 5MY4. **Did NOT change CLAUDE.md/B5 or campaign params** — only annotated + opened OQ-7.
- **Next:** PI call on OQ-7 → Phase-0 env mapping → Stage 2.

### 2026-06-01 — Phase 0 executed + Stage 1 research
- Ran `00_init.sh` (real): repo tree, git repo + remote (SSH auth OK as `hamidghaedi`), coordination scaffold, `db/schema.sql`.
- **Env:** CC wheelhouse wheels (`+computecanada`, glibc 2.29/2.30) fail on login-node glibc 2.28 → rebuilt `lecam` from **conda-forge/bioconda** (D-007). All compiled imports + ANARCI + HMMER verified. Versions → `docs/env/lecam.versions.txt`. Relaxed `.claude/settings.json` deny-list to allow installs.
- **Ledger:** initialized `db/variants.duckdb` (`variants`, 27 cols). NB: apply schema via whole-file `con.execute()`, not naive `;`-split (a `;` lives inside a comment).
- **Stage 1:** Fv verified KEGG D11678 ↔ patent US9573994B2 (D-008) → `lecanemab_fv.fasta`; ANARCI 3-scheme numbering + CDR/Vernier map; antigen template IDs; B1–B7 sentences (B2/B5 exact quotes paywalled-TODO).
- **Next:** see Resume block. Metrics thresholds + monomer template are the open Stage-1/2 items.

### 2026-05-30 — inception
- Authored `CLAUDE.md` (incl. §0 multi-cluster protocol), `PROJECT_STATUS.md`, `DEVELOPMENT_PLAN.md`, `HANDOFF.md`, and `scripts/stage1_inputs/00_init.sh` (extended to scaffold `clusters/` + `coordination/` and set the git remote).
- Locked the objective (avidity + selectivity, **not** monovalent KD) and the 8-stage plan; recorded D-001…D-005, plus **D-006** (multi-cluster git-coordination, Frontenac coordinator).
- Set project root `/global/project/hpcg6049/lecanemab-am` and GitHub remote `MaryamTabasinezhad/Lecanemab_affinity_maturation` (branch `main`).
- **Next:** run `00_init.sh`, push to GitHub, then source the Fv + antigen templates (Stage 1).
