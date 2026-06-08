# Design Decision Memo — lecanemab-am

**Purpose.** A single place for the **PI-level decisions** that define the campaign, grouped by
project phase, so the design can be ratified (or **restarted from scratch**) deliberately. Each
item has a **status**, the **options**, and **Claude's recommendation**. Status legend:
`[DECIDED D-xxx]` already in the decision log · `[RATIFY]` Claude chose autonomously, wants PI
sign-off · `[OPEN]` undefined, PI must decide · `[BLOCKER]` gates downstream work.

> Drafted 2026-06-06 (origin/main 219bda6) after Stage-6 found all top-T2 CDR hits are monomer-drift.
> Authoritative live state: `HANDOFF.md` + `PROJECT_STATUS.md`. Quantitative gates live in `configs/metrics.yaml`.

---

## 0. Cross-cutting / Objective

- **OBJ-1 — Optimization objective** `[DECIDED D-001]`. Avidity-adjusted protofibril affinity +
  preserve conformational selectivity (vs monomer & CAA fixed-N); **NOT monovalent KD**. Confirm this
  still stands — it is the lens for every item below, and Stage 6 already showed monovalent gains erode selectivity.
- **OBJ-2 — In-silico trust policy** `[OPEN][BLOCKER]`. Guardrail 5: in-silico ΔΔG/ipSAE on a
  conformational aggregate epitope is **not validated** to generalize. Decide the policy:
  - (A) In-silico is **triage only** → advance a fixed top-N panel per track to wet-lab display regardless of borderline scores; display + counter-selection decides. **(Recommended.)**
  - (B) Hard in-silico gates (no variant advances unless it clears numeric thresholds).
  - *Recommendation:* (A) with soft gates — sets realistic expectations and matches D-005.

---

## Phase 0 — Provisioning

- **P0-1 — Compute coordination** `[DECIDED D-006]`. Multi-cluster git; Frontenac coordinator.
- **P0-2 — Env build strategy** `[DECIDED D-007]`. conda-forge/bioconda (not CC wheelhouse); reuse
  `../protein` tools (ProteinMPNN/BindCraft/RFdiffusion/colabfold). Run rules: env-frontenac gotchas.
- **P0-3 — Worker clusters** `[OPEN]` (OQ-5). Hire Narval/Nibi for scale, or stay Frontenac-only?
  *Recommendation:* stay Frontenac-only until a track needs large arrays (e.g. full-settings flex_ddG ×100s of variants); revisit then.
- **P0-4 — Remaining envs / licensed tools** `[OPEN]`. `lecam-dev` (developability) not built;
  AF3 (container, access-gated), FoldX (license), AbLIFT protocol, BioPhi/Sapiens (humanness, own env).
  *Recommendation:* build `lecam-dev` + BioPhi before Stage 6 gating; AF3 only if a 3rd consensus scorer is wanted; FoldX optional (flex_ddG covers ΔΔG).

---

## Phase 1 — Inputs, Targets & Objective

- **S1-1 — Fv sequence** `[DECIDED D-008]`. KEGG D11678 ↔ patent US9573994B2.
- **S1-2 — Canonical TARGET species** `[OPEN][BLOCKER]`. Registry lists 9CO4 (brain Aβ42 oligomer,
  "Conf1 = receptor-bound target"), 7Q4B/7Q4M (type I/II fibril), 8BFZ (Arctic). **Which is THE
  target the campaign optimizes against, and is it one or an ensemble?** This drives Stage-2 modeling.
  - *Recommendation:* primary = **9CO4** (designated receptor-bound oligomer); cross-check on 7Q4B/7Q4M
    as a target ensemble (D-002 spirit). Decide before building the protofibril model.
- **S1-3 — Monomer counter-target** `[RATIFY D-009]`. 1Z0Q (Aβ42 aqueous); 1IYT rejected; 2LFM (Aβ40) control.
- **S1-4 — Epitope-homology set** `[DECIDED D-010]`. 6CO3/5CSZ/3BKJ/4HIX; 5MY4 demoted.
- **S1-5 — Amend CLAUDE.md B5?** `[OPEN]`. We added a caveat + D-010 but left B5 wording (5MY4="D3")
  unchanged. *Recommendation:* amend B5 to cite the RCSB-verified identity + the homology set.
- **S1-6 — Pin paywalled sources** `[OPEN]`. B2 (>10⁶ selectivity, R-ANA) + R-REV exact sentences still flagged.

---

## Phase 2 — Structural Modeling & Ensembles

- **S2-1 — Pose ensemble, not single pose** `[DECIDED D-002]`.
- **S2-2 — Fv model tool** `[RATIFY]`. ImmuneBuilder/ABodyBuilder2 primary (IgFold cross-check). Fine.
- **S2-3 — TARGET CONSTRUCT for co-folding** `[OPEN][BLOCKER — the central methods decision]`.
  The current "target" = free Aβ1-16 peptide, which Stage 6 showed ≈ monomer (monovalent epitope).
  Options for a protofibril-specific target:
  - (A) **Templated 9CO4 protofibril + Fv docking** (rigid 9-42 core, model flexible 1-8, dock Fv onto a protruding N-terminus; PyRosetta or Boltz pocket constraints). Captures the conformational (B3/B4) axis. **(Recommended; de-novo co-fold already proven to fail — Aβ self-aggregates.)**
  - (B) Keep free-peptide co-fold but ONLY use it for relative ranking, never as protofibril proxy.
  - (C) Defer structural target; rely on avidity (Stage 7) + wet-lab for selectivity.
  - *Recommendation:* (A), validated by requiring WT protofibril-score > monomer before trusting it.
- **S2-4 — Multi-sample depth** `[RATIFY]`. Currently 5 seeds × 5 diffusion samples = 25/variant.
  *Recommendation:* keep 25 for screening; bump for final candidates. PI may want a power/cost call.
- **S2-5 — Epitope register** `[OPEN→informed]` (OQ-1). Keep as a **hypothesis set** (D-002) — data show
  a broad N-terminal footprint (Aβ 1-11/13-15) covering both lit "3-7" and B6 hotspots. *Recommendation:* do not lock a single register.
- **S2-6 — Conformational ensemble (MD)** `[RATIFY]`. 5 ns implicit GBn2, framework-restrained → qualitative
  B3 check (confirmed flexible N-term). *Recommendation:* keep as qualitative; longer/explicit MD only if a quantitative flexibility metric is needed.

---

## Phase 3 — Paratope Mapping & Design-Space

- **S3-1 — Editable vs protected residue set** `[OPEN][BLOCKER for Stage 4]`. Stage 2.4 mapped a
  CDR-H3-led paratope. Decide the explicit **protected (fixed) set** vs **editable set**:
  - (A) Protect the paratope-core contacts (esp. CDR-H3 epitope-contacting residues); edit only peripheral CDR positions.
  - (B) Allow all CDRs editable with edit-distance caps + mandatory selectivity counter-screen.
  - *Recommendation:* given the selectivity guardrail and the Stage-6 finding, lean (A) — protect H3 core, diversify periphery.
- **S3-2 — Edit-distance / paratope-core caps** `[OPEN]`. Max mutations per variant overall and within the core.
  *Recommendation:* ≤3-4 total; ≤1 in the protected core (if any allowed).

---

## Phase 4 — Variant Generation (multi-track)

- **S4-1 — Track order** `[DECIDED D-003]`. T1 (framework/Vernier, CDR-preserving) first.
- **S4-2 — T1 method** `[RATIFY]`. AbLang2 OAS-prior framework reversions (done; 3 found — framework
  already humanized) + AbLIFT/Rosetta VH-VL redesign (pending lecam-rosetta).
- **S4-3 — T2 method & thresholds** `[RATIFY]`. ProteinMPNN `--conditional_probs_only` conservative
  point-muts (PI chose conservative); log-odds ≥ 1.0, combos ≤3. Ratify the cutoff.
- **S4-4 — Do we keep pursuing monovalent-affinity CDR gains?** `[OPEN][BLOCKER]`. Stage 6 showed
  affinity-improving CDR muts drift toward monomer. Decide the generation objective:
  - (A) **Pivot generation to protofibril-SELECTIVE designs** — score/select on Δprotofibril−Δmonomer inside the loop, or target protofibril-specific contacts. **(Recommended.)**
  - (B) Continue affinity-first generation, filter at Stage 6 (most candidates will fail).
- **S4-5 — T3/T4 scope** `[OPEN]`. T3 (BindCraft/ColabDesign hallucination) and T4 (LM point-muts) —
  pursue, and when? *Recommendation:* defer T3/T4 until the target construct (S2-3) is fixed.
- **S4-6 — Per-track panel sizes** `[OPEN]`. How many variants per track to register/score (cost).

---

## Phase 5 — In-Silico Affinity Scoring & Consensus

- **S5-1 — Scorers** `[DECIDED D-004 + RATIFY]`. Boltz-2 multi-sample **ipSAE** (NOT raw iptm —
  inflated by VH-VL) + Rosetta **flex_ddG** (2nd independent scorer added this session). AF3/Chai as optional 3rd.
- **S5-2 — M1 affinity threshold** `[OPEN][BLOCKER]`. `metrics.yaml` M1 = TODO. Define the **Δ-ipSAE-vs-WT**
  gate (delta, not absolute), accounting for the ~0.2-0.25 ipSAE noise (so ≥ ~2 SEM, multi-sample).
- **S5-3 — Consensus formula** `[RATIFY]`. Currently rank = z(Δ-ipSAE) − z(ΔΔG). Define the official combiner / weights.
- **S5-4 — flex_ddG settings policy** `[RATIFY]`. Reduced (nstruct 5/backrub 10k) for triage; FULL
  (35/35000) for interface candidates that pass triage. Confirm.

---

## Phase 6 — Selectivity, Humanness & Developability `[the decisive phase]`

- **S6-1 — Selectivity protocol & gates** `[OPEN][BLOCKER]`. Must compute on the **protofibril target**
  (S2-3) vs **monomer (1Z0Q)** and **CAA fixed-N (8QN7)**. Define M2/M2b thresholds: require
  `Δprotofibril − Δmonomer > 0 AND ≥ WT` and `Δprotofibril − ΔCAA > 0 AND ≥ WT`. Currently TODO.
- **S6-2 — Avidity metric** `[OPEN][BLOCKER]` (OQ-3). Monovalent co-fold CANNOT capture the >10⁶
  monomer selectivity (avidity). Decide: attempt a valency-aware score, or defer avidity to Stage 7 + wet-lab.
  *Recommendation:* defer to Stage 7/wet-lab; use monovalent screens for the **conformational/CAA** axis only.
- **S6-3 — Hard-reject vs deprioritize** `[OPEN]`. Stage 6 hard-rejected 6 T2 hits on a *monovalent*
  proxy. *Recommendation:* downgrade to "deprioritized — recheck on the protofibril target" rather than permanent reject, since the proxy was the monomer-like peptide.
- **S6-4 — Developability gate** `[OPEN]`. Build `lecam-dev`; set M3 cutoffs (TAP flags, Aggrescan3D,
  NetSolP, viscosity) = no new liabilities vs WT.
- **S6-5 — Humanness floor** `[OPEN]`. BioPhi/Sapiens env; M4 = OASis percentile ≥ WT.

---

## Phase 7 — Format, Valency & Delivery `[where the avidity lever actually lives]`

- **S7-1 — Multivalent format(s)** `[OPEN][arguably the highest-impact decision]`. Per OBJ-1, avidity
  for epitope-dense protofibrils is the functional lever (B7, Hexa-RmAb158). Decide which formats to
  design/model: bivalent IgG (baseline) vs tri/tetra/hexavalent. *Recommendation:* explicitly include a
  multivalent arm — CDR maturation alone (Phases 4-6) may not move selectivity.
- **S7-2 — Brain delivery (TfR1 bispecific)** `[OPEN]`. In scope (the lab's prior Aβ42×TfR1 project)?
- **S7-3 — Fc / ARIA engineering** `[OPEN]` (OQ-4). In scope or out?

---

## Phase 8 — Experimental Validation & Active Learning

- **S8-1 — Wet-lab readout** `[DECIDED D-005]`. Display + dual selection (protofibril +, monomer −) → BLI/SPR.
- **S8-2 — Display platform** `[OPEN]` (OQ-2). Yeast vs phage; protofibril reagent prep/immobilization/stability.
- **S8-3 — Panel size & stop criterion** `[OPEN]`. How many variants advance to display; when to stop in-silico.
  *Recommendation:* a small dual-selection panel (top per track + WT controls), sized to the wet-lab budget.
- **S8-4 — Active-learning loop** `[OPEN]`. How measured KD/koff re-weights the in-silico rankers (MLDE).

---

## Highest-priority asks (if you ratify nothing else)
1. **S2-3** — the protofibril target construct (unblocks the real selectivity axis).
2. **S5-2 / S6-1** — the M1 affinity + M2/M2b selectivity thresholds (defines "hit").
3. **S6-2 / S7-1** — the avidity policy + whether multivalent format is in scope (the actual lever).
4. **S4-4** — pivot generation to selectivity-aware, given the Stage-6 finding.
