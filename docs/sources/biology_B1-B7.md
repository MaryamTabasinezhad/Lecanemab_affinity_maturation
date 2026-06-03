# Load-bearing source sentences — biology facts B1–B7

Per CLAUDE.md §8 (source-grounded): every biological claim cites an **exact sentence**. Keys map to CLAUDE.md §3 / §11.
**Date:** 2026-06-01.

---

## B1 — Lecanemab = humanized mouse mAb158; Aβ-protofibril-selective
**Source:** R-NMR — Aβ NMR review, PMC10205579.
> "This antibody drug is a humanized version of a mouse monoclonal antibody, mAb158, which is specific for a soluble protofibril of Aβ(1–42)."
(Introduction, first paragraph.)

## B2 — >10⁶-fold selectivity for Aβ42 protofibril vs Aβ1-16 monomer
**Source:** R-ANA — *Ann Neurol* 2025, doi:10.1002/ana.27175.
> ⚠ **Exact sentence pending** — full text paywalled at fetch time (2026-06-01). The >10⁶-fold protofibril-vs-monomer selectivity figure is carried in CLAUDE.md §3 B2 from this source. **TODO:** retrieve verbatim sentence from the PDF/library and paste here. (Corroborating, weaker public figure: "high selectivity over monomer (>1000-fold)" appears in multiple reviews, e.g. the phase-2b trial paper — but the load-bearing >10⁶ claim must come from R-ANA.)

## B3 — Conformational epitope in N-terminal region; binding requires a flexible/unstructured N-terminus
**Sources:** R-TG (PMC12152531); R-ELIFE (eLife 106156).
> (R-TG) "type I, type II and murine type III amyloid-β fibril polymorphs" share "a flexible N-terminus".
> (R-ELIFE) "Lecanemab can bind to an epitope located in the N-terminal region of the Aβ sequence."
> (R-ELIFE) "the data suggest that additional structural contributions beyond the minimal N-terminal epitope are required for lecanemab binding to aggregated Aβ, which remain to be fully resolved."

## B4 — Spares fixed-N-terminus (SwDI / meningeal CAA Aβ40) fibrils → links to low ARIA-E
**Source:** R-TG — PMC12152531.
> The tg-SwDI structures "exhibit well-ordered and fixed N-termini" (folds DI1, DI2, DI3); human meningeal Aβ40 fibrils similarly show "structured N-termini" comparable to tg-SwDI DI1.
(Contrast with B3's flexible-N folds = engaged. This flexible-vs-fixed N-terminus axis is the structural basis of the conformational selectivity and the CAA-sparing / low-ARIA link.)

## B5 — No public lecanemab Fab–Aβ co-structure; modeled by similarity to antibody D3 (PDB 5MY4)
**Sources:** R-ELIFE (eLife 106156); R-REV (Revvity).
> (R-ELIFE) Under the tested conditions, "Lecanemab showed a certain, but not absolute preference for aggregated forms of Aβ1–42 over monomeric and low-n oligomeric forms." (Consistent with no co-structure; epitope inferred, not co-crystallized.)
> **(R-ELIFE, pinned 2026-06-03)** "Lecanemab's binding profiles align closely with the model proposed on the basis of **D3 antibody similarity (PDB 5MY4)**, correctly accounting for sequence tolerances at positions **3–7**." Modeling is by homology because "chemical structural information regarding the binding of lecanemab to amyloid beta has not yet been released in the global Protein Data Bank." (eLife 106156 / PMC12424645.)
> ⚠ **5MY4 identity caveat (verified RCSB 2026-06-03):** the *deposited* content of PDB 5MY4 is "Fab **c#17** in complex with human Aβ-pE3-12" — an anti-**pyroglutamate-Aβ** antibody (JBC 2017) against the N-truncated/modified pE3 species, **not** a full-length Aβ(1-16) N-terminal binder. R-ELIFE's "D3"/5MY4 attribution is reproduced faithfully here, but 5MY4 is a weak/indirect homology proxy for lecanemab's epitope → see OQ-7 (expand pose-ensemble templates with full-length N-terminal anti-Aβ Fabs: aducanumab 6CO3, gantenerumab 5CSZ, 3D6/bapineuzumab, WO2 3BKJ).
> R-REV (Revvity) corroborates "no lecanemab co-structure in the PDB" (B5) — exact sentence still to pin.

## B6 — Epitope register is model-dependent (hypothesis set, not a fixed pose)
**Source:** R-ELIFE — eLife 106156 + internal.
> (R-ELIFE) "additional structural contributions beyond the minimal N-terminal epitope are required … which remain to be fully resolved" → register/pose is not fixed.
Internal hotspots (Y10/E11/H13/H14/Q15/K16) vs literature "N-terminal, tolerant 3–7" → treat as **hypothesis set** (D-002). Do not tune to one pose.

## B7 — Multivalency (Hexa-RmAb158) raises binding strength to soluble aggregates → avidity is the functional lever
**Source:** R-HEXA — *Transl Neurodegener* 2021, doi:10.1186/s40035-021-00258-x, PMC8477473.
> "Hexa-RmAb158 displayed a much slower dissociation with an almost straight dissociation curve" (vs bivalent RmAb158, binding protofibrils).
> Kinetics: "a k_d value of 2.1 × 10⁻⁷ s⁻¹, and an affinity K_D of 1 pM … ~40 times lower than the k_d and K_D values of RmAb158."
(Directly grounds the §2 objective: avidity, not monovalent KD, is the lever.)

---

## Open items
- **B2:** pin the exact >10⁶-fold sentence from R-ANA (paywalled at fetch).
- **B5:** R-ELIFE D3/5MY4 homology sentence PINNED (2026-06-03); 5MY4 identity caveat added (→ OQ-7). R-REV exact "no co-structure" sentence still to pin.
- R-SD (ScienceDirect S1044743124000344) not yet fetched — secondary corroboration for B3.
- Store any retrieved PDFs/sentences alongside this file; update CLAUDE.md §11 keys only via the coordinator.
