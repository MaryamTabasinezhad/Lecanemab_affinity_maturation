# Campaign Dashboard — lecanemab-am

**Last updated:** 2026-06-03 by frontenac — **Boltz-2 A100 smoke test PASSED** (ptm 0.909; R-MODULES resolved); lecam-ab/-fold/-chai built; build-needed lecam-dev/AF3 + remaining smoke tests; no SLURM jobs running.

## Cluster status
| Cluster | Agent | Current work | SLURM jobs | Last update |
|---|---|---|---|---|
| Frontenac | F | Boltz-2 A100-verified (GB1 fold OK); next: lecam-dev + remaining smoke tests (Chai/ColabFold/RFdiff/BindCraft) → Stage 2 | — | 2026-06-03 |
| Narval | Narval | not activated | — | — |
| Nibi | Nibi | not activated | — | — |

## Recent actions
| Date | Agent | Action |
|---|---|---|
| 2026-06-03 | frontenac | **Boltz-2 A100 smoke test PASSED** (job 11542978, GB1 ptm 0.909); boltz[cuda]+torch2.12 cu130 required; R-MODULES resolved (no partition/CUDA module) |
| 2026-06-03 | frontenac | Built **lecam-fold** (Boltz-2, +affinity model) & **lecam-chai** (Chai-1) co-folding oracles; weights cached on scratch (7.9G+6.6G); split envs (dep conflict) |
| 2026-06-03 | frontenac | Built **lecam-ab** env (ImmuneBuilder/IgFold/AntiBERTy/AbLang2, torch2.5.1 cpu); solved CC wheelhouse + _manylinux pip hazards |
| 2026-06-03 | frontenac | Phase-0 env mapping → `docs/env/env_mapping.md` + `frontenac.env` (design/AF2/PyRosetta covered; lecam-ab/-fold/-dev build-needed) |
| 2026-06-03 | frontenac | Resolved monomer template (D-009: 1Z0Q); fetched antigen mmCIFs (`coords/`, fetch script); 5MY4≠D3 (anti-pyroGlu c#17) → pinned B5; resolved OQ-7 → D-010 (homology set 6CO3/5CSZ/3BKJ/4HIX, 5MY4 weak proxy) |
| 2026-06-01 | frontenac | Built `lecam` env (conda-forge; D-007); initialized DuckDB ledger; verified+numbered lecanemab Fv (D-008); identified antigen templates; extracted B1–B7 |
| 2026-05-30 | frontenac | Repo scaffold + coordination layer created |
