# Lecanemab — Computational Affinity Maturation (`lecanemab-am`)

A **computational** affinity-maturation campaign on **lecanemab** (Leqembi / BAN2401), the humanized IgG1 anti-Aβ-protofibril antibody. The pipeline is a funnel: in-silico generation/scoring → counter-selection + developability gates → a small, experimentally-testable panel of matured Fv variants → measured KD fed back to re-weight the rankers (active learning).

> **The design objective (read before anything):** maximize **avidity-adjusted affinity for Aβ protofibrils/oligomers while preserving conformational selectivity** (vs Aβ monomer and fixed-N-terminus / CAA fibrils) and developability. **Do NOT optimize raw monovalent KD** — that destroys lecanemab's >10⁶-fold selectivity and its low-ARIA safety margin. Full rationale in [`CLAUDE.md §2`](CLAUDE.md).

This is a **multi-cluster, git-coordinated** project: the git repo *is* the coordination channel between Claude Code agents running on different SLURM clusters. **Frontenac** is the coordinator; worker clusters are added as hired.

---

## Where to look for what

| You want… | Go to |
|---|---|
| Mission, objective, biology, guardrails, env map | [`CLAUDE.md`](CLAUDE.md) — the canonical context; read in full first |
| The 8-stage pipeline plan | [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) |
| Live status, stage checklist, decision log (ADRs), open questions | [`PROJECT_STATUS.md`](PROJECT_STATUS.md) |
| Coordinator session-to-session continuity / "resume here" | [`HANDOFF.md`](HANDOFF.md) |
| Cross-cluster live status + coordination rules | [`coordination/DASHBOARD.md`](coordination/DASHBOARD.md), [`coordination/COORDINATION.md`](coordination/COORDINATION.md) |
| Per-cluster config (paths, SLURM, Globus) + how to add a worker | [`clusters/`](clusters/) (`<cluster>.env`, `<cluster>/CLAUDE.md`, `README.md`) |
| Objective + metric definitions/thresholds | [`configs/objective.yaml`](configs/objective.yaml), [`configs/metrics.yaml`](configs/metrics.yaml) |
| Source-grounding (every biological claim → exact sentence) + Fv provenance | [`docs/sources/`](docs/sources/) |
| Pinned env versions / tool setup notes | [`docs/env/`](docs/env/) |
| Stage scripts | [`scripts/stage1_inputs/` … `scripts/stage8_validate/`](scripts/) |
| Portable SLURM template | [`slurm/_template.sbatch`](slurm/_template.sbatch) |
| Variant ledger schema (single source of truth) | [`db/schema.sql`](db/schema.sql) |
| Curated inputs (Fv sequence, antigen template IDs) | [`data/raw/`](data/raw/) |

## Repository conventions

- **Variant ledger** (`db/variants.duckdb`, DuckDB) is the single source of truth. The binary is **git-ignored** (unmergeable across agents); the git-shared form is `db/exports/*.csv` + `coordination/manifests/*.tsv`.
- **Large data** (PDBs, cryo-EM maps, model weights, samples, containers) moves via **Globus, not git** (`coordination/globus/`).
- Every run writes a date-stamped `manifest.json` (inputs, tool versions, configs, git commit, SLURM job id, seeds) under `results/<stage>/<run-id>/`.
- Commits are prefixed `[<cluster>]`; the coordinator is `[frontenac]`.

## Status (high level)

Phase 0 (scaffold + `lecam` env + ledger) and Stage 1 (Fv sourced/verified/numbered, antigen templates, source extracts) are done. See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) and [`HANDOFF.md`](HANDOFF.md) for the current resume point.
