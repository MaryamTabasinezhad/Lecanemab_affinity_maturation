# D-009 — Aβ-monomer counter-target template

**Date:** 2026-06-03 · **Status:** accepted · **Stage:** 1→2 (counter-screen prep)
**Resolves:** HANDOFF/PROJECT_STATUS open item "pick Aβ-monomer counter-target template (1IYT/1Z0Q/2LFM)".

## Context
The selectivity guardrail (#1) and success metric M2 require a **monomer counter-screen**:
`Δprotofibril − Δmonomer > 0 AND ≥ WT`. The monomer is an intrinsically disordered
peptide, so the "template" is a reference ensemble, not a single rigid pose. We need a
template that (a) is the **soluble aqueous monomer** (not a membrane/apolar form), and
(b) is **sequence-matched** to the targets for an apples-to-apples selectivity delta.
The Aβ42 targets are 9CO4 (oligomer), 7Q4B/7Q4M (type I/II fibril), 8BFZ (Arctic).

## Evidence (RCSB-grounded, 2026-06-03)
| ID | Aβ | Method / models | Citation condition | Verdict |
|---|---|---|---|---|
| 1IYT | Aβ42 | NMR, 10 | "in an **apolar microenvironment** … similarity with a virus fusion domain" (Eur J Biochem 2002) | **reject** — helical, non-physiological for the soluble aqueous monomer |
| 1Z0Q | Aβ42 | NMR, 30 | "**Aqueous** Solution Structure … Aβ(1-42) … reversible α→β transition" (ChemBioChem 2006) | **primary** — aqueous, largest ensemble, Aβ42 sequence-matched |
| 2LFM | Aβ40 | NMR, 20 | "partially folded … Aβ(1-40) in an **aqueous** environment" (BBRC 2011) | **control** — Aβ40-matched, pairs with the Aβ40 CAA counter-target 8QN7 |

## Decision
- **Primary monomer counter-target = Aβ42**, reference template **1Z0Q** (aqueous, 30-model ensemble).
- **Reject 1IYT** as the monomer reference: solved in an apolar microenvironment → helical, not representative of the disordered aqueous monomer that lecanemab counter-selects against.
- **Keep 2LFM (Aβ40)** as an Aβ40-sequence-matched monomer control to contrast against the Aβ40 CAA fibril (8QN7) when an Aβ40-vs-Aβ40 selectivity readout is wanted.
- Per **D-002** (pose ensemble) + the stochasticity discipline (§8), the Stage-2 counter-screen **folds the Aβ monomer multi-seed** (model generates its own ensemble); 1Z0Q/2LFM serve as validated experimental references, not a single docked pose.

## Consequences
- `data/raw/antigen/antigen_templates.md` updated; coordinates fetched to `coords/` (git-ignored).
- Feeds M2 (`M2_selectivity_monomer`) once Stage-2 WT baseline scores exist.
- Does not, by itself, set the M2 threshold (still TODO pending the WT baseline).

## Sources
- RCSB REST `data.rcsb.org/rest/v1/core/entry/{1IYT,1Z0Q,2LFM}` (titles, methods, model counts, citations) — fetched 2026-06-03.
- Objective + guardrail: CLAUDE.md §2, §9(1); D-002.
