# CLAUDE.md — Lecanemab Computational Affinity Maturation

**Repo:** `lecanemab-am`  ·  **GitHub:** `git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git`
**Project root (Frontenac):** `/global/project/hpcg6049/lecanemab-am`  ·  **Coordinator:** Frontenac (CAC, Queen's), user `hpc6049`
**Owner:** Hamid  ·  **Last structural/strategy review:** 2026-05-30

> Persistent context for Claude Code. **Read in full before proposing code/configs/decisions.**
> **Multi-cluster repo — this repo is the coordination channel (see §0).**
> Imports: `@PROJECT_STATUS.md` `@DEVELOPMENT_PLAN.md` · per-cluster `@clusters/<cluster>/CLAUDE.md` · live `@coordination/DASHBOARD.md` `@coordination/COORDINATION.md`

---

## 0. Multi-cluster coordination (read at every session start)

This project runs **multiple Claude Code agents across SLURM clusters**, coordinated **only through this git repo** (no shared memory/API). The repo is the single source of truth — every instruction, status update, and result is a git commit. **Frontenac is the coordinator;** additional clusters are added as **workers** as they come online (none active yet — see `coordination/COORDINATION.md`).

### Identity — detect your cluster, then read its files
```bash
case "$(hostname -f)" in
  *frontenac*|frnt*) CLUSTER=frontenac ;;   # COORDINATOR
  *nibi*)            CLUSTER=nibi ;;         # worker (when activated)
  *narval*)          CLUSTER=narval ;;       # worker (when activated)
  *) echo "ERROR: unknown cluster: $(hostname -f)" >&2 ;;
esac
```
Then read `clusters/<CLUSTER>/CLAUDE.md` and `source clusters/<CLUSTER>.env` for that cluster's paths / SLURM / Globus.

### Session start (ALL clusters)
1. `git pull origin main` — get latest coordination state.
2. Read this `CLAUDE.md`, then `clusters/<cluster>/CLAUDE.md`.
3. Read `coordination/DASHBOARD.md` (status across clusters) + `coordination/COORDINATION.md` (rules/registry).
4. Check `coordination/inbox/<cluster>/` for messages.

### Session end (ALL clusters)
1. Update your row in `coordination/DASHBOARD.md` (+ ledger / PROJECT_STATUS if coordinator).
2. Delete inbox messages you have actioned.
3. Commit with a `[<cluster>] <message>` prefix; `git push origin main`.

### Communication rules
- The repo IS the channel. Messages → `coordination/inbox/<recipient>/`; batch work → `coordination/manifests/*.tsv`.
- **Large data (PDBs, model weights, samples, containers) moves via Globus, NOT git** (`coordination/globus/`).
- Each agent edits **only its own** dashboard row + its own inbox; the coordinator edits the summary lines. Workers never change campaign parameters without coordinator approval.
- All shared scripts use `set -euo pipefail`, absolute paths, and `source clusters/<cluster>.env`.

---

## 1. Mission

Run a **computational** affinity-maturation (AM) campaign on **lecanemab (Leqembi / BAN2401)** — the humanized IgG1 anti-Aβ-protofibril antibody (humanized mouse **mAb158**; BioArctic/Eisai) — and deliver a ranked, developability-filtered, experimentally-testable panel of matured Fv variants that improve engagement of soluble Aβ aggregates **without sacrificing conformational selectivity or developability**.

The pipeline is a funnel: in-silico generation/scoring → counter-selection + developability gates → small wet-lab panel (display + BLI/SPR) → measured KD fed back to re-weight the in-silico rankers (active learning).

---

## 2. THE design objective — read before proposing ANYTHING

**Do NOT optimize raw monovalent KD to the Aβ N-terminal epitope.** Lecanemab is, by design, *not* a high-monovalent-affinity binder:

- monovalent affinity is intentionally **weak**; therapeutic effect comes from **avidity for epitope-dense protofibrils / oligomers**;
- selectivity is **conformational** — it requires a **flexible, unstructured Aβ N-terminus** and largely spares fixed-N-terminus vascular / CAA Aβ40 fibrils (tied to its comparatively low ARIA-E).

A campaign that maximizes monovalent affinity can convert lecanemab into a monomer- and CAA-binding antibody → loss of the >10⁶-fold selectivity **and** the safety margin.

**Operational objective:** maximize **avidity-adjusted** affinity for Aβ **protofibrils / oligomers** while **preserving or increasing selectivity** against (a) Aβ monomer and (b) fixed-N-terminus / CAA-type fibrils, **co-optimized** with developability (stability, aggregation, viscosity, humanness).

**Success metrics (primary → guardrail):**
1. ↑ predicted protofibril-complex interface confidence (multi-sample Boltz-2/AF3 **ipTM + ipSAE**) vs WT lecanemab.
2. **Selectivity margin maintained:** `Δprotofibril − Δmonomer` and `Δprotofibril − ΔCAA-fibril` both **positive and ≥ WT**.
3. Developability not worse than WT (TAP flags, Aggrescan3D, NetSolP, viscosity).
4. Humanness preserved (BioPhi OASis percentile ≥ WT lecanemab).
5. **Experimental:** improved apparent KD / koff to protofibril by BLI **with monomer counter-screen negative**.

---

## 3. Critical biology (traceable — see §11 for keys)

| # | Load-bearing fact | Source |
|---|---|---|
| B1 | Lecanemab = humanized IgG1 from mouse **mAb158**; Aβ-protofibril-selective | R-NMR |
| B2 | **>10⁶-fold** selectivity for Aβ42 protofibril vs Aβ1-16 monomer | R-ANA |
| B3 | Conformational epitope in the **N-terminal region**; binding requires a **flexible / unstructured N-terminus** | R-TG, R-SD |
| B4 | **Spares fixed-N-terminus** (SwDI / meningeal CAA Aβ40) fibrils → links to low ARIA-E | R-TG |
| B5 | **No public lecanemab Fab–Aβ co-structure**; literature models it by similarity to antibody **D3 (PDB 5MY4)** | R-ELIFE, R-REV |
| B6 | Epitope **register is model-dependent**: internal hotspots Y10/E11/H13/H14/Q15/K16 vs lit "N-terminal, tolerant 3–7". Treat as a **hypothesis set**, never a fixed pose | R-ELIFE + internal |
| B7 | **Multivalency** (Hexa-RmAb158) raises binding strength to soluble aggregates → avidity is the functional lever | R-HEXA |

---

## 4. Project assets / inputs to source (Stage 1)

- **Lecanemab Fv (VH/VL):** retrieve from **Thera-SAbDab / IMGT mAb-DB / WHO-INN (lecanemab) / BioArctic–Eisai patents**; validate by IMGT numbering against ≥2 independent sources. **Do not hand-type from memory.**
- **Antigen / epitope context:**
  - *Target:* Aβ42 protofibril + fibril cryo-EM templates (type I / type II / Arctic).
  - *Counter-targets:* Aβ monomer/peptide; fixed-N-terminus / CAA-type Aβ40 fibril.
- **Internal structures already in use:** `9CO4` (Aβ fibril; Conf 1 = receptor-bound target; Conf 2 ≈ plaque/negative), `9CKI` (negative counter-target), `5MY4` (D3 homology reference for epitope).

---

## 5. Environment & infrastructure

**Multi-cluster, git-coordinated (see §0).** Frontenac is the coordinator; workers are added as hired. Per-cluster paths, SLURM, and Globus live in `clusters/<cluster>.env` — **scripts source that file and never hard-code another cluster's paths.**

**Frontenac (coordinator), user `hpc6049`:**
- Login / CPU node: orchestration, ledger, analysis, light scoring (use a short CPU `salloc` for anything nontrivial).
- A100-PCIE-40GB GPU node (SLURM): heavy folding, MD, diffusion, hallucination.

**SLURM (Frontenac) — MANDATORY:**
```bash
#SBATCH --account=def-hpcg6049_gpu
#SBATCH --gres=gpu:a100:1
# NO --partition flag on Frontenac
```
Other clusters use their own account / GRES from `clusters/<cluster>.env`.

**Storage (Frontenac):**
- `/global/project/hpcg6049/lecanemab-am` → repo + curated inputs + final results (git-tracked code/docs/ledger)
- `/global/scratch/hpc6049/lecanemab-am`  → active working data (models, samples, logs); **not** git-tracked (symlink heavy `data/`+`results/` here)

**Conda envs** (create at Phase 0; **pin versions at install, do not assume**):

| env | purpose | core packages |
|---|---|---|
| `lecam` | orchestration, ledger, analysis | python 3.11, duckdb, pandas, biopython/biotite, ANARCI, pyyaml |
| `lecam-ab` | antibody modeling & LMs | ImmuneBuilder (ABodyBuilder2), IgFold, AbLang2, AntiBERTy, BioPhi/Sapiens |
| `lecam-fold` | co-folding oracles | Boltz-2, Chai-1 (AlphaFold3 via container) |
| `lecam-design` | variant generation | ProteinMPNN, SolubleMPNN, LigandMPNN, ColabDesign, BindCraft, RFantibody |
| `lecam-rosetta` | physics scoring + interface design | PyRosetta, Rosetta `flex_ddG`, AbLIFT, FoldX |
| `lecam-md` | conformational ensembles | OpenMM (and/or GROMACS), optionally AlphaFlow |
| `lecam-dev` | developability | Aggrescan3D, NetSolP, SoluProt, TAP/SAbDab-TAP, DeepViscosity/DeepSCM, DE-STRESS |

> Heavy models (AF3, Boltz-2, RFantibody, BindCraft) frequently have conflicting deps → **one isolated env / container per heavy tool**. Record exact versions + git commit hashes in `docs/env/`. Env **names may differ per cluster** — the canonical name for the running cluster is in `clusters/<cluster>.env` (`CONDA_ENV_*`).

---

## 6. Repository layout

```
lecanemab-am/                 # /global/project/hpcg6049/lecanemab-am  (Frontenac)
├── CLAUDE.md                 # root context + §0 multi-cluster protocol
├── PROJECT_STATUS.md         # live status + decision log
├── DEVELOPMENT_PLAN.md       # 8-stage plan
├── HANDOFF.md                # session handoff notes
├── clusters/                 # per-cluster config (multi-agent)
│   ├── README.md             #   how to add/activate a cluster
│   ├── frontenac.env         #   sourceable paths/SLURM/Globus (coordinator)
│   ├── frontenac/CLAUDE.md   #   coordinator agent instructions
│   ├── narval.env  nibi.env  #   worker env stubs (activate when hired)
│   ├── _cluster.env.template
│   └── _worker_CLAUDE.template.md
├── coordination/             # the git-as-channel layer
│   ├── COORDINATION.md       #   registry + rules + commit conventions
│   ├── DASHBOARD.md          #   live status (every agent, every session)
│   ├── inbox/<cluster>/      #   inter-agent messages (+ README protocol)
│   ├── manifests/            #   batch work assignments (*.tsv)
│   └── globus/               #   endpoint IDs + transfer recipes
├── configs/                  # objective.yaml, metrics.yaml, per-tool configs
├── data/                     # raw/ interim/ processed/  (heavy → symlink to scratch)
├── scripts/                  # stage1_inputs/ … stage8_validate/, _detect_cluster.sh
├── slurm/                    # portable sbatch templates (source clusters/<c>.env)
├── db/                       # variants.duckdb (single source of truth)
├── results/                  # results/<stage>/<run-id>/{outputs, manifest.json}
├── notebooks/                # analysis
└── docs/                     # decisions/ sources/ env/
```

---

## 7. Toolchain map (stage → primary tools → env)

| Stage | Role | Primary tools | env |
|---|---|---|---|
| 1 | Inputs + objective | ANARCI/IMGT, SAbDab | `lecam` |
| 2 | Fv + complex + ensemble | ImmuneBuilder/IgFold; Boltz-2/AF3/Chai-1; OpenMM/AlphaFlow | `lecam-ab`,`lecam-fold`,`lecam-md` |
| 3 | Paratope/design space | Paragraph/Parapred; Arpeggio/PLIP; Rosetta ala-scan | `lecam-ab`,`lecam-rosetta` |
| 4 | Variant generation | AbLIFT + framework/Vernier (T1); MPNN/RFantibody (T2); BindCraft/ColabDesign (T3); AntiBERTy/AbLang2/ESM-C (T4) | `lecam-design`,`lecam-rosetta`,`lecam-ab` |
| 5 | Affinity scoring | Boltz-2/AF3 multi-sample ipTM+ipSAE; Rosetta `flex_ddG`/FoldX | `lecam-fold`,`lecam-rosetta` |
| 6 | Selectivity + developability | counter-target re-scoring; BioPhi; TAP/Aggrescan3D/NetSolP/DeepViscosity | `lecam-dev`,`lecam-fold` |
| 7 | Format/valency/delivery | multivalent + TfR1 bispecific design; Fc engineering (opt) | `lecam-design`,`lecam-fold` |
| 8 | Validation + AL loop | display (dual-selection) + BLI/SPR; ledger feedback | `lecam` |

---

## 8. Operating rules

- **Source-grounded:** every biological claim, epitope assertion, or filter cutoff must cite an entry in `docs/sources/` (exact sentence) or §11. Ungrounded choices are tagged `ASSUMPTION:` and surfaced in PROJECT_STATUS open questions.
- **Audit trail:** every run writes a date-stamped `manifest.json` (inputs, tool versions, configs, git commit, SLURM job id, seeds) to `results/<stage>/<run-id>/`.
- **Resumable + dry-run:** scripts support `--dry-run` and idempotent re-runs; never silently overwrite.
- **Single source of truth for variants:** the **DuckDB ledger** (`db/variants.duckdb`) on the coordinator. No variant exists outside it. The binary `.duckdb` is **git-ignored** (unmergeable across agents); the git-shared form is `db/exports/variants.csv` + `coordination/manifests/*.tsv` — workers report CSV rows, the coordinator merges and re-exports.
- **Stochasticity discipline:** Boltz/AF3/diffusion are stochastic → fixed seeds + **multi-sample**, store *all* samples, record seeds in the manifest.
- **WT everywhere:** WT lecanemab Fv runs through every scoring/filter step; all deltas are reported vs WT.
- **No fabricated specifics:** sequences, version pins, and HPC module names are confirmed at setup, never guessed.

---

## 9. Guardrails (check every proposal against these)

1. **Selectivity erosion (#1 failure mode):** never advance a variant that improves protofibril engagement **and** monomer or CAA-fibril engagement. Stage-6 counter-selection is mandatory.
2. **No co-crystal:** the docked pose is a hypothesis — use the **pose ensemble** + multi-model consensus, never tune to one pose. AF-Multimer is documented-weak on CDR-H3 and epitope–paratope pose (R-EGFR).
3. **Affinity–stability tradeoff:** matured variants frequently destabilize (R-AMTRADE) → co-optimize stability/developability or reject.
4. **Metric hygiene:** do **not** rank by unnormalized ESM2 pseudo-log-likelihood (length-biased; non-predictive of binding/expression in the EGFR competition, R-EGFR). Prefer ESM-C / ESM3 or antibody-specific LMs; rank affinity by multi-sample ipTM+ipSAE consensus.
5. **Compute is a funnel, display is the decision:** in-silico ΔΔG on a conformational aggregate epitope is **not validated to generalize** — treat as soft prioritization; the wet-lab dual-selection readout decides.

---

## 10. Workflow protocol

1. Claude (chat, with the PI) drafts the next-step prompt / config; the **coordinator** (Frontenac) records the decision.
2. `git pull origin main` → run on the right cluster/node (A100 for heavy, login/CPU for light); capture logs + `manifest.json`.
3. Commit **small** outputs (CSVs, manifests, configs) to git; move **large** data via Globus. Update the ledger + your `coordination/DASHBOARD.md` row.
4. Coordinator interprets, updates PROJECT_STATUS + decision log (ADR in `docs/decisions/`), and assigns any worker tasks via `coordination/inbox/` or `coordination/manifests/`.
5. Commit with a `[<cluster>]` prefix; `git push origin main`.

---

## 11. References (key → claim supported)

| Key | Source | Supports |
|---|---|---|
| R-NMR | Aβ NMR review, PMC10205579 | B1 (humanized mAb158, protofibril-selective) |
| R-ANA | *Ann Neurol* 2025, doi:10.1002/ana.27175 | B2 (>10⁶-fold protofibril vs monomer selectivity) |
| R-TG | Lecanemab binds tg-mouse fibril folds, PMC12152531 | B3, B4 (flexible vs fixed N-terminus; CAA sparing) |
| R-SD | *J Neuroimmunol/…* ScienceDirect S1044743124000344 | B3 (protofibril selectivity; vascular fibrils; ARIA relevance) |
| R-ELIFE | eLife reviewed preprint 106156 | B5, B6 (no co-structure; D3/5MY4 model; tolerance 3–7) |
| R-REV | Revvity "Alzheimer's drug discovery" | B5 (no lecanemab co-structure in PDB) |
| R-HEXA | *Transl Neurodegener* 2021, doi:10.1186/s40035-021-00258-x | B7 (Hexa-RmAb158 multivalent avidity) |
| R-ABLIFT | Fleishman AbLIFT, PMC6728052 | Stage 4 T1 (VH/VL interface AM) |
| R-YSD | Rational AM of anti-amyloid Abs, PMC8081927 | Stage 8 (yeast display + conformational counter-selection) |
| R-AMTRADE | *Molecules* 2025, PMC11819675 | Guardrail 3 (CDR + surrounding residues; affinity–stability tradeoff) |
| R-EGFR | Adaptyv EGFR competition analysis, bioRxiv 2025.04.17.648362 | Guardrails 2,4; method provenance |
| R-MOSAIC | Escalante "Mosaic" Nipah write-ups | Stage 5 (multi-sample consensus ranking) |
| R-CRADLE | Cradle EGFR-2 win write-up | Stage 4 T1 (framework-mutation, CDR-preserving AM) |

> Store the exact load-bearing sentences (not just URLs) in `docs/sources/` so every threshold is traceable.

---

## 12. Glossary

**Aβ** amyloid-beta · **protofibril** soluble aggregated Aβ (primary target species) · **CAA** cerebral amyloid angiopathy (vascular Aβ40; counter-target) · **ARIA(-E)** amyloid-related imaging abnormalities (edema) · **Fv/scFv** variable fragment / single-chain Fv · **CDR** complementarity-determining region · **Vernier** framework residues that shape CDR conformation · **ipTM / ipSAE / iPAE** interface confidence metrics from folding models · **ΔΔG** change in binding free energy on mutation · **MLDE** machine-learning-directed evolution · **OAS** Observed Antibody Space · **avidity** apparent affinity gain from multivalent engagement.
