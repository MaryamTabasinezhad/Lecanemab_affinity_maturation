# Design Decision Memo — Lecanemab Computational Affinity Maturation

**What this document is.** A single, self-contained place that lists the decisions which are
genuinely the **project owner's (PI's) to make** — the scientific-strategy, scope, threshold, and
risk calls that the computational pipeline cannot and should not decide on its own. It is organised
by **project phase** (the eight-stage plan in `DEVELOPMENT_PLAN.md`, preceded by a provisioning
"Phase 0"), so you can either ratify the path taken so far or **redesign the campaign from scratch**
deliberately, phase by phase.

**How to read it.** Each decision has:
- a **Status** (plain language): *Decided* (already chosen and logged), *Needs your sign-off*
  (the computational side chose something reasonable but it shapes the science, so it should be
  ratified), *Open* (genuinely undefined — you must decide), and a note where the item **blocks**
  downstream work;
- **Background** — enough context to understand the decision without opening other files;
- **The decision to make** — stated as a concrete question;
- **Options** — each spelled out with its consequences;
- **Recommendation** — the computational side's suggestion and why.

**Where the underlying detail lives** (so you can drill in if you want):
- `CLAUDE.md` — the project's standing instructions, the objective (its §2), the seven load-bearing
  biology facts **B1–B7** (its §3), and the reference keys **R-xxx** that back them.
- `PROJECT_STATUS.md` — the live status, the **decision log** (entries **D-001 … D-010**), and the
  **open questions** (**OQ-1 … OQ-7**).
- `configs/metrics.yaml` — the file that defines the numeric pass/fail **success metrics M1–M5**;
  **every threshold in it is currently a placeholder marked `TODO`** (that is itself one of the
  decisions below).
- `results/stage6/SELECTIVITY_FINDING.md` and `PROTOFIBRIL_MODEL_NOTES.md` — the two analyses behind
  the current strategic crossroads (explained under Phase 6 and Phase 2).

**A short glossary** (terms used throughout):
- **Fv / VH / VL** — the antibody variable fragment and its heavy/light variable domains; this is the
  part being engineered. **CDR** — the six hypervariable loops that form the binding site
  (**paratope**). **CDR-H3** is the most diverse loop and, for lecanemab, the dominant part of the
  paratope. **Framework / Vernier** — the scaffold residues; Vernier residues sit under the CDRs and
  subtly shape their conformation.
- **Epitope** — the patch on the antigen (here the N-terminus of amyloid-β, "Aβ") that the antibody
  binds.
- **Protofibril / monomer / CAA fibril** — three forms of Aβ. The **protofibril** (soluble
  aggregate) is the *target*; the **monomer** (single free peptide) and the **CAA fibril** (vascular
  amyloid, a fibril with a rigid N-terminus) are the two things we must *not* bind — the
  *counter-targets*.
- **Conformational selectivity / avidity** — lecanemab's >10⁶-fold preference for protofibril over
  monomer comes from two things: the epitope is only accessible when the Aβ N-terminus is *flexible*
  (conformational), and the protofibril presents *many* copies of the epitope so the antibody binds
  with high apparent strength through multivalency (**avidity**). Critically, the per-arm
  (monovalent) affinity is intentionally *weak*; raising it converts lecanemab into a monomer- and
  vascular-amyloid binder and removes both the selectivity and the safety margin (low **ARIA**, the
  brain-swelling side effect). This is the heart of the objective.
- **ipTM / ipSAE** — confidence scores that a structure-prediction model outputs for a predicted
  complex. **ipTM** is a global interface confidence; we have found it is *over-confident* for
  antibody–antigen complexes because it is inflated by the (trivially correct) VH–VL pairing.
  **ipSAE** is an interface-specific score that strips that out; it is the number we rank on.
- **ΔΔG / flex_ddG** — a physics-based estimate of how much a mutation changes binding free energy
  (negative = stronger binding). **flex_ddG** is the specific Rosetta protocol we use as an
  independent second opinion alongside the structure-prediction score.
- **Δ-vs-WT** — because the absolute scores are noisy and not validated, we always report a variant's
  score *relative to wild-type (WT) lecanemab* run through the identical pipeline.

> Drafted 2026-06-06 after the selectivity counter-screen (Phase 6) showed that every CDR variant we
> had ranked as "improved" was in fact drifting toward monomer binding — see Phase 6. That finding is
> why several items below are flagged as the highest-priority decisions.

---

## 0. Cross-cutting — the objective and how much to trust the computer

### OBJ-1 — The optimisation objective itself
**Status:** *Decided* (logged as **D-001**) — please confirm it still holds.
**Background.** The campaign is built on a deliberately unusual objective: improve lecanemab's
*avidity-adjusted* engagement of Aβ protofibrils while *preserving* its conformational selectivity,
and explicitly **not** maximising the monovalent binding constant (KD). The reasoning (biology facts
B2/B3/B4 in `CLAUDE.md`) is that lecanemab's therapeutic value and its safety both depend on its
weak monovalent affinity plus avidity; a "stronger binder" would likely be a worse, less safe drug.
**The decision.** Confirm this framing is still the goal. Everything below inherits it.
**Recommendation.** Keep it. The Phase-6 result (below) is the first hard in-silico evidence that the
naïve "make it bind tighter" approach actively harms selectivity, which validates the framing.

### OBJ-2 — How much weight to put on the computational scores
**Status:** *Open*, and it **shapes the whole funnel.**
**Background.** None of our in-silico scores (the structure-prediction interface confidence, the
Rosetta ΔΔG) are validated to predict real binding for this conformational, aggregate epitope — this
is a stated guardrail. They are useful for *ranking and triage*, not for declaring success.
**The decision.** Are the computational numbers a *filter* (a variant must clear numeric gates to
advance) or a *prioritiser* (we use them to pick which variants go to the wet lab, but the wet lab
decides)?
**Options.**
- *(A) Prioritiser / soft gates.* Carry a fixed-size, best-ranked panel per design track forward to
  the wet-lab display assay regardless of borderline scores; let experiment decide. Lower risk of
  discarding a real hit on a noisy score.
- *(B) Hard gates.* Nothing advances unless it clears the numeric thresholds (M1–M5). Cleaner funnel,
  but will reject variants on numbers we don't fully trust.
**Recommendation.** (A). It matches the planned wet-lab readout (display with dual selection, logged
as **D-005**) and acknowledges the scores' limits.

---

## Phase 0 — Provisioning (compute, software, data plumbing)

This phase is largely settled; the open items are about scale and a few un-built tools.

### P0-1 — Compute coordination model
**Status:** *Decided* (**D-006**). The project runs as one or more AI agents coordinating *only*
through this git repository (no shared memory), with Frontenac as the coordinator and additional
clusters added as "workers" when needed. No action unless you want to change the working model.

### P0-2 — Software environment strategy
**Status:** *Decided* (**D-007**), no action. All tools are installed as isolated conda
environments built from the conda-forge/bioconda community channels (not ComputeCanada's internal
package mirror, which produces binaries incompatible with this machine). Several heavy tools were
reused from the sibling `../protein` project rather than reinstalled.

### P0-3 — Whether to hire additional clusters
**Status:** *Open* (**OQ-5**).
**Background.** Everything so far runs comfortably on Frontenac. Some later steps (e.g. the
full-precision physics scoring across hundreds of variants, or large generative design batches) are
embarrassingly parallel and would finish faster spread across more machines.
**The decision.** Bring the lab's other clusters (Narval, Nibi) online as workers, and when?
**Recommendation.** Stay Frontenac-only until a specific step is genuinely compute-bound; the
multi-cluster machinery is ready to activate when that happens.

### P0-4 — The last un-built tools / licensed software
**Status:** *Open* (a provisioning to-do that gates Phase 6/7, not a deep strategy call).
**Background.** One environment is still unbuilt: **`lecam-dev`**, the developability/biophysical-
liability toolkit (aggregation propensity, solubility, viscosity, "TAP" antibody-developability
flags). Also not yet set up: the AlphaFold3 container (an optional third scoring model, access-
gated), the FoldX licence (an optional second ΔΔG method — Rosetta already gives us one), the AbLIFT
antibody-interface redesign protocol, and the BioPhi/Sapiens "humanness" scorer.
**The decision.** Which of these to build, and in what order.
**Recommendation.** Build `lecam-dev` and the humanness scorer before we gate variants in Phase 6,
since those are required to decide what advances. Treat AlphaFold3 and FoldX as optional
nice-to-haves (we already have two independent scorers); add only if you want extra consensus.

---

## Phase 1 — Inputs, Targets & Objective Lock-In

### S1-1 — The lecanemab sequence
**Status:** *Decided* (**D-008**), no action. The variable-domain sequence was taken from the
WHO/KEGG public record and independently cross-checked against the BioArctic patent; both CDRs match.

### S1-2 — Which Aβ structure is *the* target?  ⚠ blocks Phase 2
**Status:** *Open*, and it is foundational.
**Background.** We have curated several cryo-EM structures of aggregated Aβ: a brain-derived Aβ42
*oligomer* (PDB **9CO4**, which our notes flag as the "receptor-bound target" conformation), two
fibril folds from human brain (type I = **7Q4B**, type II = **7Q4M**), and the Arctic-mutant fold
(**8BFZ**). These differ in shape, and a variant optimised against one may not be optimal against
another. The whole notion of "improving protofibril engagement" requires fixing what the protofibril
*is* structurally.
**The decision.** Pick the canonical target — a single structure, or an ensemble of a few — that the
campaign optimises against and counter-screens relative to.
**Recommendation.** Use **9CO4** as the primary target (it is the designated oligomer/"receptor-bound"
form), and additionally check the leading candidates against the 7Q4B/7Q4M fibril folds so we are
not over-fitting to one polymorph. Lock this before building the Phase-2 target model.

### S1-3 — The monomer counter-target structure
**Status:** *Needs your sign-off* (logged as **D-009**).
**Background.** To test that a variant has *not* gained monomer binding, we need a structural stand-in
for the disordered Aβ monomer. We chose an aqueous-solution NMR structure of Aβ42 (PDB **1Z0Q**) as
primary, kept an Aβ40 version (**2LFM**) as a sequence-matched control, and rejected an older
structure (**1IYT**) because it was solved in a membrane-mimicking solvent and is artificially
helical. This was an evidence-based choice but it is a scientific call.
**The decision.** Ratify, or substitute a monomer reference you prefer.
**Recommendation.** Ratify 1Z0Q.

### S1-4 — The homology structures used to model the binding pose
**Status:** *Decided with your prior sign-off* (**D-010**). No public lecanemab–Aβ co-structure
exists, so the binding pose is modelled by analogy to other anti-N-terminal-Aβ antibodies. We use a
set of four real antibody–Aβ co-structures (aducanumab **6CO3**, gantenerumab **5CSZ**, WO2 **3BKJ**,
3D6 **4HIX**). A structure previously cited in the literature as "antibody D3 / PDB 5MY4" turned out,
on checking, to be an antibody against a *chemically modified* form of Aβ, so it was demoted to a
weak reference. No action unless you want to revisit the set.

### S1-5 — Whether to formally correct the standing instructions about "D3 / 5MY4"
**Status:** *Open* (minor, housekeeping).
**Background.** The discovery in S1-4 (that the long-cited "D3 / 5MY4" reference is mis-identified) is
recorded as a caveat and a decision entry, but the original sentence in the standing instructions
file (`CLAUDE.md`, biology fact **B5**) was left as-is, faithfully quoting the source that contained
the error.
**The decision.** Amend B5 to state the corrected identity and point to the homology set, or leave the
caveat as the correction layer.
**Recommendation.** Amend B5 — it removes a known wrong fact from the canonical instructions.

### S1-6 — Pin the remaining paywalled source sentences
**Status:** *Open* (low-effort documentation hygiene). Two underpinning facts (the exact published
sentence for the ">10⁶-fold selectivity" figure, and a "no co-structure exists" statement) are
behind paywalls and are currently flagged rather than quoted verbatim. Decide whether to retrieve
them for the audit trail.

---

## Phase 2 — Structural Modelling & Conformational Ensembles

### S2-1 — Use a pose *ensemble*, not one fixed docked structure
**Status:** *Decided* (**D-002**), no action. Because there is no experimental co-structure and the
predicted pose is uncertain, every structure-based step uses a spread of predicted poses and looks at
consensus rather than trusting a single model.

### S2-2 — Which tool builds the antibody model
**Status:** *Needs your sign-off* (minor). We use ABodyBuilder2 as the primary antibody-structure
predictor (with IgFold as a cross-check). Standard, low-stakes; ratify or note a preference.

### S2-3 — How to represent the protofibril target for binding prediction  ⚠⚠ the central methods decision; blocks Phase 5/6
**Status:** *Open*, and it is the single most consequential technical decision right now.
**Background.** Until now, the "target" we docked the antibody against was just the **free 16-residue
N-terminal Aβ peptide** (Aβ1–16). That was a convenient stand-in for the epitope, but the Phase-6
counter-screen revealed the problem: a single free peptide is essentially *the monomer epitope*, so
"binding it better" is the same as "binding the monomer better" — exactly what we must avoid. To find
variants that are genuinely *protofibril-selective*, the target has to capture what is different about
the protofibril: the epitope is displayed on a **rigid, epitope-dense aggregated core with a flexible
N-terminus sticking out** (this is the structural basis of biology facts B3/B4). We also tested the
obvious shortcut — letting the prediction model fold the antibody together with several free Aβ
chains — and it failed informatively: the Aβ chains stuck to *each other* (as Aβ does) and left the
antibody unbound. Details in `results/stage6/PROTOFIBRIL_MODEL_NOTES.md`.
**The decision.** How do we build a protofibril target that the antibody can be scored against?
**Options.**
- *(A) Templated protofibril + docking.* Take the *real* 9CO4 structure as a fixed scaffold, add back
  the flexible N-terminus that the cryo-EM did not resolve, and dock the antibody onto that protruding
  N-terminus (using physics-based docking in our Rosetta environment, or constraint-guided
  prediction). This captures the conformational selectivity (rigid core + presented flexible
  N-terminus) and is the natural fix for the failure above. **(Recommended.)**
- *(B) Keep the free-peptide co-fold but use it only as a relative-ranking tool*, never claiming it
  represents the protofibril — and lean on avidity modelling (Phase 7) and the wet lab for true
  selectivity.
- *(C) Defer structural targeting entirely* and treat selectivity as something only the multivalent
  format (Phase 7) and the wet-lab counter-selection can establish.
**Recommendation.** (A), with a built-in sanity check: the model is only trusted if *wild-type*
lecanemab scores higher against the protofibril target than against the monomer (i.e. it reproduces
the known preference) before any variant is judged on it.

### S2-4 — How many predictions per variant
**Status:** *Needs your sign-off* (a cost/precision call). Each variant is currently predicted with 5
random seeds × 5 samples = 25 structures, and we take the consensus. More samples = less noise but
more compute. Recommendation: keep 25 for screening, increase only for a small set of finalists.

### S2-5 — Whether to commit to a single epitope register
**Status:** *Resolved as "keep open"* (**OQ-1**). The pose ensemble gives a broad N-terminal footprint
(roughly Aβ residues 1–15) that is consistent with both the published "residues 3–7" view and our
internal hotspot hypothesis. Recommendation (and current practice): keep it as a hypothesis set, do
not lock one register. No action needed unless you disagree.

### S2-6 — The molecular-dynamics flexibility check
**Status:** *Needs your sign-off* (minor). A short (5 ns) simulation confirmed, qualitatively, that
the engaged Aβ N-terminus stays flexible/disordered (supporting biology fact B3). It was deliberately
a quick qualitative check, not a quantitative flexibility measurement. Ratify, or ask for longer/more
rigorous simulation if you want a number rather than a yes/no.

---

## Phase 3 — Paratope Mapping & Defining the Design Space

### S3-1 — Which residues are allowed to change, and which are protected  ⚠ blocks Phase 4
**Status:** *Open.*
**Background.** Our pose analysis showed the binding site is dominated by CDR-H3 (the most diverse
loop). The objective's #1 risk is eroding selectivity by disturbing this conformational binding site.
So before generating variants we must decide which positions designers are allowed to touch.
**The decision.** Define the **editable** set versus the **protected** set explicitly.
**Options.**
- *(A) Protect the binding-site core (especially the CDR-H3 epitope-contacting residues); only let
  designers change peripheral loop positions.* Lower risk to selectivity; explores less.
- *(B) Allow all CDR positions to change but cap how many at once and counter-screen every variant.*
  Explores more; higher risk; relies on the selectivity filter catching problems.
**Recommendation.** Lean toward (A). The Phase-6 finding (below) showed that freely changing the
binding site reliably breaks selectivity, so protecting the core is well-justified.

### S3-2 — How many mutations per variant
**Status:** *Open.* Set a cap on total mutations per variant (and within the protected core, if any
are allowed there). Recommendation: a conservative cap (a few mutations total, essentially none in
the protected core) until the protofibril target (S2-3) is in place to judge them properly.

---

## Phase 4 — Variant Generation (the design tracks)

### S4-1 — The order of the design tracks
**Status:** *Decided* (**D-003**). Start with the safest track — framework/Vernier changes that leave
the binding loops untouched — then move to riskier binding-site redesign. No action.

### S4-2 — How the framework track (T1) generates candidates
**Status:** *Needs your sign-off.* For the safe framework track we used an antibody language model
trained on natural antibody repertoires to suggest framework residues that are "more natural" than
lecanemab's. It found only three confident suggestions — a real result in itself: lecanemab's
framework is already well-humanised, so there is little to revert. (A complementary Rosetta-based
interface-redesign method for this track is not yet built.) Ratify the approach.

### S4-3 — How the binding-site track (T2) generates candidates, and how conservatively
**Status:** *Needs your sign-off* (you already chose the conservative direction).
**Background.** Our first attempt at binding-site redesign (a standard protein-design model allowed to
rewrite all six loops) was far too aggressive — it changed roughly half of all binding-loop residues,
effectively designing a new antibody, which would certainly destroy selectivity. You then chose the
**conservative** route: use the design model only to suggest *individual* point mutations it favours,
one at a time, and small low-mutation combinations. That produced 30 candidate variants.
**The decision.** Ratify the conservative method and the specific confidence cut-off we used to
include a suggestion.
**Recommendation.** Ratify; the conservative route is the right match for the selectivity guardrail.

### S4-4 — Should we keep generating for *affinity* at all?  ⚠ strategic, follows from Phase 6
**Status:** *Open* — and arguably the most important strategic question.
**Background.** Phase 6 showed that the binding-site point mutations that improved predicted epitope
affinity *also (and more so) improved monomer binding* — i.e. improving affinity, even
conservatively, drifted toward the failure mode. This suggests that generating variants ranked on
affinity is the wrong objective for the design step.
**The decision.** Reframe what the generator optimises for.
**Options.**
- *(A) Generate for selectivity, not affinity.* Put the monomer (and CAA) counter-screen *inside* the
  generation loop, keeping only mutations that improve protofibril engagement *without* improving
  monomer engagement — or that specifically strengthen contacts unique to the aggregated form.
  **(Recommended.)**
- *(B) Keep generating for affinity and filter later.* Simpler, but most candidates will be discarded
  at Phase 6, as just happened.
**Recommendation.** (A), once the Phase-2 protofibril target (S2-3) exists to define "selective."

### S4-5 — Whether to run the other two design tracks, and when
**Status:** *Open.* Two further tracks are planned: a "hallucination"/gradient-based design track that
uses our GPU design engine, and a language-model point-mutation track. Recommendation: defer both
until the target representation (S2-3) is fixed, so they optimise toward the right thing.

### S4-6 — How many variants per track
**Status:** *Open* (a cost/throughput call). Decide the target panel size per track.

---

## Phase 5 — In-Silico Scoring & Consensus Ranking

### S5-1 — Which scoring methods, and what we rank on
**Status:** *Decided / needs sign-off.* We rank by the structure-prediction *interface* score
(**ipSAE**, not the over-confident global ipTM) combined with an independent physics-based ΔΔG
(**flex_ddG** in Rosetta). Using two independent methods is a deliberate choice (**D-004**). A third
model (AlphaFold3) is optional. Ratify, or ask for the third method.

### S5-2 — The numeric affinity threshold (defines "improved")  ⚠ blocks the funnel
**Status:** *Open.* The success-metrics file (`configs/metrics.yaml`, metric **M1**) still has its
threshold as a placeholder. Because the scores are noisy (the run-to-run spread is comparable to the
effects we're chasing) and not on an absolute scale, this needs to be a **relative, multi-sample**
gate (improvement over wild-type by at least roughly twice the run-to-run noise, seen across
samples).
**The decision.** Set the M1 affinity gate.
**Recommendation.** Define it as a Δ-vs-wild-type margin with an explicit noise allowance once the
protofibril target (S2-3) is in place — the current numbers are against the monomer-like peptide and
shouldn't be the basis for a permanent threshold.

### S5-3 — How the two scores are combined into one ranking
**Status:** *Needs your sign-off.* We currently combine them by standardising each score and adding
them. Confirm this, or specify weights (e.g. trust the physics ΔΔG more, or the structure score more).

### S5-4 — Precision policy for the physics scorer
**Status:** *Needs your sign-off.* The physics ΔΔG calculation has a fast (noisy) "triage" setting and
a slow (precise) setting. We used the fast setting to screen and intend to re-run only the survivors
at full precision. Confirm this two-tier policy.

---

## Phase 6 — Selectivity, Humanness & Developability  *(the decisive phase — and where the current crossroads is)*

This is the phase that actually enforces the objective. **What happened here is the reason several
items above are flagged urgent**, so it is worth stating plainly.

**What we found.** We took the six best binding-site variants and tested them against the full Aβ
*monomer*, comparing how much each one changed monomer engagement versus epitope engagement, relative
to wild-type. First, the method validated itself: wild-type lecanemab engaged the isolated epitope
much more strongly than the monomer, correctly reproducing its known weak monomer binding. Then the
result: **every one of the six "improved" variants bound the monomer more than wild-type does — and
more than they improved the epitope.** In other words, the variants our affinity ranking had put at
the top were all quietly converting lecanemab into a monomer binder. This is precisely the campaign's
#1 failure mode, caught before any wet-lab spend. The full analysis is in
`results/stage6/SELECTIVITY_FINDING.md`. The deeper lesson is that a *single-arm* binding prediction
cannot, even in principle, separate protofibril from monomer (both display the same epitope; the real
discriminator is avidity, i.e. many epitopes at once). That is what makes the decisions below pivotal.

### S6-1 — The selectivity test protocol and its pass/fail thresholds  ⚠ blocks "what is a hit"
**Status:** *Open.*
**Background.** Selectivity must be judged on the protofibril *target* (S2-3) against *both*
counter-targets: the monomer and the CAA (fixed-N-terminus) fibril. The required margins (metrics
**M2** and **M2b** in the metrics file) are still placeholders.
**The decision.** Define the rule. The natural form is: a variant must engage the protofibril more
than wild-type does, AND must not engage the monomer or the CAA fibril more than wild-type does
(ideally less).
**Recommendation.** Adopt that rule once the protofibril target exists; set the exact margins with the
wild-type baselines in hand.

### S6-2 — How (or whether) to score avidity in silico  ⚠ goes to the core of the objective
**Status:** *Open* (this is open question **OQ-3**).
**Background.** The objective is explicitly about *avidity*-adjusted affinity, but a single-antibody-
arm prediction is monovalent and therefore structurally blind to avidity — which, as Phase 6 showed,
is exactly the property that separates protofibril from monomer. So either we build a way to estimate
avidity, or we accept that the monovalent screens only cover the *conformational/CAA* part of
selectivity and the avidity part is handled by the multivalent format (Phase 7) and the wet lab.
**The decision.** Attempt an avidity-aware score, or formally defer avidity to Phase 7 + experiment.
**Recommendation.** Defer avidity to Phase 7 and the wet-lab assay; use the monovalent screens for the
conformational and CAA axes only, and be explicit that they do not capture monomer selectivity.

### S6-3 — What to do with variants that fail the monovalent monomer screen
**Status:** *Open* (a policy call). We currently marked the six failing variants as "rejected." But
they failed against the *monomer-like peptide*, which we now know is the wrong target. So they may
deserve a second look once the protofibril target exists.
**The decision.** Hard-reject failures, or downgrade them to "deprioritised — re-evaluate on the
protofibril target."
**Recommendation.** Downgrade rather than permanently reject, given the target was the flawed one.

### S6-4 — The developability (biophysical-liability) gate
**Status:** *Open* (requires building the `lecam-dev` tools). Decide the cutoffs (metric **M3**):
typically "no new aggregation, solubility, viscosity, or developability-flag liabilities versus
wild-type."

### S6-5 — The humanness floor
**Status:** *Open* (requires the humanness scorer). Decide metric **M4** — typically "humanness score
no worse than wild-type lecanemab," so we don't reintroduce immunogenicity risk.

---

## Phase 7 — Format, Valency & Delivery  *(where the avidity lever actually lives)*

### S7-1 — Which multivalent format(s) to pursue  ⚠ arguably the highest-impact decision in the campaign
**Status:** *Open.*
**Background.** The objective states that *avidity* — apparent binding strength gained from engaging
many epitopes on a protofibril at once — is the real functional lever (biology fact B7, e.g. the
six-valent "Hexa" research antibody binds soluble aggregates far better). Phase 6 reinforced that
binding-site point mutations alone cannot deliver protofibril-over-monomer selectivity; multivalency
can. This phase is therefore where the campaign's value may actually be created, more than further
binding-site tuning.
**The decision.** Which formats to design toward and model — the standard bivalent antibody as the
baseline, versus higher-valency formats (three, four, six binding arms).
**Recommendation.** Explicitly include a multivalent design arm; do not rely on binding-site
maturation alone to move selectivity.

### S7-2 — Brain-delivery (transferrin-receptor bispecific)
**Status:** *Open.* The lab has a prior project pairing an Aβ binder with a transferrin-receptor arm
to shuttle antibody across the blood–brain barrier. Decide whether brain delivery is in scope here.

### S7-3 — Fc / effector and ARIA engineering
**Status:** *Open* (open question **OQ-4**). The antibody's constant region drives immune-effector
function and is linked to the ARIA side-effect profile. Decide whether engineering it is in scope or
explicitly out of scope for this campaign.

---

## Phase 8 — Experimental Validation & the Active-Learning Loop

### S8-1 — The wet-lab readout
**Status:** *Decided* (**D-005**). Antibody display with a dual selection (select *for* protofibril
binding, *against* monomer binding), then measure binding kinetics by surface-based assays. No action.

### S8-2 — The display platform and reagent preparation
**Status:** *Open* (open question **OQ-2**). Choose yeast-surface versus phage display, and decide how
the protofibril reagent will be produced, stabilised, and immobilised for the counter-selection —
this is a non-trivial experimental dependency that should be planned early because it has a long lead
time.

### S8-3 — Panel size and the "stop computing, start testing" point
**Status:** *Open.* Decide how many variants advance to the wet lab and when we stop iterating in
silico. Recommendation: a modest dual-selection panel (the best few from each track, plus wild-type
and known controls), sized to the experimental budget.

### S8-4 — The active-learning loop
**Status:** *Open.* Decide how measured binding data flows back to re-weight or retrain the
computational rankers, closing the design–test–learn loop.

---

## If you ratify only a few things, make them these

1. **S2-3 — the protofibril target representation.** Until this exists, the affinity axis is measuring
   the wrong thing (it behaves like the monomer), so essentially all downstream scoring is
   provisional. This is the unblocking decision.
2. **S5-2 and S6-1 — the affinity and selectivity thresholds.** Without these, the funnel has no
   definition of "hit," and nothing can be gated.
3. **S6-2 and S7-1 — the avidity policy and whether a multivalent format is in scope.** Phase 6
   strongly suggests this is where real protofibril selectivity comes from — possibly more than from
   binding-site maturation.
4. **S4-4 — reframe generation toward selectivity rather than affinity**, given the Phase-6 finding.

These four are interlinked: the Phase-6 result implies that the campaign's value may sit more in the
*target definition* (S2-3) and the *multivalent format* (S7-1) than in further binding-site
engineering — which is the single most important strategic judgement for you to weigh in on.
