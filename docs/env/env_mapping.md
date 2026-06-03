# Conda env → role mapping (Frontenac)

**Mapped:** 2026-06-03 (Phase 0). **Source of truth for env names:** `clusters/frontenac.env` (`CONDA_ENV_*`).
All package facts below were read from `conda list` on Frontenac (login node) — not assumed.
Env names differ from the canonical `lecam-*` labels (CLAUDE.md §5); this table reconciles them.

## Summary

| Role (§5) | Canonical | Existing env(s) on Frontenac | Coverage | Gap to fill |
|---|---|---|---|---|
| Orchestration | `lecam` | **lecam** | ✅ full | — |
| Antibody modeling & LMs | `lecam-ab` | *(none)* | ⛔ missing | build: ImmuneBuilder, IgFold, AbLang2, AntiBERTy, BioPhi/Sapiens |
| Co-folding oracles | `lecam-fold` | **colabfold** (AF2 only) | ◐ partial | build: **Boltz-2**, Chai-1; AF3 container |
| Variant generation | `lecam-design` | **mpnn**, **rfd_clean**/**rfdiffusion**/**SE3nv**, **BindCraft** | ◐ strong | RFantibody, LigandMPNN, SolubleMPNN |
| Physics scoring | `lecam-rosetta` | **BindCraft** (PyRosetta only) | ◐ partial | Rosetta flex_ddG, AbLIFT, FoldX (licensed) |
| Conformational ensembles | `lecam-md` | OpenMM 8.5.1 inside colabfold/BindCraft | ◐ partial | dedicated env; AlphaFlow (opt) |
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
1. **`lecam-ab`** — antibody structure (ImmuneBuilder/ABodyBuilder2, IgFold) + LMs (AbLang2, AntiBERTy, BioPhi/Sapiens). Needed Stage 2/3/6.
2. **`lecam-fold` / Boltz-2** — the Stage-5 affinity ranker (D-004 = multi-sample Boltz-2/AF3 ipTM+ipSAE). ColabFold/AF2 is **supplementary**, not a substitute (AF-Multimer weak on CDR-H3/epitope pose — guardrail 2). Chai-1 + AF3 container also pending.
3. **`lecam-dev`** — developability gate tools (Stage 6).
4. **`lecam-rosetta`** — flex_ddG + AbLIFT + FoldX (licensed; PyRosetta already usable via BindCraft env).
5. **`lecam-md`** — dedicated OpenMM/GROMACS env (interim: OpenMM 8.5.1 in colabfold/BindCraft).
6. **Design extras** — RFantibody (antibody-specific RFdiffusion), LigandMPNN, SolubleMPNN.

## Smoke tests still owed (A100, before first heavy submit)
- [ ] ColabFold 1-target fold (verify GPU + cached weights)
- [ ] RFdiffusion 1-design (rfd_clean) on the A100
- [ ] BindCraft 1-design (validates jax/PyRosetta/OpenMM stack on GPU)
- [ ] Confirm CUDA/cuDNN **module names** on the Frontenac A100 node (placeholder in `slurm/_template.sbatch`)
