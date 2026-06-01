# Antigen template registry — lecanemab AM (Stage 1)

**Date:** 2026-06-01 · **Status:** IDs identified (downloads deferred — see notes).
Curated per CLAUDE.md §4. Roles map to the objective (§2): **target** = Aβ protofibril/oligomer (flexible N-terminus); **counter-targets** = Aβ monomer + fixed-N-terminus/CAA Aβ40 fibril. Selectivity margin is computed target − counter-target (§2 metric 2).

## TARGET — Aβ protofibril / oligomer / fibril (flexible, unstructured N-terminus → engaged)

| ID | Type | Aβ | N-terminus | Role | Source |
|---|---|---|---|---|---|
| **9CO4** | brain-derived Aβ42 oligomer, **Conformation 1** | Aβ42 | (internal: receptor-bound target) | primary target | internal (CLAUDE.md §4) |
| **7Q4B** | fibril **Type I** (sporadic AD) | Aβ42 | flexible | target fold | Yang et al., Science 2022 (PMC7612234) |
| **7Q4M** | fibril **Type II** (familial AD) | Aβ42 | flexible | target fold | Yang et al., Science 2022 |
| **8BFZ** | fibril **Arctic** (E22G) | Aβ42 | flexible (ordered from ~E11/V12) | target fold (Arctic) | RCSB 8BFZ |

> R-TG (PMC12152531): type I, type II and murine type III polymorphs "share a flexible N-terminus" → lecanemab-engageable.

## COUNTER-TARGETS — must stay negative (selectivity guardrail #1)

| ID | Type | Aβ | N-terminus | Role | Source |
|---|---|---|---|---|---|
| **9CKI** | brain-derived Aβ42 oligomer, **Conformation 2** | Aβ42 | (internal: plaque/negative) | negative counter-target | internal (CLAUDE.md §4) |
| **8QN7** | **leptomeningeal CAA** fibril | Aβ40 | **fixed/ordered** | CAA counter-target | PMC12152531 (R-TG) |
| **8OLN** | **tg-SwDI DI1** fold | Aβ (SwDI) | **fixed/ordered** | fixed-N counter-target | PMC12152531 (R-TG) |
| _TBD_ | **Aβ monomer / peptide** | Aβ40/42 | disordered | monomer counter-screen | NMR ensembles, e.g. 1IYT/1Z0Q (Aβ42), 2LFM (Aβ40) — **to select** |

> R-TG: tg-SwDI (DI1/DI2/DI3) and human meningeal Aβ40 show "well-ordered and fixed N-termini" → lecanemab-spared (links to low ARIA-E, B4).

## REFERENCE / homology

| ID | What | Use |
|---|---|---|
| **5MY4** | antibody **D3** (anti-Aβ N-terminus) | epitope homology model for lecanemab (B5/B6); no public lecanemab co-structure |

## Notes / open items
- **Monomer template (OQ):** Aβ monomer is intrinsically disordered — pick an NMR ensemble (1IYT, 1Z0Q, 2LFM) and/or model the linear N-terminal peptide; decide in Stage 2.
- **EMDB maps:** cryo-EM density (EMDB) IDs for 7Q4B/7Q4M/8BFZ/8QN7/8OLN not yet recorded — add when fetching maps (large data → Globus, not git).
- **Download:** PDB coordinate files are small (wgettable into `data/raw/antigen/`); EMDB maps are large (Globus). Downloads deferred to a Stage-2 prep step.
- **Register meaning:** epitope register is a hypothesis set (B6, D-002) — these templates feed the pose **ensemble**, not a single pose.
