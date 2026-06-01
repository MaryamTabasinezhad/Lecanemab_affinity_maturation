# Multi-Cluster Coordination Protocol — lecanemab-am

**Coordinator:** Frontenac (Agent F). **This repo is the only channel.**

## Agent registry
| Agent | Cluster | Role | Working dir | GPU | Status |
|---|---|---|---|---|---|
| F | Frontenac | coordinator | /global/project/hpcg6049/lecanemab-am | A100-40GB | ACTIVE |
| Narval | Narval | worker | CONFIRM | A100 | not activated |
| Nibi | Nibi | worker | CONFIRM | CONFIRM | not activated |

## Communication
1. Coordinator pushes instructions/status to `main`.
2. Workers pull `main` at session start, execute, commit results, push.
3. Large data via Globus (not git) — see `globus/`.

## Commit convention
Prefix every commit with the cluster: `[frontenac] ...`, `[narval] ...`, `[nibi] ...`.

## Conflict avoidance
Each cluster edits ONLY its own DASHBOARD row + its own inbox + its own manifest;
the coordinator edits the summary lines. Resolve DASHBOARD merge conflicts by keeping
both rows and the most recent "Last updated" line.

## Rules for all agents
1. Pull before work; push after.
2. Use ONLY provided settings/configs — no changes without coordinator approval.
3. Scripts use `set -euo pipefail`, absolute paths, and `source clusters/<cluster>.env`.
4. Log all SLURM job IDs in DASHBOARD.md.
5. Variants live in the DuckDB ledger (single source of truth, on the coordinator).
   Workers report rows as CSV; the coordinator merges and re-exports `db/exports/variants.csv`.
   The binary `.duckdb` is git-ignored (unmergeable across agents).
