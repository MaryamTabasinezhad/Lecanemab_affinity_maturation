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
