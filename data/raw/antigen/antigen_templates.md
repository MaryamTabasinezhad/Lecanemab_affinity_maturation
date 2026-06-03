# Antigen template registry — lecanemab AM (Stage 1)

**Date:** 2026-06-03 · **Status:** IDs identified + coordinate files fetched (`coords/`, git-ignored, via `scripts/stage1_inputs/fetch_antigen_templates.sh`). Monomer template resolved (D-009). ⚠ 5MY4 identity caveat — see Reference section.
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
| **1Z0Q** | Aβ42 monomer, **aqueous** NMR (30 models) | Aβ42 | disordered | **primary monomer counter-screen** (D-009) | Danielsson, ChemBioChem 2006 ("Aqueous Solution Structure ... Aβ(1-42)") |
| **2LFM** | Aβ40 monomer, aqueous NMR (20 models) | Aβ40 | disordered | Aβ40-matched monomer control (D-009) | Vivekanandan 2011 ("partially folded ... Aβ(1-40) in an aqueous environment") |

> R-TG: tg-SwDI (DI1/DI2/DI3) and human meningeal Aβ40 show "well-ordered and fixed N-termini" → lecanemab-spared (links to low ARIA-E, B4).

## REFERENCE / homology — pose-ensemble template set (D-002, D-010 / OQ-7 resolved)

Full-length **N-terminal anti-Aβ Fab co-structures** = the primary homology set for the lecanemab epitope (1–16) pose ensemble. 5MY4 is retained only as an annotated weak proxy.

| ID | What | Epitope | Role |
|---|---|---|---|
| **6CO3** | aducanumab–Aβ complex | Aβ 3–7 | primary homology (extended N-term) |
| **5CSZ** | gantenerumab Fab + Aβ1-11 | Aβ 1–11 | primary homology |
| **3BKJ** | WO2 Fab + Aβ1-16 | Aβ 1–16 | primary homology (**closest to lecanemab's 1–16 window**) |
| **4HIX** | humanised 3D6 (bapineuzumab precursor) Fab + Aβ | Aβ N-term (1–7) | primary homology |
| **5MY4** | Fab **c#17**, anti-**pyroglutamate**-Aβ (pE3-12) — *not* "D3" per RCSB | pE3-12 (truncated/modified) | **weak proxy only** (R-ELIFE cite; see caveat) |

> ⚠ **5MY4 identity caveat (verified 2026-06-03, RCSB + R-ELIFE).** R-ELIFE (eLife 106156 / PMC12424645) models lecanemab "on the basis of **D3** antibody similarity (PDB **5MY4**), correctly accounting for sequence tolerances at positions **3–7**." Our B5/CLAUDE.md faithfully reflect that sentence. **However, the deposited content of 5MY4 (RCSB, JBC 2017) is "Fab c#17 in complex with human Aβ-pE3-12" — an anti-*pyroglutamate-Aβ* antibody against the N-truncated, modified pE3 species, not a full-length Aβ(1-16) N-terminal binder.** It is therefore a *weak/indirect* homology proxy for lecanemab's conformational N-terminal epitope. Better-matched **full-length N-terminal anti-Aβ Fab co-structures** (aducanumab **6CO3**, gantenerumab **5CSZ** Aβ1-11, 3D6/bapineuzumab **4HIX**, WO2 **3BKJ** Aβ1-16) are now the **primary homology set** and 5MY4 is demoted to a weak proxy — **OQ-7 resolved by PI 2026-06-03 → D-010** (see table above).

## Notes / open items
- **Monomer template — RESOLVED (D-009):** primary = **1Z0Q** (Aβ42, aqueous, 30-model ensemble; sequence-matched to the Aβ42 targets). **1IYT rejected** (solved "in an apolar microenvironment" → helical, non-physiological for the soluble aqueous monomer). **2LFM** (Aβ40, aqueous) kept as the Aβ40-matched control to pair against the Aβ40 CAA counter-target (8QN7). Per D-002 + stochastic discipline, the Stage-2 counter-screen folds the Aβ monomer multi-seed (its own ensemble); 1Z0Q/2LFM are the validated experimental references.
- **EMDB maps:** cryo-EM density (EMDB) IDs for 7Q4B/7Q4M/8BFZ/8QN7/8OLN not yet recorded — add when fetching maps (large data → Globus, not git).
- **Download — DONE:** coordinate mmCIFs fetched to `coords/` (git-ignored) by `scripts/stage1_inputs/fetch_antigen_templates.sh` (idempotent, `--dry-run`); see `coords/fetch_manifest.tsv`. EMDB maps still deferred (large → Globus).
- **Register meaning:** epitope register is a hypothesis set (B6, D-002) — these templates feed the pose **ensemble**, not a single pose.
