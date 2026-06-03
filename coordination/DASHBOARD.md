# Campaign Dashboard — lecanemab-am

**Last updated:** 2026-06-03 by frontenac — **STAGE 2 COMPLETE**: Fv model + co-fold (ipSAE 0.53±0.26) + pose gate + 2.3 MD (B3 confirmed: Aβ N-term flexible). All 7 lecam-* envs except lecam-dev built. No SLURM jobs running.

## Cluster status
| Cluster | Agent | Current work | SLURM jobs | Last update |
|---|---|---|---|---|
| Frontenac | F | Stage 2 complete (gate + B3 MD); next Stage 3/4 (paratope→variant gen); build lecam-dev for Stage 6 | — | 2026-06-03 |
| Narval | Narval | not activated | — | — |
| Nibi | Nibi | not activated | — | — |

## Recent actions
| Date | Agent | Action |
|---|---|---|
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
