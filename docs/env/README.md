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

> **Env→role mapping (Frontenac, 2026-06-03):** see `docs/env/env_mapping.md`. Several roles are
> already covered by pre-existing envs (colabfold, mpnn, rfd_clean/rfdiffusion/SE3nv, BindCraft);
> canonical names live in `clusters/frontenac.env`.

## Manual / licensed / container checklist (do NOT guess install commands)
- [x] PyRosetta — present (2026.3) in the **BindCraft** env (`CONDA_ENV_PYROSETTA`)
- [ ] FoldX license + binary  (still missing)
- [x] Rosetta **flex_ddG** — env `lecam-rosetta` built (PyRosetta 2026.21 + `scripts/_tools/flexddg/`, smoke-tested); AbLIFT protocol TODO
- [ ] AlphaFold3 container + model params (access-gated)
- [x] Boltz-2 — env `lecam-fold` built (boltz[cuda], torch 2.12 cu130) + **A100-verified** (GB1, ptm 0.909); weights cached `$SCRATCH/cache/boltz` (7.9G, incl. affinity model)
- [x] Chai-1 — env `lecam-chai` built (separate; dep conflict); weights `$SCRATCH/cache/chai` (6.6G, incl. ESM2-3B)
- [x] BindCraft repo+env — present (`…/protein/alzheimer/bindcraft`, env `BindCraft`)
- [x] ColabFold (AF2) — env + weights present (`~/.cache/colabfold/params`, 5.3G)
- [x] ProteinMPNN repo — present (`…/protein/ProteinMPNN`); runtime env `mpnn`
- [x] RFdiffusion — env `rfd_clean`/`rfdiffusion` (rfdiffusion 1.1.0)
- [ ] RFantibody, LigandMPNN, SolubleMPNN  (still missing)
- [x] `lecam-ab` — **built 2026-06-03** (ImmuneBuilder/IgFold/AntiBERTy/AbLang2 verified; `scripts/env/build_lecam-ab.frontenac.sh`); BioPhi/Sapiens deferred to own env
- [x] `lecam-md` — **built 2026-06-03** (OpenMM 8.2 CUDA + pdbfixer + mdtraj; A100-verified job 11570164; `scripts/env/build_lecam-md.frontenac.sh`); AlphaFlow optional/TODO
- [ ] `lecam-dev` (Aggrescan3D/NetSolP/SoluProt/TAP/DeepViscosity) — not built
- [x] Frontenac A100: driver 595.58.03 (CUDA 13.2); **no system CUDA module needed** for torch-bundled-CUDA tools; **no `--partition`** (auto-routes to gpubase_*). (Workers TBD.)
