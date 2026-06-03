# Campaign Dashboard — lecanemab-am

**Last updated:** 2026-06-03 by frontenac — monomer template resolved (D-009), antigen coords fetched, 5MY4 discrepancy → OQ-7 (PI decision); no SLURM jobs running.

## Cluster status
| Cluster | Agent | Current work | SLURM jobs | Last update |
|---|---|---|---|---|
| Frontenac | F | Stage-1/2 prep done (D-009 monomer + coords); OQ-7 awaiting PI; next: env mapping → Stage 2 | — | 2026-06-03 |
| Narval | Narval | not activated | — | — |
| Nibi | Nibi | not activated | — | — |

## Recent actions
| Date | Agent | Action |
|---|---|---|
| 2026-06-03 | frontenac | Resolved monomer template (D-009: 1Z0Q); fetched 10 antigen mmCIFs (`coords/`, fetch script); found+flagged 5MY4≠D3 (anti-pyroGlu c#17) → pinned B5, opened OQ-7 |
| 2026-06-01 | frontenac | Built `lecam` env (conda-forge; D-007); initialized DuckDB ledger; verified+numbered lecanemab Fv (D-008); identified antigen templates; extracted B1–B7 |
| 2026-05-30 | frontenac | Repo scaffold + coordination layer created |
