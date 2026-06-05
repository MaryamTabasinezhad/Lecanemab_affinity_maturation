# Stage 6 — monomer selectivity counter-screen of the top T2 hits (2026-06-04)

**Setup:** Boltz-2 multi-seed co-fold of WT + the top-6 T2 hits (by affinity consensus)
against the **full Aβ42 monomer** (counter-target), vs their Aβ1-16 **epitope** engagement
(target proxy). Metric M2 (monovalent proxy): `sel_margin = ΔT − ΔM`, ΔT = target-axis change
vs WT, ΔM = monomer-axis change vs WT. Want `sel_margin > 0` AND `ΔM ≤ 0` (no monomer drift).

## Result

**WT sanity (method works):** ipSAE epitope **0.53** vs Aβ42 monomer **0.14** — WT strongly
prefers the isolated N-terminal epitope over the monomer-embedded one (mirrors lecanemab's
known weak monomer binding). The screen discriminates correctly.

| Variant | mutation | ΔT (epitope) | ΔM (monomer) | sel_margin | verdict |
|---|---|---|---|---|---|
| T2-0026 | HC:G59D;R112B→D | +0.130 | **+0.208** | −0.078 | monomer-drift |
| T2-0030 | HC:T29D;LC:K56N | +0.143 | **+0.331** | −0.188 | monomer-drift |
| T2-0021 | LC:K56N;V114Y | +0.210 | **+0.405** | −0.195 | monomer-drift |
| T2-0017 | LC:H31A | +0.015 | **+0.219** | −0.204 | monomer-drift |
| T2-0019 | HC:Y110P;V114Y | +0.136 | **+0.347** | −0.211 | monomer-drift |
| T2-0001 | LC:V114Y | +0.095 | **+0.355** | −0.260 | monomer-drift |

**Every top T2 hit FAILS selectivity** — all increase monomer engagement *more* than epitope
engagement. The affinity-only ranking's best candidates are converting lecanemab toward a
**monomer binder** → the #1 failure mode (guardrail 1). All 6 marked `status=rejected`,
`monomer_screen=positive`.

## Why this matters (campaign-defining)

This **validates the §2 objective in silico**: naively improving *monovalent* affinity to the
N-terminal epitope erodes the conformational/avidity-based selectivity. The counter-screen
rejected exactly the variants the affinity score ranked highest — before any wet-lab spend.

**Methodological crux:** a single-Fv (monovalent) co-fold cannot distinguish protofibril from
monomer — both present the same N-terminal epitope; the >10⁶ selectivity is **avidity**-based
(epitope density), not monovalent. So *any* monovalent affinity gain shows up as a monomer
gain. To find genuinely protofibril-SELECTIVE improvements in silico we need either:
- **(A) Avidity modeling / multivalent formats (Stage 7)** — the real lever (B7, Hexa-RmAb158);
- **(B) A protofibril/oligomer target model** (e.g., Fv vs a stacked-Aβ assembly / 9CO4 oligomer)
  so the target axis is genuinely aggregation-specific and differs from the monomer;
- **(C) Selectivity-aware generation** — design CDR mutations that improve epitope WITHOUT
  improving monomer (counter-screen inside the generation loop).

## Caveats
Monovalent proxy; ipSAE noisy (guardrail 5); target = isolated 1-16 peptide (not a true
protofibril); CAA/fixed-N axis (M2b) deferred (needs a fibril-templated model). The DIRECTION
(all 6 monomer-drift, ΔM ≫ ΔT) is consistent and strong; the magnitudes are soft. Wet-lab
display + counter-selection remains the decision (guardrail 5).
