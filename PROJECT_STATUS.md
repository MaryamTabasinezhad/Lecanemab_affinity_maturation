# PROJECT_STATUS.md — lecanemab-am

**Last updated:** 2026-06-03  ·  **Updated by:** Hamid (with Claude)  ·  **Phase:** Phase 0 (done) → Stage 1 (in progress)
**GitHub:** `git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git`  ·  **Project root:** `/global/project/hpcg6049/lecanemab-am` (Frontenac)  ·  **Coordinator:** Frontenac · **Workers:** none active yet

---

## Snapshot

Phase 0 scaffold **executed** on Frontenac (`00_init.sh`): full repo tree + git repo + coordination layer + `db/schema.sql`; `lecam` env built (conda-forge; D-007); DuckDB ledger initialized. **Stage 1 deliverables:** lecanemab Fv sourced & cross-verified (D-008) + ANARCI-numbered; antigen templates identified, **coordinates fetched** (D-009 monomer template resolved), B1–B7 extracted. While fetching, found + resolved a load-bearing reference discrepancy — **5MY4 is anti-pyroGlu-Aβ Fab c#17, not "D3"** (OQ-7).
Immediate next action: **PI decision on OQ-7** (epitope-homology template set); then Phase-0 env mapping (`lecam-*` → existing `colabfold`/`mpnn`/`rfdiffusion`/`BindCraft`) + A100 smoke tests; then Stage 2 (Fv model + multi-seed co-fold).

---

## Stage checklist

| Stage | Title | Status |
|---|---|---|
| 0 | Provisioning (repo, envs, HPC paths, ledger) | ◐ scaffold+ledger+`lecam` done; other envs + smoke tests pending |
| 1 | Inputs, Targets & Objective Lock-In | ◐ Fv+CDRs+antigens+B1–B7 done; monomer template resolved (D-009) + coords fetched; metrics thresholds await Stage-2 baseline; OQ-7 homology-set open |
| 2 | Structural Modeling & Conformational Ensembles | ☐ |
| 3 | Paratope Mapping & Design-Space Definition | ☐ |
| 4 | Variant Generation (multi-track) | ☐ |
| 5 | In Silico Affinity Scoring & Consensus Ranking | ☐ |
| 6 | Selectivity Counter-Design, Humanness & Developability | ☐ |
| 7 | Format, Valency & Delivery Engineering | ☐ |
| 8 | Experimental Validation & Active-Learning Loop | ☐ |

Legend: ☐ not started · ◐ in progress · ☑ done · ⊘ blocked

---

## Now / Next / Blocked

**Done (2026-06-01):** Phase-0 scaffold (`00_init.sh`); `lecam` env built (conda-forge/bioconda); DuckDB ledger initialized (`variants`, 27 cols); lecanemab Fv sourced+verified+ANARCI-numbered (3 schemes, CDRs+Vernier); antigen templates identified; B1–B7 source sentences extracted.

**Next (immediate):**
1. **PI decision on OQ-7** — expand the epitope-homology template set (6CO3/5CSZ/3BKJ/3D6) + demote 5MY4 to weak proxy? (Affects Stage-2/3 pose ensemble.)
2. Set `configs/metrics.yaml` thresholds + WT references once a Stage-2 WT baseline exists (currently TODO).
3. ~~Pick Aβ-monomer counter-target template~~ **DONE (D-009: 1Z0Q primary, 2LFM Aβ40 control).**
4. Pin exact B2 (>10⁶ selectivity, R-ANA) sentence (paywalled). B5 D3/5MY4 sentence **pinned 2026-06-03**; R-REV "no co-structure" sentence still to pin.
4. Phase-0 finish: build remaining envs (`lecam-ab/-fold/-design/-rosetta/-md/-dev`; several map to existing `colabfold`/`mpnn`/`rfdiffusion`/`BindCraft`); A100 smoke tests (1-sample Boltz-2, 1-design BindCraft); confirm SLURM module names.
5. Begin Stage 2: Fv model (ImmuneBuilder/IgFold) + multi-seed co-fold against the protofibril epitope.

**Blocked:** none.

---

## Decision log (ADR-lite)

| ID | Date | Decision | Rationale | Source |
|---|---|---|---|---|
| D-001 | 2026-05-30 | Optimization objective = **avidity-adjusted protofibril affinity + selectivity**, NOT monovalent KD | Monovalent affinity gain risks destroying the >10⁶ protofibril/monomer selectivity and the low-ARIA profile | B2,B3,B4 / R-ANA,R-TG |
| D-002 | 2026-05-30 | Structure-based steps use a **pose ensemble**, not a single docked complex | No public co-structure; epitope register uncertain; AF-M weak on CDR-H3/epitope pose | B5,B6 / R-ELIFE,R-EGFR |
| D-003 | 2026-05-30 | First (and safest) variant track = **framework/Vernier + VH-VL interface, CDR-preserving** | Lowest risk to the conformational paratope; mirrors EGFR-2 winning strategy (Cradle) and AbLIFT | R-CRADLE,R-ABLIFT |
| D-004 | 2026-05-30 | Rank affinity by **multi-sample Boltz-2/AF3 ipTM+ipSAE consensus**; exclude unnormalized ESM2 LL from ranking | Multi-sample consensus won the de-novo Nipah track; ESM2 LL non-predictive in EGFR | R-MOSAIC,R-EGFR |
| D-005 | 2026-05-30 | Wet-lab readout = **display with dual selection (protofibril +, monomer −)** then BLI/SPR | Conformational AM is validated this way; counter-selection enforces selectivity | R-YSD |
| D-006 | 2026-05-30 | Adopt **multi-cluster git-coordination** (Frontenac coordinator; workers added as hired) per the lab's prior bispecific-project protocol | Async parallel work across clusters with a full git audit trail; same pattern already proven on the Aβ42×TfR1 project | MULTI_AGENT_COORDINATION_GUIDE |
| D-007 | 2026-06-01 | Build conda envs from **conda-forge/bioconda**, NOT the ComputeCanada CVMFS pip wheelhouse | CC `+computecanada` wheels target glibc 2.29/2.30 but the Frontenac login node is glibc 2.28 → compiled wheels (numpy/pandas/duckdb/biotite) fail to load; conda-forge builds are old-glibc-portable | env build this session |
| D-008 | 2026-06-01 | Verified lecanemab Fv = **KEGG D11678 (WHO-INN)**, CDRs cross-confirmed by **BioArctic patent US9573994B2** | Satisfies §4 ≥2-source rule; both VH/VL CDRs match | `docs/sources/lecanemab_fv_provenance.md` |
| D-009 | 2026-06-03 | Aβ-monomer counter-target = **1Z0Q** (Aβ42 aqueous NMR, 30 models) primary; **reject 1IYT** (apolar/helical); **2LFM** (Aβ40) as Aβ40-matched control | Sequence-matched to Aβ42 targets + aqueous disordered form; counter-screen folds monomer multi-seed (D-002) | `docs/decisions/D-009-...md`; RCSB-grounded |

---

## Open questions / risks

- **OQ-1 — epitope register.** Reconcile internal hotspots (Y10/E11/H13/H14/Q15/K16) with literature ("N-terminal, tolerant 3–7"). Resolve in Stage 2 via ensemble docking + literature cross-check; **do not commit to a single register** (D-002).
- **OQ-2 — display platform.** Yeast surface display vs phage; protofibril reagent prep, stability, and immobilization for counter-selection (Stage 8 dependency).
- **OQ-3 — avidity metric.** Define a concrete valency-aware "avidity-adjusted affinity" score for in-silico use (Stage 6).
- **OQ-4 — Fc / ARIA scope.** Decide whether Fc effector engineering is in-scope (currently optional, Stage 7).
- **R-ENV — tooling conflicts.** AF3 / Boltz-2 / RFantibody / BindCraft likely need isolated envs or containers; resolve at Phase 0.
- **R-MODULES — HPC module names.** Frontenac CUDA/module names are placeholders in `slurm/` templates → confirm on first login before submitting (no guessing).
- **OQ-5 — worker clusters.** Which clusters to hire (Narval / Nibi candidates from prior project) and when; activate via `clusters/<cluster>.env` + `clusters/<cluster>/CLAUDE.md`.
- **OQ-6 — Globus endpoints.** Confirm per-cluster Globus endpoint UUIDs + base paths for `lecanemab-am` before any large transfer (`coordination/globus/endpoints.md`).
- **OQ-7 — epitope homology template set (NEEDS PI DECISION).** R-ELIFE models lecanemab on "D3 antibody similarity (PDB **5MY4**)", but **5MY4's deposited content is anti-pyroglutamate-Aβ Fab c#17 (pE3-12)** — an N-truncated/modified epitope, a weak proxy for lecanemab's full-length N-terminal (1–16) conformational epitope (verified RCSB 2026-06-03). **Proposal:** expand the pose-ensemble homology set (D-002) with full-length N-terminal anti-Aβ Fab co-structures — aducanumab **6CO3** (3–7), gantenerumab **5CSZ** (Aβ1-11), 3D6/bapineuzumab (Aβ1-7), WO2 **3BKJ** (Aβ1-16) — and demote 5MY4 to an annotated weak proxy. Affects Stage-2/3 epitope modeling + OQ-1.

---

## Environment & data status

| Item | Status |
|---|---|
| Repo skeleton | ☑ created (`00_init.sh`) |
| Git remote (GitHub) | ☑ set (`origin`, SSH auth OK as `hamidghaedi`) |
| Coordination scaffold (`clusters/`, `coordination/`) | ☑ created |
| Conda envs | ◐ `lecam` built (conda-forge); `lecam-ab/-fold/-design/-rosetta/-md/-dev` pending |
| DuckDB ledger | ☑ initialized (`db/variants.duckdb`, `variants` 27 cols) |
| Lecanemab Fv sequence | ☑ sourced + verified (2 sources) + ANARCI-numbered (IMGT/Kabat/Chothia) + CDRs/Vernier |
| Antigen templates | ◐ IDs identified + **coords fetched** (`data/raw/antigen/coords/`, git-ignored); monomer template **resolved (D-009)**; EMDB maps deferred (Globus); **OQ-7** homology-set open |
| `docs/sources/` extracts (B1–B7) | ◐ written; **B5 D3/5MY4 sentence pinned + 5MY4 identity caveat (OQ-7)**; B2 + R-REV sentences still flagged |
| SLURM templates verified on Frontenac | ☐ not verified (module names placeholder) |
| Worker clusters activated | ☐ none (Frontenac only) |

---

## Changelog

- **2026-06-03** — Stage-1/2 prep: resolved Aβ-monomer counter-target template (**D-009**: 1Z0Q primary Aβ42, 2LFM Aβ40 control, 1IYT rejected as apolar/helical; RCSB-grounded). Added reproducible `scripts/stage1_inputs/fetch_antigen_templates.sh` → fetched 10 antigen/reference mmCIFs to `data/raw/antigen/coords/` (git-ignored; manifest in `coords/`). **Discrepancy found + resolved:** PDB **5MY4** (R-ELIFE "D3" homology ref) is actually anti-pyroglutamate-Aβ Fab c#17 (pE3-12), not a full-length N-terminal binder → pinned the exact R-ELIFE sentence, added 5MY4 identity caveat, opened **OQ-7** (expand pose-ensemble homology set with 6CO3/5CSZ/3BKJ/3D6). No campaign-parameter changes.
- **2026-06-01** — Phase 0 executed (`00_init.sh`): repo tree, git repo, coordination scaffold, `db/schema.sql`. Built `lecam` env from conda-forge/bioconda after finding CC wheelhouse incompatible with login-node glibc 2.28 (D-007). Initialized DuckDB ledger. **Stage 1:** sourced+verified lecanemab Fv (KEGG D11678 ↔ patent US9573994B2; D-008) → `data/raw/lecanemab_fv.fasta`; ANARCI-numbered (IMGT/Kabat/Chothia) + CDR/Vernier map (`scripts/stage1_inputs/number_fv.py` → `data/interim/fv_numbering/`); identified antigen templates (`data/raw/antigen/antigen_templates.md`); extracted B1–B7 sentences (`docs/sources/`). Relaxed `.claude/settings.json` deny-list to permit package installs (kept rm-rf/sudo/apt/shutdown blocks).
- **2026-05-30** — Project created. Authored `CLAUDE.md`, `PROJECT_STATUS.md`, `DEVELOPMENT_PLAN.md`, `HANDOFF.md`, and `scripts/stage1_inputs/00_init.sh`. Strategy reframe (avidity + selectivity, not monovalent KD) and 8-stage plan locked (D-001…D-005). Adopted multi-cluster git-coordination (D-006); set project root to `/global/project/hpcg6049/lecanemab-am` and GitHub remote `MaryamTabasinezhad/Lecanemab_affinity_maturation`.
