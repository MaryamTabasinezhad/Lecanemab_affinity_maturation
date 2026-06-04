# Conda env → role mapping (Frontenac)

**Mapped:** 2026-06-03 (Phase 0). **Source of truth for env names:** `clusters/frontenac.env` (`CONDA_ENV_*`).
All package facts below were read from `conda list` on Frontenac (login node) — not assumed.
Env names differ from the canonical `lecam-*` labels (CLAUDE.md §5); this table reconciles them.

## Summary

| Role (§5) | Canonical | Existing env(s) on Frontenac | Coverage | Gap to fill |
|---|---|---|---|---|
| Orchestration | `lecam` | **lecam** | ✅ full | — |
| Antibody modeling & LMs | `lecam-ab` | **lecam-ab** (built 2026-06-03) | ✅ core | ImmuneBuilder+IgFold+AntiBERTy+AbLang2 verified; **BioPhi/Sapiens deferred** to own env |
| Co-folding oracles | `lecam-fold` (Boltz-2) + `lecam-chai` (Chai-1) | **lecam-fold**, **lecam-chai** built 2026-06-03; **colabfold** (AF2) | ✅ Boltz-2+Chai-1 | AF3 = container (pending) |
| Variant generation | `lecam-design` | **mpnn**, **rfd_clean**/**rfdiffusion**/**SE3nv**, **BindCraft** | ◐ strong | RFantibody, LigandMPNN, SolubleMPNN |
| Physics scoring | `lecam-rosetta` | **lecam-rosetta** built 2026-06-04 (PyRosetta 2026.21 + flex_ddG) | ✅ flex_ddG | AbLIFT protocol + FoldX (licensed) TODO |
| Conformational ensembles | `lecam-md` | **lecam-md** built 2026-06-03 (OpenMM 8.2 CUDA, A100-verified) | ✅ | AlphaFlow (opt) still TODO |
| Developability | `lecam-dev` | *(none)* | ⛔ missing | build: Aggrescan3D, NetSolP, SoluProt, TAP, DeepViscosity, DE-STRESS |

## Existing envs — what's actually installed (verified 2026-06-03)

| env | python | key packages | maps to | notes |
|---|---|---|---|---|
| **lecam** | 3.11 | duckdb, pandas, biopython/biotite, **ANARCI 2026.2.13.2**, HMMER, pyyaml | `lecam` (MAIN) | conda-forge build (D-007) |
| **colabfold** | 3.11 | colabfold 1.6.1, alphafold-colabfold 2.3.13, jax 0.6.0 (CUDA12), **openmm 8.5.1** | `lecam-fold` (AF2), `lecam-md` (OpenMM) | weights cached `~/.cache/colabfold/params` (5.3G); AF2 only — **not Boltz-2/AF3** |
| **mpnn** | 3.9 | pytorch 2.7.1 | `lecam-design` (ProteinMPNN) | repo-run tool; repo `…/protein/ProteinMPNN` (+ `…/protein/proteinmpnn`) |
| **rfd_clean** | 3.9 | rfdiffusion 1.1.0, se3-transformer 1.0.0, dgl 2.1.0, torch 2.5.1/cu11.8 | `lecam-design` (RFdiffusion) | preferred RFdiffusion env (newer torch) |
| **rfdiffusion** | 3.9 | rfdiffusion 1.1.0, se3-transformer 1.0.0, dgl 2.1.0, torch 2.0.1/cu11.8 | `lecam-design` (RFdiffusion) | alternate (older torch) |
| **SE3nv** | 3.9 | (RFdiffusion SE3-transformer support env) | `lecam-design` (RFdiffusion) | classic RFdiffusion SE3 env |
| **BindCraft** | 3.10 | bindcraft + colabdesign 1.1.3, jax 0.6.0, openmm 8.5.1, **pyrosetta 2026.3** | `lecam-design` (BindCraft/ColabDesign), `lecam-rosetta` (PyRosetta) | repo `…/protein/alzheimer/bindcraft`; doubles as PyRosetta host |

## Build-needed (provisioning backlog — Phase 0)
1. ~~**`lecam-ab`**~~ **BUILT 2026-06-03** (`scripts/env/build_lecam-ab.frontenac.sh`, versions in `lecam-ab.versions.txt`): ImmuneBuilder/ABodyBuilder2 + IgFold + AntiBERTy + AbLang2, all verified loading (CPU torch 2.5.1; weights cached on login node). **Remaining for this role:** BioPhi/Sapiens humanness (Stage 6) → recommend a separate `lecam-hum` env (fairseq/Flask conflicts).
2. ~~**`lecam-fold` / Boltz-2**~~ **BUILT 2026-06-03** (`scripts/env/build_lecam-fold.frontenac.sh`): Boltz-2 2.2.1, CUDA torch 2.6 cu124, `boltz.main` imports, `pip check` clean; weights cached on scratch (`$SCRATCH/cache/boltz`, 7.9G incl. the **affinity** model `boltz2_aff.ckpt`). **Chai-1 also BUILT** in its own env `lecam-chai` (`build_lecam-chai.frontenac.sh`; weights `$SCRATCH/cache/chai`, 6.6G incl. traced ESM2-3B) — separate because chai_lab conflicts with Boltz on requests/protobuf/pandas/rdkit. **Still pending:** AF3 (container, access-gated) + **A100 GPU fold smoke tests** for both. ColabFold/AF2 remains supplementary only (guardrail 2).
3. **`lecam-dev`** — developability gate tools (Stage 6).
4. ~~**`lecam-rosetta`**~~ **BUILT 2026-06-04** (`scripts/env/build_lecam-rosetta.frontenac.sh`): PyRosetta 2026.21 (pip, thread+serialization build) + **flex_ddG** ΔΔG via PyRosetta RosettaScriptsParser (`scripts/_tools/flexddg/`, smoke-tested). Remaining: AbLIFT VH-VL redesign protocol + FoldX (separate licensed binary).
5. ~~**`lecam-md`**~~ **BUILT 2026-06-03** (`scripts/env/build_lecam-md.frontenac.sh`): OpenMM 8.2 (CUDA, A100-verified job 11570164) + pdbfixer + mdtraj. AlphaFlow (optional) still TODO.
6. **Design extras** — RFantibody (antibody-specific RFdiffusion), LigandMPNN, SolubleMPNN.

## ⚠ pip build gotchas on Frontenac (apply to EVERY pip-based env build)
The CC StdEnv breaks PyPI pip installs two ways — both must be neutralized or wheels fail / source-build:
1. **CC wheelhouse hijack** — `PIP_CONFIG_FILE` points at a CVMFS config whose find-links serve `+computecanada` wheels (glibc 2.29/2.30) that break on system glibc 2.28. → set `PIP_CONFIG_FILE=/dev/null` and an explicit `--index-url`.
2. **`_manylinux` shim** — `PYTHONPATH=/cvmfs/.../custom/python/site-packages` contains a `_manylinux.py` that **disables manylinux detection** (pip sees 36 tags, no manylinux → rejects all PyPI manylinux wheels → falls back to source builds, e.g. tokenizers needs Rust and fails). → run pip with **`env -u PYTHONPATH`** (restores 657 tags incl `manylinux_2_17_x86_64`).
3. `PYTHONNOUSERSITE=1` — silences the harmless `anaconda-cloud-auth` GLIBC_2.30 plugin warning from a py3.12 pydantic in `~/.local`.

Canonical wrapper: `env -u PYTHONPATH PYTHONNOUSERSITE=1 PIP_CONFIG_FILE=/dev/null conda run -n <env> pip install --index-url https://pypi.org/simple ...`

### Runtime gotcha (compiled libs, e.g. OpenMM) — `LD_LIBRARY_PATH`
The CC StdEnv may put a `LD_LIBRARY_PATH` into the shell that forces the **system** `/lib64/libstdc++.so.6` (too old — lacks `GLIBCXX_3.4.29`) ahead of the conda env's own, so OpenMM/pdbfixer imports fail with `ImportError: ... GLIBCXX_3.4.29 not found`. It is intermittent (depends on whether the StdEnv was sourced in that shell). **Fix: force the env's lib first** — set `LD_LIBRARY_PATH=$CONDA_PREFIX/lib` (NOT just `-u`, which is a no-op when the shell hasn't set it). Canonical runtime wrapper for envs with compiled deps (lecam-ab OpenMM, lecam-md, ...):
`env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=/global/home/hpc6049/.conda/envs/<env>/lib conda run -n <env> python ...`

## Smoke tests (A100)
- [x] **Boltz-2** 1-sample fold — **PASSED 2026-06-03** (job 11542978, frnt154, ~1 min): GB1 single-seq from offline scratch weights → valid 56-res PDB, ptm 0.909 / complex_plddt 0.94. **R-MODULES resolved:** A100 driver **595.58.03** (CUDA 13.2-capable); torch's bundled CUDA (cu130) runs with **no system CUDA module load** — and **no `--partition`** needed (SLURM auto-routes to `gpubase_6hrs`). NOTE: `boltz[cuda]` extra (cuequivariance kernels) is **required** for the GPU forward path. Job script: `slurm/smoke_boltz2.sbatch`.
- [ ] **Chai-1** 1 fold (`lecam-chai`, `CHAI_DOWNLOADS_DIR=$SCRATCH/cache/chai`)
- [ ] ColabFold 1-target fold (verify GPU + cached weights)
- [ ] RFdiffusion 1-design (rfd_clean) on the A100
- [ ] BindCraft 1-design (validates jax/PyRosetta/OpenMM stack on GPU)
- [ ] Confirm CUDA/cuDNN **module names** on the Frontenac A100 node (placeholder in `slurm/_template.sbatch`)
