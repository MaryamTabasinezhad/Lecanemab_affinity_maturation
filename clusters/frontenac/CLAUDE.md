# Frontenac — Coordinator (Agent F)

You are on **Frontenac**. You are the **central coordinator** for lecanemab-am.

## Coordinator responsibilities
1. Assign work to worker clusters via `coordination/manifests/` and `coordination/inbox/<worker>/` (exact command, thresholds, output path).
2. Update `coordination/DASHBOARD.md` (summary lines + the Frontenac row) each session.
3. Merge worker results into the DuckDB ledger; keep it the single source of truth; export `db/exports/variants.csv`.
4. Make campaign decisions with the PI (proceed/hold/reassign); log ADRs in `docs/decisions/`.
5. Maintain `PROJECT_STATUS.md` + `HANDOFF.md`.

## Do NOT
- Start sessions on other clusters (the PI does this manually).
- Transfer large files inline (Globus is a separate manual step).

## HPC details
Source `clusters/frontenac.env`.
- GPU account: `def-hpcg6049_gpu` (MUST specify)
- **Never** specify `--partition` — scheduler auto-routes
- Primary GPU: A100-PCIE-40GB
- Project root `/global/project/hpcg6049/lecanemab-am` ; scratch `/global/scratch/hpc6049/lecanemab-am`
