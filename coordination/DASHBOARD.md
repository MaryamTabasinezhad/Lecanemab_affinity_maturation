# Campaign Dashboard — lecanemab-am

**Last updated:** 2026-06-03 by frontenac — Stage-1/2 prep (D-009, D-010) + Phase-0 env mapping done; build-needed envs + A100 smoke tests remain; no SLURM jobs running.

## Cluster status
| Cluster | Agent | Current work | SLURM jobs | Last update |
|---|---|---|---|---|
| Frontenac | F | Env mapping done (`docs/env/env_mapping.md`); next: build lecam-ab/-fold(Boltz-2)/-dev + A100 smoke tests → Stage 2 | — | 2026-06-03 |
| Narval | Narval | not activated | — | — |
| Nibi | Nibi | not activated | — | — |

## Recent actions
| Date | Agent | Action |
|---|---|---|
| 2026-06-03 | frontenac | Phase-0 env mapping → `docs/env/env_mapping.md` + `frontenac.env` (design/AF2/PyRosetta covered; lecam-ab/-fold/-dev build-needed) |
| 2026-06-03 | frontenac | Resolved monomer template (D-009: 1Z0Q); fetched antigen mmCIFs (`coords/`, fetch script); 5MY4≠D3 (anti-pyroGlu c#17) → pinned B5; resolved OQ-7 → D-010 (homology set 6CO3/5CSZ/3BKJ/4HIX, 5MY4 weak proxy) |
| 2026-06-01 | frontenac | Built `lecam` env (conda-forge; D-007); initialized DuckDB ledger; verified+numbered lecanemab Fv (D-008); identified antigen templates; extracted B1–B7 |
| 2026-05-30 | frontenac | Repo scaffold + coordination layer created |
