# HANDOFF.md — lecanemab-am

Coordinator (Frontenac) session-to-session state for the **git-coordinated, multi-cluster** loop. **Update at the END of every working session.** This complements `coordination/DASHBOARD.md` (live cross-cluster status); HANDOFF is the coordinator's continuity log.

**Read order for a new session:** `git pull` → `CLAUDE.md` (incl. §0) → `clusters/<cluster>/CLAUDE.md` → `coordination/DASHBOARD.md` → `coordination/COORDINATION.md` → `PROJECT_STATUS.md` → `DEVELOPMENT_PLAN.md` → `HANDOFF.md` (this file).

---

## Resume here (next action)

**Phase / Stage:** Stage 4/5 — T1 (neutral) + **T2 (30 CDR variants) SCORED** (Boltz Δ-ipSAE + REDUCED flex_ddG triage; consensus_rank in ledger). **First above-noise binding signal:** T2-0021 LC:K56N+V114Y Δipsae +0.21, T2-0017 LC:H31A flexddg −0.69, T2-0001 LC:V114Y +0.09; LC:V114Y/K56N/H31A recur. Next, IN ORDER: (1) **Stage-6 selectivity counter-screen — MANDATORY before any T2 advances** (guardrail 1): co-fold top T2 vs Aβ monomer (1Z0Q) + CAA fibril (8QN7); require Δprotofibril−Δmonomer>0 & ≥WT — a higher Aβ1-16-peptide ipSAE may be MONOMER DRIFT (bad). Build **lecam-dev** (developability) too; (2) re-run top ~5 T2 with FULL flex_ddG (nstruct=35/backrub=35000); (3) metrics.yaml M1 threshold (decision); (4) T3/T4.

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
# DONE 2026-06-03: Stage 2.4 pose-cluster + epitope-register -> GATE MET (pose_hypotheses.json).
#                 Consensus epitope Aβ 1-11/13-15; dominant family 68%; CDR-H3-led paratope; OQ-1 informed.
#                 scripts/stage2_model/analyze_poses.py (lecam; LD_LIBRARY_PATH=$CONDA_PREFIX/lib).
# DONE 2026-06-03: lecam-md built (OpenMM 8.2 CUDA, A100-verified); Stage 2.3 MD -> B3 CONFIRMED
#                 (Aβ N-term flexible RMSF 2.1Å/98% coil; core 6-11 ordered) -> results/stage2/md-flex-11570164.
#                 STAGE 2 COMPLETE.
# DONE 2026-06-04: Stage 4 T1 generated (3 framework variants) AND scored (Boltz-2 Δ-ipSAE vs WT,
#       array job 11673009): all neutral-within-noise -> ledger status=scored. Loop closed.
#       Reusable: scripts/stage4_score/{make_variant_yamls,collect_scores}.py + slurm/stage4_score_cofold.sbatch.
# DONE 2026-06-04: lecam-rosetta built (PyRosetta 2026.21) + flex_ddG 2nd scorer; T1 ΔΔG all ~0 (binding-neutral,
#       agrees with Boltz). scripts/_tools/flexddg/{flexddg_run,aggregate_flexddg}.py + slurm/stage5_flexddg.sbatch.
#       flex_ddG RUN: env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib conda run -n lecam-rosetta.
#       For CDR/interface muts use FULL settings (nstruct=35, backrub=35000); framework used reduced (5/10000).
# Next: (1) build lecam-dev -> score T1 + WT developability/humanness (T1's real value) -> Stage-6 gate;
#       (2) T2/T3 CDR tracks (binding gains) through the Boltz+flex_ddG harness;
#       (3) set metrics.yaml M1 threshold as Δ-ipSAE gate (decision); (4) AbLIFT/FoldX add-ons.
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

### 2026-06-04 (e) — Scored the 30 T2 variants (first above-noise binding signal)
- Boltz-2 multi-seed Δ-ipSAE (array 11829065, 30 tasks) + REDUCED flex_ddG triage (array 11829066, 150 traj, nstruct=5/backrub=10000). Generalized harness: `make_variant_yamls.py --list-name`, `stage4_score_cofold.sbatch` (LIST_FILE env), `gen_resfiles.py` (IMGT→seq_pos, multi-mut), `stage5_flexddg_array.sbatch` (VLIST/NSTRUCT/BACKRUB env), `collect_t2_scores.py` (consensus = z(Δipsae)−z(flexddg)).
- **Top consensus:** T2-0021 LC:K56N+LC:V114Y **Δipsae +0.209** (~3×SEM), T2-0017 LC:H31A flexddg **−0.69**, T2-0019 HC:Y110P+V114Y +0.136, T2-0001 LC:V114Y +0.094, T2-0011 HC:E107D flexddg −0.65. → `results/stage4/t2_scores_summary.json`. Ledger: boltz_ipsae/flexddg_kcal/consensus_rank/status=scored.
- **CAVEATS:** flex_ddG reduced (triage only); ipSAE soft prioritization (guardrail 5); **SELECTIVITY UNCHECKED — improved Aβ1-16-peptide ipSAE could = monomer drift; Stage-6 counter-screen mandatory before any hit (guardrail 1).**

### 2026-06-04 (d) — T2 conservative CDR point-mutation panel (30 variants registered)
- PI chose "conservative point mutations". `scripts/stage4_gen/t2_conservative_pointmuts.py`: ProteinMPNN `--conditional_probs_only` on the Fv–Aβ complex → per-CDR-position log p(aa | rest-WT + backbone + bound Aβ). 17 single CDR muts clear log-odds≥1.0 (LC:V114Y 3.9, HC:G59D 3.8, HC:Y110P 3.3, LC:K56N 2.9, HC:T29D 2.8, HC:R112B→D 2.5, …; span H1/H2/H3/L2/L3), + low-edit combos → **30 T2 registered** (LEC-AM-T2-0001..30). `results/stage4/t2c-20260604/`.
- IMGT notation handles insertion codes (e.g. R112B, Y111A in CDR-H3). Conditioned on the uncertain pose → counter-screen mandatory.
- Next: score (Boltz Δ-ipSAE + FULL flex_ddG) + Stage-6 selectivity counter-screen.

### 2026-06-04 (c) — T2 ProteinMPNN first pass: too-aggressive finding (awaiting PI constraint)
- `scripts/stage4_gen/t2_cdr_proteinmpnn.py` (reuses `../protein/ProteinMPNN` + `mpnn` env, CPU). Vanilla MPNN, Fv–Aβ complex, Aβ+framework fixed, 6 IMGT CDRs designable, 96 seqs.
- **Every design rewrites 27–35/56 CDR positions** (median 31) → near-complete CDR rewrite, NOT conservative AM. Would erode conformational selectivity (guardrail 1). **0 registered to ledger** (by design). Finding: `results/stage4/t2-20260604/T2_FINDING.md`.
- **AWAITING PI decision** on how to constrain T2: (1) fix CDR-H3 + WT-bias the rest; (2) conservative point-muts only (cap ~2-4); (3) accept aggressive + stringent Stage-6 selectivity counter-screen. Then re-run with the chosen constraint, register, score via the Boltz+flex_ddG harness (FULL flex_ddG for these interface muts).
- Note: ProteinMPNN helper `make_fixed_positions_dict.py --specify_non_fixed` lets you pass the designable positions directly. CDR seq positions: H={...33 pos}, L={...23 pos} in the manifest.

### 2026-06-04 (b) — lecam-rosetta + flex_ddG 2nd scorer (T1 binding-neutral consensus)
- Built `lecam-rosetta` (PyRosetta 2026.21, pip via pyrosetta-installer distributed=True). Run flex_ddG via PyRosetta RosettaScriptsParser on the Kortemme `ddG-backrub.xml` — **no compiled rosetta_scripts binary needed**. Tools in `scripts/_tools/flexddg/`.
- CPU array (job 11675128, 15 traj, ~7 min each): per variant 5 trajectories, backrub=10000 (REDUCED). `aggregate_flexddg.py` → ddG (REU + zemu-GAM kcal).
- **ΔΔG (GAM kcal):** HC:T70S −0.00±0.03, LC:A17D +0.06±0.13, HC:S24A +0.10±0.10 — all binding-neutral; **agrees with Boltz-2 Δ-ipSAE** → 2-scorer consensus (D-004). Ledger `flexddg_kcal` set; `db/exports/variants.csv`. → `results/stage5/t1_consensus_scores.json`.
- WT complex used: best-ipSAE pose `data/interim/flexddg/wt_complex.pdb`; resfiles use Boltz sequential resnums (NOT IMGT).

### 2026-06-04 — Scored the 3 T1 variants (Boltz-2 Δ-ipSAE vs WT)
- Per-variant 5-seed×5-sample Boltz-2 co-fold vs Aβ1-16 (A100 array 11673009, 5 min), reusing the WT 2.2 harness. `scripts/stage4_score/make_variant_yamls.py` + `slurm/stage4_score_cofold.sbatch` + `collect_scores.py`.
- Δ-ipSAE vs WT (0.531): HC:S24A **−0.077**, HC:T70S **−0.105**, LC:A17D **−0.136** — all within noise (ipSAE std ~0.25). Expected: CDR-preserving framework changes are ~neutral on binding (none improves it). iptm ~0.95 all (intra-Fv-inflated, same as WT).
- Ledger updated: boltz_ipsae/boltz_iptm/status=scored/stage_reached=5 → `db/exports/variants.csv`. Comparison → `results/stage4/t1_scores_summary.json`.
- T1 advancement should be driven by **developability/humanness** (Stage 6, needs lecam-dev), not these binding deltas. Guardrail 5: in-silico ipSAE = soft prioritization, display decides.

### 2026-06-03 (k) — Stage 4 T1 (framework, LM-prior) — first variants in ledger
- `scripts/stage4_gen/t1_framework_lm.py` (lecam-ab, AbLang2 paired OAS prior): CDR-preserving framework/Vernier point mutants by per-position log-odds (logit[mut]−logit[wt]); IMGT CDRs protected; Vernier (Kabat) tagged.
- **Finding:** lecanemab framework is strongly OAS-consistent — only 3 positions clear log-odds≥0.5: **LC:A17D (2.92), HC:T70S (1.11), HC:S24A (1.09)** (all framework, no Vernier). Not padded with marginal noise (guardrail 4).
- Registered LEC-AM-T1-0001..3 → `db/variants.duckdb` (via `scripts/_tools/ledger_load_csv.py`) + `db/exports/variants.csv` (git-shared). FASTA/CSV/manifest in `results/stage4/t1-20260603/`.
- T1's AbLIFT/Rosetta VH-VL interface-redesign sub-method pending `lecam-rosetta`.

### 2026-06-03 (j) — lecam-md built + Stage 2.3 MD (B3 confirmed)
- Built `lecam-md` (conda-forge OpenMM 8.2 **CUDA** + pdbfixer + mdtraj; `scripts/env/build_lecam-md.frontenac.sh`). CUDA platform A100-verified (login lists only Reference/CPU — no GPU there).
- `scripts/stage2_model/md_flexibility.py` + `slurm/stage2_md.sbatch`: 5 ns implicit-solvent (amber14/GBn2) MD of the best-ipSAE pose (seed2/model_3), Fv-framework CA restrained, CDR+Aβ free. A100 job 11570164 (15 min, CUDA, 500 frames).
- **B3 confirmed:** Aβ N-term(1-5) RMSF **2.10 Å** / **97.5% coil**; core(6-11) RMSF 1.04 Å (most ordered = engaged); C-term(12-16) RMSF 2.09 Å; CDR-H3 RMSF 0.77 Å. → flexible/unstructured engaged N-terminus, contrasting fixed-N counter-targets (B4). → `results/stage2/md-flex-11570164/md_flexibility.json`.
- Run rule: `LD_LIBRARY_PATH=$CONDA_PREFIX/lib` (OpenMM libstdc++/nvrtc vs CC StdEnv).

### 2026-06-03 (i) — ipSAE on the 25 WT co-fold poses
- `scripts/stage2_model/compute_ipsae.py` wraps official `scripts/_tools/ipsae.py` v4 (Dunbrack 2025; supports Boltz npz+pdb), pae_cutoff=10 dist_cutoff=10. → `ipsae_summary.json` (+ manifest_ipsae.json).
- **Fv–Aβ interface ipSAE = 0.531 ± 0.256 (range 0.07–0.88)**; H-P 0.531, L-P 0.494; intra-Fv VH-VL 0.964 (sanity, genuine). The headline iptm 0.961 was inflated by VH-VL; ipSAE is the interface-specific number → recorded as M1 baseline in metrics.yaml.
- **Interpretation:** contact footprint is consistent (2.4 Jaccard 0.86) but interface *confidence* is moderate + high-variance → pose genuinely uncertain (D-002); rank variants by Δ-ipSAE with multi-sample consensus, never absolute iptm.

### 2026-06-03 (h) — Stage 2.4: pose cluster + epitope register (GATE MET)
- `scripts/stage2_model/analyze_poses.py` (lecam/biotite+scipy) on the 25 poses → `pose_hypotheses.json` + `manifest_2.4.json`.
- Consensus epitope (≥50% poses): Aβ **1-11, 13, 14, 15** (positions 2-10 @ 100%; V12 28%, K16 32%). Paratope CDR-H3-led (10 H3 residues; + L3/L1/H1/H2 + Vernier-flank FR e.g. H50/H59).
- **OQ-1 informed:** footprint covers BOTH lit "3-7" (all 100%) and B6 hotspots (Y10/E11/H13/H14/Q15; not K16) → neither contradicted; kept as hypothesis set (D-002).
- Pose family: largest cluster 17/25 (**68%**), Aβ-CA mean pairwise RMSD 3.4 Å, footprint Jaccard 0.864. Gate ✅ (self-consistent family, N-terminal/B3, not-contradicting-B6) with documented uncertainty.

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
