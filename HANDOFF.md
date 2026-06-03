# HANDOFF.md — lecanemab-am

Coordinator (Frontenac) session-to-session state for the **git-coordinated, multi-cluster** loop. **Update at the END of every working session.** This complements `coordination/DASHBOARD.md` (live cross-cluster status); HANDOFF is the coordinator's continuity log.

**Read order for a new session:** `git pull` → `CLAUDE.md` (incl. §0) → `clusters/<cluster>/CLAUDE.md` → `coordination/DASHBOARD.md` → `coordination/COORDINATION.md` → `PROJECT_STATUS.md` → `DEVELOPMENT_PLAN.md` → `HANDOFF.md` (this file).

---

## Resume here (next action)

**Phase / Stage:** Phase 0 envs done → **Stage 2 in progress** (2.1 WT Fv model + 2.2 Boltz-2 co-fold vs Aβ1-16 done — WT baseline iptm 0.961±0.019 measured). Next: 2.4 pose-cluster + epitope-register check (Stage-2 gate, OQ-1) + ipSAE; 2.3 MD ensemble (needs lecam-md). metrics.yaml now has the WT baseline (M1); threshold still a decision.

**Env note:** `conda activate lecam`; **always set `PYTHONNOUSERSITE=1`** (a py3.12 pydantic in `~/.local` leaks into conda's plugin loader → noisy `anaconda-cloud-auth`/GLIBC warnings; harmless, just suppress). Env built from **conda-forge/bioconda** (NOT the CC wheelhouse — glibc 2.28 mismatch, D-007). Versions pinned in `docs/env/lecam.versions.txt`.

**Next commands (Frontenac):**
```bash
cd /global/project/hpcg6049/lecanemab-am
git pull origin main
# DONE 2026-06-03: monomer template = 1Z0Q (D-009); antigen coords fetched to data/raw/antigen/coords/
#                  (fetch_antigen_templates.sh, git-ignored); B5 D3/5MY4 sentence pinned + caveat.
# DONE 2026-06-03: OQ-7 resolved (D-010) -> homology set 6CO3/5CSZ/3BKJ/4HIX; 5MY4 = weak proxy.
# Stage 1 leftover: set configs/metrics.yaml thresholds once a Stage-2 WT baseline exists.
# DONE 2026-06-03: envs mapped; lecam-ab + lecam-fold(Boltz-2) + lecam-chai(Chai-1) built, weights cached.
# DONE 2026-06-03: Boltz-2 A100 smoke test PASSED (job 11542978, ptm 0.909); R-MODULES resolved
#                 (no --partition, no CUDA module; A100 driver 595.58). sbatch: slurm/smoke_boltz2.sbatch.
# Phase 0 remaining = BUILDS: lecam-dev (developability), AF3 container, dedicated lecam-rosetta (flex_ddG/FoldX)/-md;
#                 +RFantibody/LigandMPNN; BioPhi/Sapiens (own env).
#                 Remaining smoke tests: Chai-1, ColabFold, RFdiffusion, BindCraft (pattern: copy smoke_boltz2.sbatch).
# PIP ON FRONTENAC (every env): env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null conda run -n <env> \
#                 pip install --index-url https://pypi.org/simple ...   (CC wheelhouse + _manylinux shim else break wheels)
# DONE 2026-06-03: Stage 2.1 WT Fv model (ABodyBuilder2) -> results/stage2/fv-wt-20260603/ + data/interim/fv_model.pdb.
#                 RUN compiled-dep envs with: env -u PYTHONPATH PYTHONNOUSERSITE=1 \
#                   LD_LIBRARY_PATH=/global/home/hpc6049/.conda/envs/<env>/lib conda run -n <env> python ...
# DONE 2026-06-03: Stage 2.2 Boltz-2 co-fold WT Fv + Aβ1-16 (job 11544623): 25 samples,
#                 iptm 0.961±0.019 -> results/stage2/cofold-wt-Abeta1-16-11544623/ (samples on scratch).
#                 Reusable: slurm/stage2_cofold.sbatch + scripts/stage2_model/aggregate_cofold.py.
# Stage 2 next: 2.4 cluster the 25 poses (Fv-Aβ contacts) + epitope-register check vs B6 hotspots
#               (Y10/E11/H13/H14/Q15/K16) and lit "tolerant 3-7" -> pose_hypotheses.json; this is the
#               Stage-2 GATE (self-consistent pose family, B3-consistent, not contradicting B6) + OQ-1.
#               Compute ipSAE from PAE. 2.3 MD/AlphaFlow ensemble (needs lecam-md — not built).
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

### 2026-06-03 (g) — Stage 2.2: Boltz-2 co-fold WT Fv + Aβ1-16
- `slurm/stage2_cofold.sbatch` + `configs/stage2/cofold_wt_Abeta1-16.yaml` (Fv H/L + Aβ1-16 `DAEFRHDSGYEVHHQK`, single-seq). A100 job 11544623 (5 min). 5 seeds × 5 samples = **25 models** (all kept on scratch, D-004 discipline). Aggregated by `scripts/stage2_model/aggregate_cofold.py`.
- **WT baseline:** iptm 0.961±0.019 (min 0.916/max 0.984), ptm 0.974, complex_plddt 0.944. Chain-pair iptm: H-P 0.94, L-P 0.93, H-L 0.985 → peptide contacts **both VH and VL** (CDR-spanning paratope). → `results/stage2/cofold-wt-Abeta1-16-11544623/summary.json` (+ manifest); recorded in metrics.yaml M1.
- **CAVEAT (do not over-read):** Ab-Ag iptm is overconfident/poorly calibrated (guardrail 2, R-EGFR); 0.96 ≠ correct pose. Use Δ-vs-WT + ipSAE; pose is a hypothesis (D-002). Epitope = 1-16 peptide, not the protofibril.

### 2026-06-03 (f) — Stage 2.1: WT Fv model (ABodyBuilder2)
- `scripts/stage2_model/model_fv_wt.py` (env lecam-ab) → refined Fv `results/stage2/fv-wt-20260603/fv_model.pdb` (+ `data/interim/fv_model.pdb`), `geometry_report.json`, `manifest.json`.
- Geometry (ABodyBuilder2 predicted error, Å, in B-factor col): framework-H **0.254**, CDR-H3 **0.816 mean / 2.436 max**, overall-H 0.334 → CDR-H3 least certain (expected; guardrail 2). This is the WT structural baseline for Stage 2.2 co-fold + the eventual metrics.yaml WT reference.
- **Gotcha solved (generalizable):** CC StdEnv `LD_LIBRARY_PATH` intermittently forces system libstdc++ ahead of conda's → OpenMM import `GLIBCXX_3.4.29 not found`. Fix = `LD_LIBRARY_PATH=$CONDA_PREFIX/lib` (force env lib; `-u` alone is unreliable). In memory + docs/env/env_mapping.md.

### 2026-06-03 (e) — Boltz-2 A100 GPU smoke test PASSED
- `slurm/smoke_boltz2.sbatch` + `slurm/smoke/boltz2_gb1.yaml` (single-seq GB1, `msa: empty` → runs OFFLINE). Job **11542978** on frnt154, COMPLETED ~1 min → `boltz2_gb1_model_0.pdb` (56 res) + confidence (**ptm 0.909, complex_plddt 0.94**). Outputs on scratch: `$SCRATCH/results/phase0_smoke/boltz2_11542978/`.
- **Fix that mattered:** plain `boltz` install fails on GPU at the triangle-multiply kernel (`ModuleNotFoundError: cuequivariance_torch`). Boltz-2's GPU forward path **requires `boltz[cuda]`** → reinstalled with the extra; pip resolved **torch 2.12.0+cu130** (cuequivariance_ops needs newer nvidia libs than torch 2.6 pins). Don't cap torch in lecam-fold. Build script + `lecam-fold.versions.txt` updated.
- **R-MODULES resolved:** A100 driver **595.58.03** (CUDA 13.2); torch's bundled CUDA runs with **no `module load cuda`**; **no `--partition`** (SLURM routes gpu:a100 → gpubase_6hrs). Recorded in `slurm/_template.sbatch`.
- Submit pattern (keep REPO_ROOT correct, log to scratch): `cd $repo && sbatch --output=$SCRATCH_ROOT/logs/<name>-%j.out slurm/<job>.sbatch`.

### 2026-06-03 (d) — Built lecam-fold (Boltz-2) + lecam-chai (Chai-1)
- **Boltz-2** (`lecam-fold`, `build_lecam-fold.frontenac.sh`): boltz 2.2.1, CUDA torch 2.6 cu124, numpy 1.26, lightning 2.5.0; `boltz.main` imports, `pip check` clean. Weights → `$SCRATCH/cache/boltz` (7.9G): `boltz2_conf.ckpt` (struct) + **`boltz2_aff.ckpt` (affinity model)** + CCD `mols/`. Download via `boltz.main.download_boltz2(Path(cache))`.
- **Chai-1** (`lecam-chai`, `build_lecam-chai.frontenac.sh`): chai_lab 0.6.1, CUDA torch 2.6, numpy 1.26; imports OK. Weights → `$SCRATCH/cache/chai` (6.6G): 6 components + conformers + **traced ESM2-3B (5.7G)**. Set `CHAI_DOWNLOADS_DIR=$SCRATCH/cache/chai` at runtime (read at import).
- **Why two envs:** chai_lab conflicts with Boltz on shared deps (boltz pins requests==2.32.3 + wandb needs protobuf<6; chai wants requests 2.34 + protobuf 7) → §5 "one isolated env per heavy tool". Co-installing churns pandas/rdkit too. lecam-fold was repaired to clean Boltz state after the conflict was observed.
- **Weights MUST be pre-fetched on login node** (compute nodes have no internet) — done. Created scratch tree `$SCRATCH_ROOT`; cache vars `BOLTZ_CACHE`/`CHAI_CACHE` in frontenac.env.
- **Owed:** A100 GPU fold smoke tests (both) + AF3 container. ColabFold/AF2 stays supplementary (guardrail 2).

### 2026-06-03 (c) — Built lecam-ab env
- `scripts/env/build_lecam-ab.frontenac.sh` (reproducible) → **ImmuneBuilder/ABodyBuilder2, IgFold, AntiBERTy, AbLang2** all verified loading (py3.10, CPU **torch 2.5.1**, numpy 2.2.6). Model weights pre-downloaded on login node (compute nodes have no internet). Versions: `docs/env/lecam-ab.versions.txt`.
- **Frontenac pip hazards solved (generalizable — applies to lecam-fold/-dev builds):** (1) CC wheelhouse hijack → `PIP_CONFIG_FILE=/dev/null` + explicit `--index-url`; (2) CC `_manylinux` shim on `PYTHONPATH` disables manylinux wheels (36 tags, source-build fallback fails on tokenizers/Rust) → **`env -u PYTHONPATH`** (→657 tags); (3) `PYTHONNOUSERSITE=1` silences pydantic plugin warning.
- Version pins that matter: **transformers 4.40.2** (antiberty 0.1.3 breaks on 5.x: `all_tied_weights_keys`); **torch 2.5.1** not 2.6 (2.6 `weights_only=True` default breaks IgFold ckpt load); setuptools<81 + matplotlib for IgFold.
- **Deferred:** BioPhi/Sapiens (humanness, Stage 6) → own env, fairseq/Flask conflicts.

### 2026-06-03 (b) — Phase-0 env mapping
- Inventoried existing conda envs (`conda list`, not assumed) → mapped to `lecam-*` roles in `clusters/frontenac.env`; authoritative table in `docs/env/env_mapping.md`.
- **Usable now:** `lecam` (orchestration); design stack — ProteinMPNN (`mpnn`; repo `…/protein/ProteinMPNN`), RFdiffusion (`rfd_clean`/`rfdiffusion`/`SE3nv`), BindCraft+ColabDesign (`BindCraft`; repo `…/protein/alzheimer/bindcraft`); AF2 oracle (`colabfold` + 5.3G cached weights); PyRosetta 2026.3 (inside `BindCraft`); OpenMM 8.5.1 (interim, in colabfold/BindCraft).
- **Build-needed:** `lecam-ab`, `lecam-fold` (**Boltz-2**/Chai-1 — the Stage-5 ranker per D-004; ColabFold/AF2 is supplementary, not a substitute), `lecam-dev`, dedicated `lecam-rosetta` (flex_ddG/AbLIFT/FoldX) + `lecam-md`; plus RFantibody/LigandMPNN/SolubleMPNN.
- **Owed:** A100 smoke tests (ColabFold/RFdiffusion/BindCraft 1-job each) + confirm CUDA module names (`slurm/_template.sbatch` placeholder).
- No CONDA_ENV_* consumers in scripts yet (only a comment), so repointing broke nothing.

### 2026-06-03 (a) — Stage-1/2 prep: monomer template + antigen coords + 5MY4 discrepancy
- **D-009:** Aβ-monomer counter-target resolved — **1Z0Q** (Aβ42 aqueous NMR, 30 models) primary; **1IYT rejected** (RCSB citation: solved "in an apolar microenvironment" → helical); **2LFM** (Aβ40) kept as Aβ40-matched control. All RCSB-grounded (no memory-typing). ADR → `docs/decisions/D-009-...md`.
- **Antigen coords fetched:** new idempotent `scripts/stage1_inputs/fetch_antigen_templates.sh` pulled 10 mmCIFs (targets 9CO4/7Q4B/7Q4M/8BFZ; counters 9CKI/8QN7/8OLN/1Z0Q/2LFM; ref 5MY4) → `data/raw/antigen/coords/` (git-ignored; `.gitignore` updated; manifest in `coords/fetch_manifest.tsv`).
- **5MY4 discrepancy (OQ-7):** verified via RCSB that PDB **5MY4 = anti-pyroglutamate-Aβ Fab "c#17" (pE3-12 epitope), NOT antibody "D3"** as R-ELIFE/CLAUDE.md B5 state. Our B5 faithfully quotes R-ELIFE (now **pinned**), but 5MY4 is a weak/indirect homology proxy.
- **OQ-7 resolved same day (PI sign-off) → D-010:** primary epitope-homology set = full-length N-terminal anti-Aβ Fab co-structures **6CO3** (aducanumab), **5CSZ** (gantenerumab Aβ1-11), **3BKJ** (WO2 Aβ1-16, closest to lecanemab's window), **4HIX** (humanised 3D6/bapineuzumab); **5MY4 demoted to annotated weak proxy**. 4 new refs fetched to `coords/`. **CLAUDE.md/B5 wording unchanged** (faithful to R-ELIFE); the caveat + ADR are the correction layer.
- **Next:** Phase-0 env MAPPING (existing colabfold/mpnn/rfdiffusion/rfd_clean/BindCraft/SE3nv → lecam-* roles) → Stage 2 (Fv model + multi-seed co-fold; homology pose ensemble from the D-010 set).

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
