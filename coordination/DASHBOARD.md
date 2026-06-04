# Campaign Dashboard — lecanemab-am

**Last updated:** 2026-06-04 by frontenac — **T1 scored by 2 independent scorers** (Boltz-2 Δ-ipSAE + Rosetta flex_ddG): all binding-neutral (consensus, D-004 met). lecam-rosetta built. No SLURM jobs running.

## Cluster status
| Cluster | Agent | Current work | SLURM jobs | Last update |
|---|---|---|---|---|
| Frontenac | F | T1 2-scorer consensus done (binding-neutral); next: build lecam-dev (T1 developability) + T2/T3 CDR tracks | — | 2026-06-04 |
| Narval | Narval | not activated | — | — |
| Nibi | Nibi | not activated | — | — |

## Recent actions
| Date | Agent | Action |
|---|---|---|
| 2026-06-04 | frontenac | Built **lecam-rosetta** + **flex_ddG** 2nd scorer (job 11675128): T1 ΔΔG −0.00/+0.06/+0.10 kcal — binding-neutral, agrees with Boltz → 2-scorer consensus |
| 2026-06-04 | frontenac | **Scored T1** (Boltz-2 Δ-ipSAE vs WT, array 11673009): S24A −0.077, T70S −0.105, A17D −0.136 — neutral-within-noise → ledger status=scored |
| 2026-06-03 | frontenac | **Stage 4 T1**: AbLang2/OAS-prior framework reversions → 3 CDR-preserving variants in ledger (LC:A17D/HC:T70S/HC:S24A); framework already humanized |
| 2026-06-03 | frontenac | Built **lecam-md** (OpenMM CUDA, A100-verified) + **Stage 2.3 MD**: B3 confirmed (Aβ N-term RMSF 2.1Å/98% coil; core ordered) → STAGE 2 COMPLETE |
| 2026-06-03 | frontenac | **ipSAE on 25 poses**: Fv-Aβ 0.53±0.26 (vs VH-VL 0.96) → iptm-inflation confirmed; M1 baseline = ipSAE → ipsae_summary.json |
| 2026-06-03 | frontenac | **Stage 2.4 pose-cluster + register (GATE MET)**: consensus epitope Aβ1-11/13-15, family 68%, CDR-H3-led; OQ-1 informed → pose_hypotheses.json |
| 2026-06-03 | frontenac | **Stage 2.2 Boltz-2 co-fold** WT Fv + Aβ1-16 (job 11544623, 25 samples): iptm 0.961±0.019, peptide contacts both VH&VL → results/stage2/cofold-wt-Abeta1-16-11544623 |
| 2026-06-03 | frontenac | **Stage 2.1 WT Fv model** (ABodyBuilder2): framework 0.25Å / CDR-H3 0.82Å pred error → results/stage2/fv-wt-20260603 |
| 2026-06-03 | frontenac | **Boltz-2 A100 smoke test PASSED** (job 11542978, GB1 ptm 0.909); boltz[cuda]+torch2.12 cu130 required; R-MODULES resolved (no partition/CUDA module) |
| 2026-06-03 | frontenac | Built **lecam-fold** (Boltz-2, +affinity model) & **lecam-chai** (Chai-1) co-folding oracles; weights cached on scratch (7.9G+6.6G); split envs (dep conflict) |
| 2026-06-03 | frontenac | Built **lecam-ab** env (ImmuneBuilder/IgFold/AntiBERTy/AbLang2, torch2.5.1 cpu); solved CC wheelhouse + _manylinux pip hazards |
| 2026-06-03 | frontenac | Phase-0 env mapping → `docs/env/env_mapping.md` + `frontenac.env` (design/AF2/PyRosetta covered; lecam-ab/-fold/-dev build-needed) |
| 2026-06-03 | frontenac | Resolved monomer template (D-009: 1Z0Q); fetched antigen mmCIFs (`coords/`, fetch script); 5MY4≠D3 (anti-pyroGlu c#17) → pinned B5; resolved OQ-7 → D-010 (homology set 6CO3/5CSZ/3BKJ/4HIX, 5MY4 weak proxy) |
| 2026-06-01 | frontenac | Built `lecam` env (conda-forge; D-007); initialized DuckDB ledger; verified+numbered lecanemab Fv (D-008); identified antigen templates; extracted B1–B7 |
| 2026-05-30 | frontenac | Repo scaffold + coordination layer created |
