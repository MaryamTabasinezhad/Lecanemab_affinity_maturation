# Lecanemab Fv — sequence provenance

**Date sourced:** 2026-06-01 · **Stage:** 1 · **Status:** verified (≥2 independent sources agree)
**Artifact:** `data/raw/lecanemab_fv.fasta`

Lecanemab (Leqembi / BAN2401) = humanized IgG1/κ of murine **mAb158** (BioArctic/Eisai). CAS **1260393-98-3**.

## Sequences (variable domains)

**VH (124 aa, IgG1):**
```
EVQLVESGGGLVQPGGSLRLSCSASGFTFSSFGMHWVRQAPGKGLEWVAYISSGSSTIYYGDTVKGRFTISRDNAKNSLFLQMSSLRAEDTAVYYCAREGGYYYGRSYYTMDYWGQGTTVTVSS
```
**VL (112 aa, κ):**
```
DVVMTQSPLSLPVTPGAPASISCRSSQSIVHSNGNTYLEWYLQKPGQSPKLLIYKVSNRFSGVPDRFSGSGSGTDFTLRISRVEAEDVGIYYCFQGSHVPPTFGPGTKLEIK
```

VH boundary: ...TMDY**WGQGTTVTVSS** | CH1 begins `ASTKGP...` (IgG1).
VL boundary: ...FQGSHVPPT**FGPGTKLEIK** | Cκ begins `RTVAAPSV...`.

## Sources

| # | Source | What it provided | Access |
|---|---|---|---|
| S1 | **KEGG DRUG D11678** (derived from WHO-INN) | Full HC (454 aa) + LC (219 aa); CAS 1260393-98-3; IgG1/κ | https://www.kegg.jp/entry/D11678 |
| S2 | **BioArctic patent US9573994B2** ("Aβ protofibril binding antibodies"; EP2004688 family) | All 6 CDRs explicitly; defines BAN2401 as VL=SEQ ID NO:7, VH=SEQ ID NO:13 | https://patents.google.com/patent/US9573994B2/en |

**Independence:** S1 traces to the WHO-INN nomenclature submission; S2 is the originator's patent. Distinct provenance chains.

## Cross-verification (S1 ↔ S2)

All six patent CDRs are found verbatim inside the KEGG VH/VL:

| CDR | US9573994B2 | In KEGG Fv |
|---|---|---|
| VH-CDR1 (SEQ ID NO:1) | `SFGMH` | ✓ |
| VH-CDR2 (SEQ ID NO:2) | `YISSGSSTIYYGDTVKG` | ✓ |
| VH-CDR3 (SEQ ID NO:3) | `EGGYYYGRSYYTMDY` | ✓ |
| VL-CDR1 (SEQ ID NO:4) | `RSSQSIVHSNGNTYLE` | ✓ |
| VL-CDR2 (SEQ ID NO:5) | `KVSNRFS` | ✓ |
| VL-CDR3 (SEQ ID NO:6) | `FQGSHVPPT` | ✓ |

CDR labels above follow the patent (≈Kabat). Formal IMGT/Kabat/Chothia numbering + Vernier annotation is the next Stage-1 step (ANARCI, pending the `lecam` env).

## Full constant-containing chains (KEGG D11678, for Stage-7 format work)

**Heavy chain (454 aa):**
```
EVQLVESGGGLVQPGGSLRLSCSASGFTFSSFGMHWVRQAPGKGLEWVAYISSGSSTIYYGDTVKGRFTISRDNAKNSLFLQMSSLRAEDTAVYYCAREGGYYYGRSYYTMDYWGQGTTVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKRVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK
```
**Light chain (219 aa):**
```
DVVMTQSPLSLPVTPGAPASISCRSSQSIVHSNGNTYLEWYLQKPGQSPKLLIYKVSNRFSGVPDRFSGSGSGTDFTLRISRVEAEDVGIYYCFQGSHVPPTFGPGTKLEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC
```
> Note: KEGG HC shows `...EEEQYNSTYRVVSVLTVL...` — the `YRVV` contains a probable transcription nuance vs canonical IgG1 `YRVVSVLTVL`; re-confirm the Fc region against UniProt/IMGT before any constant-region engineering (Stage 7). Does not affect the Fv (Stage 1–6 scope).

## Notes / caveats
- `data/raw/lecanemab_fv.fasta` holds **only the Fv** (VH, VL) — the working unit for Stages 1–6.
- Full chains above retained for Stage-7 valency/Fc work; Fc to be re-verified against UniProt/IMGT before use.
- DrugBank (DB14580) and Thera-SAbDab also list lecanemab but were not machine-readable here (403/blocked); KEGG+patent suffice for the ≥2-source gate.
