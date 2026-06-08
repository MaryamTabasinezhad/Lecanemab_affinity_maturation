# Protofibril-target model — design notes + feasibility (2026-06-06)

PI chose to fix the in-silico target so the affinity axis is aggregation-specific (vs the
current Aβ1-16 peptide ≈ monomer epitope). Goal: a target where the Aβ N-terminal epitope is
displayed on a rigid, epitope-dense protofibril core with a FLEXIBLE N-terminus (B3), so a
variant can be selected for protofibril-over-monomer engagement.

## Structural ground truth (from fetched coords)
- **9CO4** (designated primary target; brain-derived Aβ42 oligomer) & **7Q4B** (type I fibril):
  10 stacked Aβ42 chains, ordered core **res 9-42**, **N-terminus 1-8 unresolved = flexible**.
  → exactly the B3 protofibril: rigid epitope-dense core + protruding flexible N-terminal epitope.
- **8QN7** (CAA counter, Aβ40): N-terminus **1-38 fully ordered** = fixed/buried (B4) → spared.
- Monomer (1Z0Q/2LFM): fully disordered.

## Feasibility test (FAILED, informative)
Boltz co-fold: WT Fv + 3× free Aβ42 (de novo). Result: the 3 Aβ chains **self-aggregated**
(P-Q-R: 52-138 CA contacts <8 Å, min 3.5 Å — fibril-like stack formed) but the **Fv did NOT
bind** (every Fv×Aβ ipSAE = 0.000; only intra-Fv H-L = 0.89). Aβ-Aβ self-association dominates;
the antibody is left unbound. → **A de-novo multi-chain co-fold cannot serve as the protofibril
target.**

## Validated build plan (next)
Template the protofibril from the REAL structure; do not let Boltz refold the Aβ:
1. Extract a 3-5 chain segment of the **9CO4** stacked core (res 9-42) as a FIXED scaffold;
   model back the flexible N-terminus (1-8) on a central chain → epitope 1-16 protruding.
2. **Dock** the WT Fv onto that protruding N-terminus (PyRosetta in `lecam-rosetta`: seed from
   the Stage-2 pose by superposing the bound Aβ1-16 onto the central chain's 9-16, then
   local docking/refinement + interface score), OR use Boltz pocket/contact constraints to
   pin the Fv near the central chain's N-terminus while keeping the Aβ as the fixed stack.
3. Validate on WT: require ipSAE/interface_score(protofibril) > monomer (0.14) — i.e., the
   model must reproduce the conformational preference before scoring variants.
4. Re-screen T2 (and future tracks) on Δprotofibril − Δmonomer (M2) + CAA axis (8QN7 fixed-N).

## Caveat
Even a templated monovalent dock captures only the CONFORMATIONAL selectivity (rigid core +
presented flexible N-terminus, B3/B4) — NOT avidity (the dominant monomer-selectivity lever,
Stage 7). Both are needed; this addresses the conformational axis.

---

## Build attempt 1 — rigid graft of the WT Fv pose onto 9CO4 (2026-06-08)
`scripts/stage6_select/build_protofibril_target.py`: superposed the Stage-2 WT co-fold (Fv + bound
Aβ1-16) onto a central 9CO4 chain (F) via the overlapping ordered epitope residues 9-16, then assembled
Fv + bound epitope + the 10-chain 9CO4 core.

**Result = OCCLUDED (informative failure):** align RMSD on res 9-16 = **3.4 Å** (the epitope's 9-16
backbone is in a different conformation in the cross-β fibril than in our free-peptide-bound pose);
the grafted Fv has **80 clashing atoms (<2.5 Å)** with the protofibril core (183 contacts <4.5 Å).
→ The free-peptide binding pose **does not transfer** to the protofibril by rigid superposition.

**Interpretation.** Two things differ between the free-peptide target and the protofibril: (1) the
ordered epitope (9-16) adopts the cross-β fibril conformation, not the free conformation our Fv bound;
(2) the rigid stacked core sterically blocks the free-peptide approach. This is exactly *why* the
free 1-16 peptide was a poor target proxy — and it means a protofibril complex must be obtained by
**flexible docking**, not grafting.

## Refined build plan (flexible docking)
1. Prepare the protofibril receptor: a 3-5 chain 9CO4 segment (central chain + neighbours, res 9-42),
   kept rigid; model the flexible N-terminus (1-8) on the central chain so the epitope 1-16 protrudes
   into solvent.
2. **Dock the Fv** onto the protruding N-terminus allowing it to find a clash-free, core-compatible
   binding mode (PyRosetta local docking biased to the N-terminal epitope, fibril core fixed; or
   Boltz with pocket/contact constraints to the central chain's N-terminus). Refine + relieve clashes.
3. **Validate on WT** before trusting it: require WT to engage the protofibril favourably AND
   (key control) to be **occluded on 8QN7** (CAA, ordered N-terminus 1-38) — reproducing B3 (binds
   flexible-N protofibril) vs B4 (spares fixed-N CAA). Only then score variants on Δprotofibril−Δmonomer.

---

## Build attempt 2 — PyRosetta local docking (PIPELINE VALIDATED, 2026-06-08)
`scripts/stage6_select/dock_fv_protofibril.py` (modes: `seed`, `dock`).
- **Clash-free seed works:** geometric placement (paratope facing the epitope, 12 Å standoff) onto a
  3-chain 9CO4 segment (E/F/G, res 9-42, central F) gives **0 Fv–receptor clashes** (vs 80 for the
  rigid graft). `results/stage6/dock_9co4_wt/seed_report.json`.
- **Local dock works:** PyRosetta `DockMCMProtocol` (receptor rigid) + `InterfaceAnalyzerMover` →
  WT Fv docks onto the 9CO4 epitope with a favourable refined interface: **dG_separated −5.69 REU,
  16 interface residues, 459 Å² buried** (1-decoy smoke test). Scaled run (20 decoys) = job 11950541.
- **Methods-consistency requirement found:** InterfaceAnalyzer on the *raw* Boltz monomer complex
  gives +257 REU (it is not Rosetta-relaxed) — meaningless. **Target and every counter-target must be
  scored through the IDENTICAL dock+refine protocol** (DockMCM already refines), else the numbers are
  not comparable. → monomer/CAA baselines must be re-docked/refined the same way, not InterfaceAnalyzer'd raw.

## Remaining for a usable selectivity score (next)
1. Robust WT 9CO4 score (multi-decoy; job 11950541) + the same protocol on the **monomer** (dock WT
   Fv onto free Aβ1-16) and **CAA**.
2. CAA control needs the **8QN7 fibril stack** (deposited cif is 1 chain; apply helical symmetry to
   build neighbours so the ordered N-terminus is packed/occluded) — the key B4 discriminator.
3. Validate: WT favourable on 9CO4, occluded/worse on 8QN7; only then re-screen variants on the
   protofibril-vs-monomer/CAA margin.
4. Caveat stands: monovalent docking captures conformational + steric (B3/B4) selectivity, NOT avidity
   (the monomer lever) — that remains Stage 7 + wet-lab.

---

## WT VALIDATION (2026-06-08) — model reproduces B3/B4 and explains §2
Same DockMCM+InterfaceAnalyzer protocol on all three forms (`results/stage6/protofibril_model/wt_validation.json`):
- **Monomer** (free Aβ1-16): dG **-27.56 REU** (49 int res, 1487 Å²) — Fv wraps the whole flexible epitope.
- **Protofibril** (9CO4): dG **-8.62 REU** (9 int res, 362 Å²) — only the protruding accessible part engaged.
- **CAA** (8QN7 5-rung stack via NCS op2/op5): **OCCLUDED** (seed 205 clashes; N-term 1-16 buried, 16/16 CA <5 Å to neighbour rungs).

**Validated:** B3 (protofibril engageable) + B4 (CAA occluded). **Key insight:** monovalent affinity is
*higher* for the MONOMER than the protofibril → the protofibril preference is **avidity**, not monovalent
affinity. This mechanistically explains why the Stage-6 affinity-improving CDR variants drifted to monomer,
and validates the §2 objective. **Design implication:** select variants improving the restricted
protofibril interface WITHOUT improving the monomer wrap.
