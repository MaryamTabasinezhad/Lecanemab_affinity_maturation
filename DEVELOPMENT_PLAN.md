# DEVELOPMENT_PLAN.md — Lecanemab AM Pipeline (8 stages)

**Repo:** `lecanemab-am`  ·  Companion to `@CLAUDE.md` (context/guardrails) and `@PROJECT_STATUS.md` (live state).

This plan operationalizes the objective in `CLAUDE.md §2`: **maximize avidity-adjusted affinity for Aβ protofibrils/oligomers while preserving or increasing selectivity vs (a) monomer and (b) fixed-N-terminus/CAA fibrils, co-optimized with developability.** Every stage runs WT lecanemab as the reference and reports deltas vs WT.

---

## Pipeline flow

```
[1] Inputs + objective
        │
[2] Fv model + Fv–epitope pose ensemble + flexible-N-terminus MD ensemble
        │
[3] Paratope map → editable vs protected positions
        │
[4] Variant generation ── T1 framework/interface (AbLIFT, CDR-preserving)   ← start here
                         ├ T2 CDR redesign (MPNN / RFantibody)
                         ├ T3 CDR gradient opt (BindCraft / ColabDesign)
                         └ T4 LM-guided point mutations (AntiBERTy/AbLang2/ESM-C)
        │
[5] Affinity scoring (multi-sample ipTM+ipSAE consensus + ensemble ΔΔG) → shortlist
        │
[6] GATE: selectivity counter-design (vs monomer + CAA-fibril) + humanness + developability
        │
[7] Format/valency/delivery (multivalent / TfR1 bispecific / Fc)
        │
[8] Wet-lab: display dual-selection → BLI/SPR → measured KD → re-weight rankers ──┐
        └──────────────────────── active-learning loop back to [4] ─────────────┘
```

## Global definition of done (per round)

≥1 variant that (i) improves predicted + measured protofibril engagement over WT, (ii) keeps the monomer **and** CAA-fibril counter-screens negative, (iii) is no worse than WT on humanness and developability. Otherwise iterate from Stage 4 with Stage-8 feedback.

---

## Phase 0 — Provisioning (prerequisite, not a numbered stage)

- Create repo skeleton at `/global/project/hpcg6049/lecanemab-am` (`CLAUDE.md §6`); set git remote `git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git` (branch `main`); first commit + push. (`scripts/stage1_inputs/00_init.sh` does all of this.)
- Create the **coordination scaffold**: `clusters/` (frontenac.env + frontenac/CLAUDE.md, worker templates, narval/nibi env stubs) and `coordination/` (COORDINATION.md, DASHBOARD.md, inbox/, manifests/, globus/).
- Build conda envs (`CLAUDE.md §5`); record pinned versions + commit hashes in `docs/env/`.
- Resolve env/container isolation for AF3 / Boltz-2 / RFantibody / BindCraft.
- Initialize DuckDB ledger (schema below).
- Confirm Frontenac module names + the portable sbatch template (`slurm/`).
- **Gate:** repo pushes to GitHub; coordinator self-identifies from hostname; every env imports cleanly; ledger initializes; a 1-design BindCraft and a 1-sample Boltz-2 smoke test complete on A100.

---

## Stage 1 — Inputs, Targets & Objective Lock-In

- **Objective:** assemble verified inputs and freeze the objective, metrics, and counter-targets so nothing downstream is ambiguous.
- **Inputs:** lecanemab INN/Thera-SAbDab/IMGT/patent; antigen templates (`CLAUDE.md §4`).
- **Tools (env):** ANARCI/IMGT numbering, SAbDab, biopython/biotite (`lecam`, `lecam-ab`).
- **Method:**
  1. Retrieve lecanemab VH/VL; **cross-verify against ≥2 independent sources**; ANARCI-number (IMGT + Kabat + Chothia); annotate CDRs and Vernier positions.
  2. Curate antigen set: **target** = Aβ42 protofibril/fibril (type I/II/Arctic); **counter-targets** = Aβ monomer/peptide + fixed-N/CAA-type Aβ40 fibril.
  3. Write `configs/objective.yaml` + `configs/metrics.yaml` (the 5 success metrics, thresholds, WT references).
  4. Extract load-bearing source sentences (B1–B7) → `docs/sources/`.
- **HPC:** Frontenac login / CPU node (no GPU needed).
- **Outputs:** `data/raw/lecanemab_fv.fasta`, CDR/Vernier map, `data/raw/antigen/`, `objective.yaml`, `metrics.yaml`.
- **Gate:** Fv verified (≥2 sources); CDRs + Vernier annotated; target + both counter-targets defined; objective/metrics committed.
- **Audit:** `docs/sources/` entries link every fact to an exact sentence; provenance for the Fv recorded.

---

## Stage 2 — Structural Modeling & Conformational Ensembles

- **Objective:** build an Fv model, a **set** of Fv–epitope pose hypotheses, and a flexible-N-terminus ensemble in aggregate context — not a single static complex.
- **Inputs:** Stage-1 Fv + antigen set.
- **Tools (env):** ImmuneBuilder (ABodyBuilder2) / IgFold [Fv]; Boltz-2 / AlphaFold3 / Chai-1 [complex, multi-seed]; OpenMM / AlphaFlow [ensemble] (`lecam-ab`, `lecam-fold`, `lecam-md`).
- **Method:**
  1. Model the Fv; validate geometry (CDR-H3 caution).
  2. Co-fold Fv against the protofibril epitope across **multiple seeds**; keep all samples.
  3. Generate an MD / AlphaFlow ensemble of the Aβ N-terminus + CDR loops; confirm the engaged epitope presents a **flexible N-terminus** (consistent with B3).
  4. Cluster poses → retain top-k **pose hypotheses** with confidence + a recorded uncertainty estimate.
- **HPC:** A100 SLURM array (folding + MD).
- **Outputs:** `data/interim/fv_model.pdb`, `complex_poses/` (ranked, multi-seed), `ensembles/`, `pose_hypotheses.json`.
- **Gate:** ≥1 self-consistent pose family consistent with B3 and not contradicting B6; pose uncertainty logged.
- **Audit:** per-run `manifest.json` (model versions, seeds, sample count).

---

## Stage 3 — Paratope Mapping & Design-Space Definition

- **Objective:** decide which positions to vary and which to protect.
- **Inputs:** Stage-2 pose ensemble.
- **Tools (env):** Paragraph/Parapred [paratope]; Arpeggio/PLIP [contacts]; Rosetta alanine scan / `flex_ddG` hotspot scan (`lecam-ab`, `lecam-rosetta`).
- **Method:**
  1. Map paratope contacts **across the pose ensemble** (use consensus contacts, not one pose).
  2. Classify positions: epitope-contact CDR · Vernier/framework · VH-VL interface · structural core.
  3. Define the **editable set** (with rationale per position) and the **protected set** (conformational-paratope core).
- **HPC:** light GPU/CPU.
- **Outputs:** `position_classes.csv`, `editable_positions.yaml`, `hotspot_ranking.csv`.
- **Gate:** editable set defined with per-position rationale; paratope core flagged protected.
- **Audit:** every contact referenced to specific pose IDs.

---

## Stage 4 — Variant Generation (multi-track)

- **Objective:** generate diverse candidate Fv variants across complementary tracks; register all in the ledger.
- **Inputs:** Stage-3 editable/protected sets + pose ensemble.
- **Tracks / tools (env):**
  - **T1 — Framework/Vernier + VH-VL interface (CDR-preserving). START HERE (D-003).** AbLIFT + Rosetta interface redesign; evolutionary priors from OAS / MMseqs2. *Lowest risk to the conformational paratope.*
  - **T2 — CDR redesign.** ProteinMPNN / SolubleMPNN / LigandMPNN; RFantibody / DiffAb, restricted to editable CDR positions.
  - **T3 — CDR gradient optimization.** BindCraft / ColabDesign partial hallucination on the Fv–epitope complex (AF2-M backprop on ipTM/PAE/contacts) — your existing A100 engine.
  - **T4 — LM-guided point mutations.** AntiBERTy / AbLang2 / ESM-C (MLDE-style) with a humanness pre-screen.
- **Method:** each track emits sequences → dedup → **register in ledger** with `track`, `mutations`, `n_mut`, `edit_dist_to_wt`. Enforce conservative edit-distance caps on the paratope core.
- **HPC:** A100 arrays (BindCraft, RFantibody, MPNN batches).
- **Outputs:** variants in ledger; per-track FASTA in `results/stage4/<run-id>/`.
- **Gate:** target N variants per track; all CDR edits within the editable set; paratope-core caps respected.
- **Audit:** per-track config + seeds in manifests.

---

## Stage 5 — In Silico Affinity Scoring & Consensus Ranking

- **Objective:** score each variant's protofibril-complex confidence + ΔΔG and produce a consensus rank.
- **Inputs:** Stage-4 variants + Stage-2 pose ensemble.
- **Tools (env):** Boltz-2 / AF3 / Chai-1 re-fold (multi-sample) → ipTM + ipSAE/iPAE; Rosetta `flex_ddG` / FoldX (ensemble-averaged ΔΔG) (`lecam-fold`, `lecam-rosetta`).
- **Method:**
  1. Re-predict each variant–epitope complex with *k* diffusion samples (store all); compute Δ vs WT for each metric.
  2. Compute ensemble-averaged ΔΔG.
  3. **Rank by consensus** (rank-intersection of ipTM, ipSAE, ΔΔG) — not any single metric. **Exclude unnormalized ESM2 LL from ranking** (guardrail 4).
- **HPC:** A100 array — largest compute stage; size the array to variant count.
- **Outputs:** scored variants in ledger; `ranked_shortlist.csv`.
- **Gate:** shortlist = variants with consensus improvement over WT on **≥2 independent scorers**.
- **Audit:** all samples + seeds retained; metric definitions in `docs/`.

---

## Stage 6 — Selectivity Counter-Design, Humanness & Developability (the GATE)

- **Objective:** protect the mechanism — keep only variants that are *selectively* better and developable.
- **Inputs:** Stage-5 shortlist.
- **Tools (env):** counter-target re-scoring (Boltz-2/AF3 vs monomer + CAA-fibril); BioPhi/Sapiens OASis [humanness]; TAP/SAbDab-TAP, Aggrescan3D, NetSolP, SoluProt, DeepViscosity/DeepSCM, DE-STRESS [developability] (`lecam-dev`, `lecam-fold`).
- **Method:**
  1. **Selectivity:** for each variant compute `Δprotofibril − Δmonomer` and `Δprotofibril − ΔCAA-fibril`; keep only those **positive and ≥ WT** (negative/counter-design).
  2. **Humanness:** OASis percentile ≥ WT.
  3. **Developability:** not worse than WT; flag new charge patches, exposed hydrophobics, Aggrescan hotspots, and new glyco/deamidation/isomerization motifs.
- **HPC:** light GPU/CPU.
- **Outputs:** `selectivity_dev_report.csv`, `gated_panel.csv` (the testable set).
- **Gate:** variants failing selectivity **or** developability are rejected **regardless of affinity rank** (guardrail 1).
- **Audit:** per-variant counter-target scores + liability flags retained.

---

## Stage 7 — Format, Valency & Delivery Engineering

- **Objective:** convert affinity gains into functional avidity in a deliverable construct.
- **Inputs:** Stage-6 gated panel.
- **Tools / precedents (env):** multivalent reformatting (**Hexa-RmAb158** precedent, R-HEXA); **TfR1 BBB bispecific** (RmAb158-scFv8D3 precedent) — merges with your existing TfR1 arm; optional Fc effector engineering for the ARIA axis (`lecam-design`, `lecam-fold`).
- **Method:**
  1. Select top gated Fv(s).
  2. Design format(s): IgG1 · multivalent · tandem/bispecific with TfR1 arm.
  3. Re-model the full construct; sanity-check format stability + expression.
- **HPC:** A100 (full-construct folding).
- **Outputs:** construct designs + sequences, format rationale, full-construct models.
- **Gate:** format preserves Fv selectivity in silico; expression/developability sane.
- **Audit:** format choices logged as ADRs in `docs/decisions/`.

---

## Stage 8 — Experimental Validation & Active-Learning Loop

- **Objective:** test the gated panel, measure, and feed results back.
- **Inputs:** Stage-7 constructs / Stage-6 gated Fv panel.
- **Tools / assays:** yeast or phage display with **dual selection** (protofibril +, monomer −); BLI / SPR for KD·kon·koff to protofibril **plus monomer and CAA-fibril counter-screens** (Adaptyv-style); optional ephrin-independent neutralization/competition assays (`lecam` for analysis).
- **Method:**
  1. Synthesize the gated panel.
  2. Display + counter-select → rank-order survivors.
  3. BLI/SPR on survivors; record measured KD/kon/koff in the ledger.
  4. **Re-train / re-weight** the Stage-5 rankers on measured data → improves the next round (closes the loop; this is where your own data, not the public competition data, makes scoring predictive for a conformational amyloid epitope).
- **HPC:** analysis on Frontenac (login / CPU node); synthesis/assays external (wet-lab or service).
- **Outputs:** `measured_kd.csv` in ledger, round report, updated ranker weights.
- **Gate (round success):** ≥1 variant with improved protofibril KD/koff **and** negative monomer counter-screen → success; else iterate from Stage 4 with feedback.
- **Audit:** raw sensorgrams + fits archived; manifest links design → sequence → assay.

---

## Cross-cutting

### Variant ledger schema (DuckDB — `db/variants.duckdb`)

```sql
CREATE TABLE variants (
  variant_id        TEXT PRIMARY KEY,   -- e.g. LEC-AM-T1-0042
  parent            TEXT,               -- 'lecanemab_WT'
  track             TEXT,               -- T1 | T2 | T3 | T4
  chain             TEXT,               -- HC | LC | both
  mutations         TEXT,               -- 'HC:Y32F;LC:S56T' (IMGT numbering)
  n_mut             INTEGER,
  edit_dist_to_wt   INTEGER,
  -- Stage 5 (affinity, vs WT)
  boltz_iptm        DOUBLE,
  boltz_ipsae       DOUBLE,
  af3_iptm          DOUBLE,
  flexddg_kcal      DOUBLE,
  consensus_rank    INTEGER,
  -- Stage 6 (selectivity + developability)
  sel_monomer_delta DOUBLE,             -- Δprotofibril - Δmonomer  (want >0, >= WT)
  sel_cafib_delta   DOUBLE,             -- Δprotofibril - ΔCAA-fibril
  oasis_humanness   DOUBLE,
  agg3d_score       DOUBLE,
  netsolp           DOUBLE,
  viscosity_flag    BOOLEAN,
  tap_flags         TEXT,
  -- Stage 8 (experimental)
  kd_protofibril_M  DOUBLE,
  koff_protofibril  DOUBLE,
  monomer_screen    TEXT,               -- 'negative' (desired) | 'positive'
  -- provenance
  stage_reached     INTEGER,
  status            TEXT,               -- generated | scored | gated | rejected | tested | hit
  source_config     TEXT,               -- path to run config / manifest
  created_at        TIMESTAMP
);
```

### Naming conventions

- **variant_id:** `LEC-AM-<track>-<nnnn>` (e.g. `LEC-AM-T1-0042`).
- **mutations:** `<chain>:<WT><IMGTpos><MUT>` joined by `;` (e.g. `HC:Y32F;LC:S56T`).
- **runs:** `results/<stage>/<YYYYMMDD>-<short-git-sha>-<tag>/` each with `manifest.json`.

### Portable SLURM template (`slurm/_template.sbatch`)

Scripts are cluster-portable: they detect the cluster and `source clusters/<cluster>.env` for the account, GRES, walltime, and env name (never hard-code another cluster's values).

```bash
#!/bin/bash
#SBATCH --job-name=lecam
#SBATCH --output=%x-%A_%a.out
# Frontenac: account/GRES below; other clusters override via clusters/<cluster>.env.
#SBATCH --account=def-hpcg6049_gpu     # Frontenac default; see clusters/<cluster>.env
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8              # tune per tool
#SBATCH --mem=48G                      # tune per tool
#SBATCH --time=08:00:00                # tune per stage (workers may allow longer)
# NO --partition flag on Frontenac
# module load ...                      # CONFIRM module names per cluster before first submit
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
source "$REPO_ROOT/scripts/_detect_cluster.sh"     # sets $CLUSTER + sources clusters/$CLUSTER.env
# activate "$CONDA_ENV_*" for the stage, then run the stage script; write manifest.json.
```

### Multi-cluster execution

The compute-heavy stages (Stage 4 generation, Stage 5 scoring) are the natural parallelization points. The **coordinator (Frontenac)** splits the variant set into per-cluster TSV manifests (`coordination/manifests/manifest_stage<N>_<cluster>.tsv`), drops an inbox message with the exact command + output path, and each **worker** runs its slice and commits the scored rows + small CSVs back to git (large model samples stay on that cluster's scratch and move via Globus only if needed). The DuckDB ledger remains the single source of truth — workers report rows; the coordinator merges. Until a worker is hired, every stage runs on Frontenac.

### Active-learning loop

Each completed Stage-8 round writes measured KD into the ledger; Stage-5 rankers are re-fit on the accumulated (design → measured) pairs, then a new Stage-4 batch is generated biased toward the regions of sequence space that produced selective, developable hits. The loop is the mechanism that turns generic folding-model scores into a target-specific predictor for this conformational amyloid epitope — treat the first round's in-silico scores as weak priors, not ground truth.
