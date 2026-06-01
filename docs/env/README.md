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
