# PROJECT_STATUS.md — lecanemab-am

**Last updated:** 2026-06-04  ·  **Updated by:** Hamid (with Claude)  ·  **Phase:** Stage 4 T1 generated + scored by **2 independent scorers** (Boltz-2 ipSAE + Rosetta flex_ddG); all binding-neutral
**GitHub:** `git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git`  ·  **Project root:** `/global/project/hpcg6049/lecanemab-am` (Frontenac)  ·  **Coordinator:** Frontenac · **Workers:** none active yet

---

## Snapshot

Phase 0 scaffold **executed** on Frontenac (`00_init.sh`): full repo tree + git repo + coordination layer + `db/schema.sql`; `lecam` env built (conda-forge; D-007); DuckDB ledger initialized. **Stage 1 deliverables:** lecanemab Fv sourced & cross-verified (D-008) + ANARCI-numbered; antigen templates identified, **coordinates fetched** (D-009 monomer template resolved), B1–B7 extracted. While fetching, found + resolved a load-bearing reference discrepancy — **5MY4 is anti-pyroGlu-Aβ Fab c#17, not "D3"** (OQ-7).
Immediate next action: **PI decision on OQ-7** (epitope-homology template set); then Phase-0 env mapping (`lecam-*` → existing `colabfold`/`mpnn`/`rfdiffusion`/`BindCraft`) + A100 smoke tests; then Stage 2 (Fv model + multi-seed co-fold).

---

## Stage checklist

| Stage | Title | Status |
|---|---|---|
| 0 | Provisioning (repo, envs, HPC paths, ledger) | ◐ scaffold+ledger+`lecam`+`lecam-ab`+`lecam-fold`+`lecam-chai` built; **Boltz-2 A100-verified** (R-MODULES resolved); build-needed `lecam-dev`/AF3 + remaining smoke tests (Chai/ColabFold/RFdiffusion/BindCraft) |
| 1 | Inputs, Targets & Objective Lock-In | ◐ Fv+CDRs+antigens+B1–B7 done; monomer template resolved (D-009) + coords fetched; metrics thresholds await Stage-2 baseline; OQ-7 homology-set open |
| 2 | Structural Modeling & Conformational Ensembles | ☑ **complete**: 2.1 Fv model; 2.2 co-fold (ipSAE Fv-Aβ 0.53±0.26); 2.4 pose-cluster (family 68%, epitope Aβ 1-11/13-15, CDR-H3 paratope, OQ-1 informed); 2.3 MD → **B3 confirmed** (Aβ N-term flexible: RMSF 2.1Å, 98% coil; core 6-11 ordered). (AlphaFlow optional.) |
| 3 | Paratope Mapping & Design-Space Definition | ☐ |
| 4 | Variant Generation (multi-track) | ◐ **T1 done** (3 framework mutants, scored, binding-neutral). **T2 ProteinMPNN: 1st pass — finding:** vanilla full-CDR redesign rewrites 27-35/56 CDR positions (too aggressive → would erode selectivity, guardrail 1); **0 registered**, needs constraining (PI decision, see `results/stage4/t2-20260604/T2_FINDING.md`). T3/T4 not started |
| 5 | In Silico Affinity Scoring & Consensus Ranking | ◐ **2 independent scorers live**: Boltz-2 Δ-ipSAE + Rosetta **flex_ddG** (`lecam-rosetta`, PyRosetta). Ran both on T1 → consensus **binding-neutral** (D-004 met). FoldX/AbLIFT optional add-ons |
| 6 | Selectivity Counter-Design, Humanness & Developability | ☐ |
| 7 | Format, Valency & Delivery Engineering | ☐ |
| 8 | Experimental Validation & Active-Learning Loop | ☐ |

Legend: ☐ not started · ◐ in progress · ☑ done · ⊘ blocked

---

## Now / Next / Blocked

**Done (2026-06-01):** Phase-0 scaffold (`00_init.sh`); `lecam` env built (conda-forge/bioconda); DuckDB ledger initialized (`variants`, 27 cols); lecanemab Fv sourced+verified+ANARCI-numbered (3 schemes, CDRs+Vernier); antigen templates identified; B1–B7 source sentences extracted.

**Next (immediate):**
1. ~~PI decision on OQ-7~~ **DONE (D-010: homology set 6CO3/5CSZ/3BKJ/4HIX; 5MY4 weak proxy).**
2. Set `configs/metrics.yaml` thresholds + WT references once a Stage-2 WT baseline exists (currently TODO).
3. ~~Pick Aβ-monomer counter-target template~~ **DONE (D-009: 1Z0Q primary, 2LFM Aβ40 control).**
4. Pin exact B2 (>10⁶ selectivity, R-ANA) sentence (paywalled). B5 D3/5MY4 sentence **pinned 2026-06-03**; R-REV "no co-structure" sentence still to pin.
4. Phase-0 finish: ~~env mapping~~ **DONE**; ~~`lecam-ab`~~ **BUILT**; ~~`lecam-fold`/Boltz-2 + `lecam-chai`/Chai-1~~ **BUILT** (weights cached on scratch). Remaining **builds** = `lecam-dev` (developability), AF3 container, dedicated `lecam-rosetta`/`-md`, +RFantibody/LigandMPNN, BioPhi/Sapiens (own env); **A100 GPU smoke tests** (Boltz-2/Chai-1/ColabFold/RFdiffusion/BindCraft 1-job each) + confirm SLURM module names.
5. ~~Boltz-2 A100 smoke test~~ **DONE** (job 11542978, ptm 0.909; R-MODULES resolved). Remaining smoke tests: Chai-1, ColabFold, RFdiffusion, BindCraft.
6. Begin Stage 2: Fv model (ImmuneBuilder/IgFold via `lecam-ab`) + multi-seed Boltz-2 co-fold (`lecam-fold`) against the protofibril epitope (D-010 homology ensemble).

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
| D-010 | 2026-06-03 | Epitope-homology pose-ensemble set = **6CO3 (aducanumab), 5CSZ (gantenerumab), 3BKJ (WO2 1-16), 4HIX (3D6)**; **5MY4 demoted to weak proxy** | 5MY4 is anti-pyroGlu pE3-12 (verified RCSB), not lecanemab's full-length N-term epitope; full-length N-terminal Fabs match the 1–16 window (D-002 ensemble) | `docs/decisions/D-010-...md`; resolves OQ-7 |

---

## Open questions / risks

- **OQ-1 — epitope register.** **INFORMED 2026-06-03 (Stage 2.4, 25-pose ensemble):** consensus Fv footprint on Aβ = positions **1–11, 13, 14, 15** (core 2–10 at 100%); this covers **both** the literature "3–7" register (3-7 all 100%) **and** the internal B6 hotspots (Y10/E11/H13/H14/Q15 in consensus; K16 not) → neither contradicted; broad N-terminal footprint. Per D-002 still treated as a **hypothesis set**, not locked. `results/stage2/cofold-wt-Abeta1-16-11544623/pose_hypotheses.json`. (iptm overconfident; confirm flexibility in 2.3 MD.)
- **OQ-2 — display platform.** Yeast surface display vs phage; protofibril reagent prep, stability, and immobilization for counter-selection (Stage 8 dependency).
- **OQ-3 — avidity metric.** Define a concrete valency-aware "avidity-adjusted affinity" score for in-silico use (Stage 6).
- **OQ-4 — Fc / ARIA scope.** Decide whether Fc effector engineering is in-scope (currently optional, Stage 7).
- **R-ENV — tooling conflicts.** AF3 / Boltz-2 / RFantibody / BindCraft likely need isolated envs or containers; resolve at Phase 0.
- ~~**R-MODULES — HPC module names.**~~ **RESOLVED 2026-06-03** (Boltz-2 A100 smoke test, job 11542978): A100 node driver 595.58.03 (CUDA 13.2); torch-bundled-CUDA tools need **no system CUDA module**; **no `--partition`** flag (SLURM auto-routes `gpu:a100` to `gpubase_*`). Recorded in `slurm/_template.sbatch`. (Only revisit if a tool needs system-CUDA compilation, or for worker clusters.)
- **OQ-5 — worker clusters.** Which clusters to hire (Narval / Nibi candidates from prior project) and when; activate via `clusters/<cluster>.env` + `clusters/<cluster>/CLAUDE.md`.
- **OQ-6 — Globus endpoints.** Confirm per-cluster Globus endpoint UUIDs + base paths for `lecanemab-am` before any large transfer (`coordination/globus/endpoints.md`).
- ~~**OQ-7 — epitope homology template set.**~~ **RESOLVED 2026-06-03 → D-010** (PI sign-off): primary homology set = 6CO3/5CSZ/3BKJ/4HIX (full-length N-terminal anti-Aβ Fabs); 5MY4 demoted to annotated weak proxy. Coordinates fetched. Feeds Stage-2/3 pose ensemble + OQ-1.

---

## Environment & data status

| Item | Status |
|---|---|
| Repo skeleton | ☑ created (`00_init.sh`) |
| Git remote (GitHub) | ☑ set (`origin`, SSH auth OK as `hamidghaedi`) |
| Coordination scaffold (`clusters/`, `coordination/`) | ☑ created |
| Conda envs | ◐ **mapped 2026-06-03** (`docs/env/env_mapping.md`): `lecam`✅; **`lecam-ab`✅** (ImmuneBuilder/IgFold/AntiBERTy/AbLang2); **`lecam-fold`✅ Boltz-2** + **`lecam-chai`✅ Chai-1** (weights cached on scratch; GPU smoke tests owed); design via existing `mpnn`/`rfd_clean`/`rfdiffusion`/`SE3nv`/`BindCraft`; AF2 via `colabfold`; PyRosetta via `BindCraft`. **Build-needed:** `lecam-dev`, dedicated `lecam-rosetta`/`-md`; +RFantibody/LigandMPNN; AF3 container; BioPhi/Sapiens (own env) |
| DuckDB ledger | ☑ initialized + **3 T1 variants loaded** (`db/variants.duckdb`; git-shared `db/exports/variants.csv`) |
| Lecanemab Fv sequence | ☑ sourced + verified (2 sources) + ANARCI-numbered (IMGT/Kabat/Chothia) + CDRs/Vernier |
| Antigen templates | ◐ IDs identified + **coords fetched** (`data/raw/antigen/coords/`, git-ignored); monomer template **resolved (D-009)**; EMDB maps deferred (Globus); **OQ-7** homology-set open |
| `docs/sources/` extracts (B1–B7) | ◐ written; **B5 D3/5MY4 sentence pinned + 5MY4 identity caveat (OQ-7)**; B2 + R-REV sentences still flagged |
| SLURM templates verified on Frontenac | ☑ verified 2026-06-03 (Boltz-2 A100 job 11542978; no --partition, no CUDA module) |
| Worker clusters activated | ☐ none (Frontenac only) |

---

## Changelog

- **2026-06-04 (c)** — **T2 ProteinMPNN first pass (reused `../protein/ProteinMPNN` + `mpnn` env).** `scripts/stage4_gen/t2_cdr_proteinmpnn.py`: vanilla MPNN CDR redesign on the Fv–Aβ complex (Aβ+framework fixed, 6 IMGT CDRs designable, 96 seqs). **Finding: every design rewrites 27–35/56 CDR positions** (~55%) → not conservative AM; would erode conformational selectivity (guardrail 1). **0 registered** (by design); needs constraining — PI decision among {fix-H3+WT-bias, conservative point-muts, or aggressive+counter-screen}. → `results/stage4/t2-20260604/T2_FINDING.md`. Raw designs kept (not in ledger).
- **2026-06-04 (b)** — Built **`lecam-rosetta`** (PyRosetta 2026.21 via pip, thread+serialization build) and added **flex_ddG** as the 2nd independent scorer (D-004). PyRosetta-driven flex_ddG (no compiled rosetta_scripts binary): `scripts/_tools/flexddg/` (XML + `flexddg_run.py` + `aggregate_flexddg.py`), CPU array `slurm/stage5_flexddg.sbatch` (job 11675128, 15 traj). **ΔΔG (zemu-GAM kcal): HC:T70S −0.00±0.03, LC:A17D +0.06±0.13, HC:S24A +0.10±0.10 — all binding-neutral**, agreeing with Boltz-2 Δ-ipSAE. **2-scorer consensus: T1 framework mutants are binding-neutral** (expected — interface-distal). Ledger `flexddg_kcal` set. → `results/stage5/t1_consensus_scores.json`. Caveat: flex_ddG REDUCED (nstruct=5, backrub=10000) — fine here (ddG~0); use full 35/35000 for CDR/interface muts.
- **2026-06-04** — **Scored the 3 T1 variants** (Boltz-2 multi-seed co-fold vs Aβ1-16, A100 array job 11673009, 5 min; `slurm/stage4_score_cofold.sbatch` + `make_variant_yamls.py`/`collect_scores.py`, reusing the WT 2.2 harness). Δ-ipSAE vs WT (0.531): HC:S24A −0.077, HC:T70S −0.105, LC:A17D −0.136 — **all neutral-within-noise** (ipSAE std ~0.25), the expected outcome for CDR-preserving framework changes (none improves binding; T1 value = developability/humanness, Stage 6). Ledger updated (boltz_ipsae/iptm, status=scored, stage_reached=5; `db/exports/variants.csv`). → `results/stage4/t1_scores_summary.json`. Closes the generate→score loop. Caveat: in-silico ipSAE = soft prioritization only (guardrail 5).
- **2026-06-03 (k)** — **Stage 4 T1 started** (CDR-preserving framework/Vernier; D-003). `scripts/stage4_gen/t1_framework_lm.py` (AbLang2 paired, OAS prior): per-position log-odds (logit[mut]−logit[wt], normalization-free → guardrail 4); all IMGT CDRs protected; Vernier tagged. **Finding: lecanemab framework is already strongly OAS-consistent** — only 3 framework positions clear log-odds≥0.5: **LC:A17D (2.92), HC:T70S (1.11), HC:S24A (1.09)** → registered LEC-AM-T1-0001..3 (`db/variants.duckdb` + `db/exports/variants.csv`; FASTA/manifest in `results/stage4/t1-20260603/`). The AbLIFT/Rosetta VH-VL interface-redesign half of T1 is pending `lecam-rosetta`. Next: score T1 (Boltz-2 Δ-ipSAE vs WT) + Stage-6 developability/humanness; T2/T3/T4.
- **2026-06-03 (j)** — Built **`lecam-md`** (OpenMM 8.2 CUDA + pdbfixer + mdtraj; A100-verified) and ran **Stage 2.3 MD** (`scripts/stage2_model/md_flexibility.py`, `slurm/stage2_md.sbatch`, A100 job 11570164, 5 ns implicit GBn2, Fv-framework-restrained). **B3 CONFIRMED:** engaged Aβ N-terminus (1-5) stays flexible — RMSF **2.10 Å**, **97.5% coil** — while the contacted core (6-11) is most ordered (RMSF 1.04 Å); C-term (12-16) RMSF 2.09 Å; CDR-H3 RMSF 0.77 Å. → `results/stage2/md-flex-11570164/md_flexibility.json`. **Stage 2 now complete** (gate + flexible-N). Caveat: 5 ns/implicit/single-pose → qualitative.
- **2026-06-03 (i)** — **ipSAE on the 25 WT co-fold poses** (`scripts/stage2_model/compute_ipsae.py` wrapping official `scripts/_tools/ipsae.py` v4, pae10/dist10): **Fv–Aβ interface ipSAE = 0.53±0.26 (range 0.07–0.88)** vs intra-Fv VH–VL ipSAE 0.96. Confirms the iptm-0.96 caveat — interface confidence is moderate and **high-variance** (the real pose uncertainty iptm masked). Recorded as the headline M1 WT baseline in `metrics.yaml` (gate on Δ-ipSAE, not absolute iptm). → `results/stage2/cofold-wt-Abeta1-16-11544623/ipsae_summary.json`.
- **2026-06-03 (h)** — **Stage 2.4 — pose clustering + epitope-register (Stage-2 GATE MET)** (`scripts/stage2_model/analyze_poses.py`, env `lecam`/biotite+scipy): analyzed the 25 co-fold poses → consensus epitope Aβ **1-11,13,14,15** (core 2-10 @100%); **OQ-1 informed** — footprint covers both lit "3-7" and B6 hotspots (Y10/E11/H13/H14/Q15; not K16). Dominant pose family **68%** (17/25), footprint Jaccard 0.864. Paratope **CDR-H3-led** (H3=10 residues, +L3/L1/H1/H2 +Vernier-flank FR). Gate: self-consistent family ✅, N-terminal/B3 ✅, not-contradicting-B6 ✅ — with documented uncertainty (iptm overconfident; pose=hypothesis, D-002). → `results/stage2/cofold-wt-Abeta1-16-11544623/pose_hypotheses.json`. Remaining Stage 2: 2.3 MD/AlphaFlow flexible-N ensemble (`lecam-md`) + ipSAE.
- **2026-06-03 (g)** — **Stage 2.2 — multi-seed Boltz-2 co-fold** WT Fv + Aβ N-terminal **1-16** peptide (`slurm/stage2_cofold.sbatch`, `configs/stage2/cofold_wt_Abeta1-16.yaml`, A100 job 11544623, 5 min): 5 seeds × 5 samples = **25 models kept** (scratch) → WT baseline **iptm 0.961±0.019, ptm 0.974, plddt 0.944**; chain-pair iptm shows the peptide contacts **both VH (0.94) and VL (0.93)** (CDR-spanning paratope). Summary+manifest → `results/stage2/cofold-wt-Abeta1-16-11544623/`. WT baseline recorded in `metrics.yaml` M1 (as reference, not threshold). **Caveat:** Ab-Ag iptm is overconfident (guardrail 2/R-EGFR) → use Δ-vs-WT + ipSAE, not absolute. **Next:** 2.4 cluster the 25 poses + check epitope register vs B6 (Stage-2 gate, OQ-1); compute ipSAE; 2.3 MD ensemble (needs `lecam-md`).
- **2026-06-03 (f)** — **Stage 2 started — 2.1 WT Fv model** (`scripts/stage2_model/model_fv_wt.py`, env `lecam-ab`/ABodyBuilder2 1.2): refined Fv from the Stage-1 VH/VL → `results/stage2/fv-wt-20260603/` (+ `data/interim/fv_model.pdb`). Geometry (predicted error, Å): framework-H **0.25**, CDR-H3 **0.82 mean / 2.44 max** — CDR-H3 least certain as expected (guardrail 2), the loop most needing the pose ensemble. New runtime gotcha solved: CC StdEnv's `LD_LIBRARY_PATH` forces system libstdc++ → OpenMM `GLIBCXX_3.4.29` import error; fix = force `LD_LIBRARY_PATH=$CONDA_PREFIX/lib` (docs/env + memory). Next: 2.2 multi-seed Boltz-2 co-fold vs protofibril epitope (D-010 homology ensemble), 2.3 MD ensemble (needs `lecam-md`).
- **2026-06-03 (e)** — **Boltz-2 A100 GPU smoke test PASSED** (job 11542978, frnt154, ~1 min): single-seq GB1 fold from offline scratch weights → valid 56-res structure, ptm 0.909 / complex_plddt 0.94 (`slurm/smoke_boltz2.sbatch` + `slurm/smoke/boltz2_gb1.yaml`). Fixed: Boltz-2's GPU forward path **requires the `boltz[cuda]` extra** (cuequivariance kernels) — pip resolved torch 2.12 cu130 (build script + versions updated). **R-MODULES resolved:** A100 driver 595.58.03 (CUDA 13.2), no system CUDA module needed, no `--partition` (auto-routes to gpubase_*); recorded in `slurm/_template.sbatch`.
- **2026-06-03 (d)** — Built **`lecam-fold`** (Boltz-2 2.2.1) and **`lecam-chai`** (Chai-1 0.6.1) co-folding oracles (`scripts/env/build_lecam-{fold,chai}.frontenac.sh`; versions in `docs/env/lecam-{fold,chai}.versions.txt`). Both: py3.11, CUDA torch 2.6 cu124, numpy<2; imports verified, `pip check` clean. Weights pre-fetched to **scratch** (login node, since compute nodes are offline): Boltz `$SCRATCH/cache/boltz` 7.9G (struct + **affinity** model + CCD), Chai `$SCRATCH/cache/chai` 6.6G (6 components + traced ESM2-3B + conformers). **Split into two envs** because chai_lab conflicts with Boltz on requests/protobuf/pandas/rdkit (§5 isolation rule). Created the scratch tree (`$SCRATCH_ROOT`); cache-path vars added to `clusters/frontenac.env`. **Owed:** A100 GPU fold smoke tests + AF3 container.
- **2026-06-03 (c)** — Built **`lecam-ab`** env (`scripts/env/build_lecam-ab.frontenac.sh`; versions in `docs/env/lecam-ab.versions.txt`): ImmuneBuilder/ABodyBuilder2, IgFold, AntiBERTy, AbLang2 — all verified loading (py3.10, CPU torch 2.5.1, numpy 2.2.6; weights cached on login node). Resolved Frontenac pip hazards: CC wheelhouse hijack (`PIP_CONFIG_FILE=/dev/null`) **and** the CC `_manylinux` shim on `PYTHONPATH` that disabled manylinux wheels (`env -u PYTHONPATH`); pinned transformers 4.40.2 (antiberty breaks on 5.x) and torch 2.5.1 (2.6 weights_only break vs IgFold ckpts). **Deferred:** BioPhi/Sapiens humanness → own env (fairseq/Flask conflicts).
- **2026-06-03 (b)** — Phase-0 **env mapping** (`docs/env/env_mapping.md`): inventoried existing conda envs (verified via `conda list`) and mapped to `lecam-*` roles in `clusters/frontenac.env`. Covered now: orchestration (`lecam`), design (ProteinMPNN`mpnn`, RFdiffusion`rfd_clean`/`rfdiffusion`/`SE3nv`, BindCraft+ColabDesign`BindCraft`), AF2 oracle (`colabfold`+5.3G weights), PyRosetta (in `BindCraft`), OpenMM (interim). Located repos (ProteinMPNN, BindCraft) + ColabFold weights. **Build-needed:** `lecam-ab`, `lecam-fold`(Boltz-2/Chai-1), `lecam-dev`, dedicated `lecam-rosetta`(flex_ddG/FoldX)/`-md`; +RFantibody/LigandMPNN/SolubleMPNN. A100 smoke tests still owed.
- **2026-06-03 (a)** — Stage-1/2 prep: resolved Aβ-monomer counter-target template (**D-009**: 1Z0Q primary Aβ42, 2LFM Aβ40 control, 1IYT rejected as apolar/helical; RCSB-grounded). Added reproducible `scripts/stage1_inputs/fetch_antigen_templates.sh` → fetched antigen/reference mmCIFs to `data/raw/antigen/coords/` (git-ignored; manifest in `coords/`). **Discrepancy found:** PDB **5MY4** (R-ELIFE "D3" homology ref) is actually anti-pyroglutamate-Aβ Fab c#17 (pE3-12), not a full-length N-terminal binder → pinned the exact R-ELIFE sentence + added 5MY4 identity caveat. **OQ-7 resolved same day (PI) → D-010:** primary epitope-homology set = 6CO3 (aducanumab) / 5CSZ (gantenerumab) / 3BKJ (WO2 1-16) / 4HIX (3D6); 5MY4 demoted to weak proxy; 4 new refs fetched. No campaign-parameter changes.
- **2026-06-01** — Phase 0 executed (`00_init.sh`): repo tree, git repo, coordination scaffold, `db/schema.sql`. Built `lecam` env from conda-forge/bioconda after finding CC wheelhouse incompatible with login-node glibc 2.28 (D-007). Initialized DuckDB ledger. **Stage 1:** sourced+verified lecanemab Fv (KEGG D11678 ↔ patent US9573994B2; D-008) → `data/raw/lecanemab_fv.fasta`; ANARCI-numbered (IMGT/Kabat/Chothia) + CDR/Vernier map (`scripts/stage1_inputs/number_fv.py` → `data/interim/fv_numbering/`); identified antigen templates (`data/raw/antigen/antigen_templates.md`); extracted B1–B7 sentences (`docs/sources/`). Relaxed `.claude/settings.json` deny-list to permit package installs (kept rm-rf/sudo/apt/shutdown blocks).
- **2026-05-30** — Project created. Authored `CLAUDE.md`, `PROJECT_STATUS.md`, `DEVELOPMENT_PLAN.md`, `HANDOFF.md`, and `scripts/stage1_inputs/00_init.sh`. Strategy reframe (avidity + selectivity, not monovalent KD) and 8-stage plan locked (D-001…D-005). Adopted multi-cluster git-coordination (D-006); set project root to `/global/project/hpcg6049/lecanemab-am` and GitHub remote `MaryamTabasinezhad/Lecanemab_affinity_maturation`.
