# T2 (ProteinMPNN CDR redesign) — first-pass finding (2026-06-04)

**Setup:** vanilla ProteinMPNN on the WT Fv–Aβ1-16 complex; Aβ (P) + all framework FIXED;
all 6 IMGT CDRs (56 positions) designable; temps 0.2/0.3; 96 sequences.

**Result:** every design mutates **27–35 of 56 CDR positions** (min 27, median 31, max 35;
≈55%). Zero designs fall within a conservative edit-distance cap (≤6).

**Interpretation (load-bearing):** off-the-shelf ProteinMPNN essentially **rewrites
lecanemab's CDRs**. It optimizes generic sequence–structure compatibility, but lecanemab's
paratope (CDR-H3-led, per Stage 2.4) is *functionally* specialized for **conformational
selectivity** for the flexible-N-terminus Aβ protofibril — a property ProteinMPNN does not
model. The designs are also conditioned on a single, uncertain pose (D-002; ipSAE noisy).
Advancing such near-complete rewrites would almost certainly **erode the >10⁶ selectivity
(guardrail #1)** — the campaign's #1 failure mode.

**Conclusion:** naive full-CDR ProteinMPNN is **too aggressive** for this conformationally
selective antibody. T2 must be **constrained** to protect the paratope. Options (PI decision):
1. **Fix CDR-H3 (the dominant paratope) + WT-bias the rest** → moderate, lower-risk diversification.
2. **Conservative point mutations only** (cap ~2–4 edits; strong WT bias / per-position picks).
3. **Accept aggressive rewrites** as an exploratory set gated by stringent Stage-6 selectivity
   counter-screening (highest risk/reward).

No variants registered to the ledger from this unconstrained run (by design — they would
violate guardrail 1). Raw designs kept at `mpnn/seqs/wt_complex.fa` for reference.
