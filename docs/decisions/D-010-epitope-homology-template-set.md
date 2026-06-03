# D-010 — Epitope-homology template set (resolves OQ-7)

**Date:** 2026-06-03 · **Status:** accepted (PI sign-off) · **Stage:** 2→3 (epitope/pose ensemble)
**Resolves:** OQ-7. **Relates:** D-002 (pose ensemble, not single pose), B5/B6.

## Context
R-ELIFE (eLife 106156 / PMC12424645) models lecanemab "on the basis of **D3** antibody
similarity (PDB **5MY4**)", and CLAUDE.md B5 carries this. Verification against RCSB
(2026-06-03) shows **5MY4's deposited content is "Fab c#17 in complex with human
Aβ-pE3-12"** — an anti-**pyroglutamate-Aβ** antibody (JBC 2017) recognizing the
**N-truncated, modified pE3 species**, not lecanemab's full-length N-terminal (1–16)
conformational epitope. 5MY4 is therefore a weak/indirect homology proxy. There is no
public lecanemab co-structure (B5), so the epitope must be modeled by homology — and
D-002 mandates a **pose ensemble**, not a single template.

## Decision
**Primary epitope-homology set = full-length N-terminal anti-Aβ Fab co-structures** (all RCSB-verified, X-ray):

| ID | Antibody | Epitope | Note |
|---|---|---|---|
| 6CO3 | aducanumab | Aβ 3–7 | extended N-terminal conformation |
| 5CSZ | gantenerumab | Aβ 1–11 | |
| 3BKJ | WO2 | Aβ 1–16 | **closest to lecanemab's 1–16 window** |
| 4HIX | humanised 3D6 (bapineuzumab precursor) | Aβ N-term (1–7) | |

- **5MY4 demoted to an annotated weak proxy** — retained for traceability to R-ELIFE, but **not** weighted as a primary template (it is an anti-pyroGlu pE3-12 binder).
- These templates feed the **pose ensemble / multi-model consensus** (D-002); no single pose is privileged. Epitope register stays a hypothesis set (B6, OQ-1).

## Consequences
- Coordinates fetched to `data/raw/antigen/coords/` via `fetch_antigen_templates.sh` (git-ignored); registry table updated in `antigen_templates.md`.
- Stage 2/3 epitope modeling draws the homology ensemble from {6CO3, 5CSZ, 3BKJ, 4HIX}; cross-checks vs the internal B6 hotspot set (Y10/E11/H13/H14/Q15/K16) and the "tolerant 3–7" literature register.
- **CLAUDE.md B5 wording unchanged** (it faithfully quotes R-ELIFE); the caveat + this ADR are the correction layer. Any B5 edit is a separate coordinator action.

## Sources
- RCSB REST `core/entry/{5MY4,6CO3,5CSZ,3BKJ,4HIX}` + `core/polymer_entity/5MY4/*` — fetched 2026-06-03.
- R-ELIFE 106156 / PMC12424645 (D3/5MY4 homology sentence, pinned in `docs/sources/biology_B1-B7.md`).
- D-002 (pose ensemble); CLAUDE.md §2, B5, B6.
