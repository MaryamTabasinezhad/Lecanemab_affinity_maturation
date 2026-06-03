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
- [ ] Rosetta flex_ddG + AbLIFT  (still missing → `lecam-rosetta`)
- [ ] AlphaFold3 container + model params (access-gated)
- [ ] Boltz-2 + Chai-1 model weights  (→ `lecam-fold`; the Stage-5 ranker, D-004)
- [x] BindCraft repo+env — present (`…/protein/alzheimer/bindcraft`, env `BindCraft`)
- [x] ColabFold (AF2) — env + weights present (`~/.cache/colabfold/params`, 5.3G)
- [x] ProteinMPNN repo — present (`…/protein/ProteinMPNN`); runtime env `mpnn`
- [x] RFdiffusion — env `rfd_clean`/`rfdiffusion` (rfdiffusion 1.1.0)
- [ ] RFantibody, LigandMPNN, SolubleMPNN  (still missing)
- [ ] `lecam-ab` (ImmuneBuilder/IgFold/AbLang2/AntiBERTy/BioPhi) — not built
- [ ] `lecam-dev` (Aggrescan3D/NetSolP/SoluProt/TAP/DeepViscosity) — not built
- [ ] Confirm CUDA/cuDNN + module names per cluster (Frontenac A100; workers TBD)
