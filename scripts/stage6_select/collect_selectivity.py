#!/usr/bin/env python
"""Stage 6 — monomer selectivity margin for the top T2 hits (M2-style, monovalent proxy).

Compares each variant's effect on engaging the Aβ1-16 EPITOPE (target proxy) vs the full
Aβ42 MONOMER (counter-target):
   ΔT = ipSAE_epitope(var) - ipSAE_epitope(WT)      [target axis; from T2 scoring]
   ΔM = ipSAE_monomer(var) - ipSAE_monomer(WT)       [monomer counter; this run]
   sel_margin = ΔT - ΔM            (want > 0 AND ΔM <= 0 = no monomer drift; guardrail 1)
A variant with ΔM > 0 binds the monomer MORE than WT -> selectivity erosion (REJECT-flag).

CAVEATS (honest): monovalent co-fold cannot capture the avidity-based >10^6 monomer
selectivity (that's Stage 7 valency + wet-lab); the "target" is the isolated 1-16 peptide,
not a true protofibril; CAA/fixed-N axis (M2b) needs a fibril-templated model (deferred).
This is a coarse FIRST FILTER, not a verdict. Run in lecam.
"""
import argparse, json
from pathlib import Path
import duckdb

REPO = Path(__file__).resolve().parents[2]
DB = REPO / "db/variants.duckdb"
EXPORT = REPO / "db/exports/variants.csv"
WT_EPITOPE = json.load(open(REPO / "results/stage2/cofold-wt-Abeta1-16-11544623/ipsae_summary.json"))["aggregate"]["ipsae_FvAb_max"]["mean"]


def ipsae(vid):
    f = REPO / "results/stage4" / f"score-{vid}" / "ipsae_summary.json"   # now = monomer co-fold
    return json.load(open(f))["aggregate"]["ipsae_FvAb_max"]["mean"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vids", nargs="+", required=True)
    args = ap.parse_args()
    # epitope (target) ipSAE per variant from the saved T2 scoring summary
    t2 = {r["variant_id"]: r["ipsae"] for r in
          json.load(open(REPO / "results/stage4/t2_scores_summary.json"))["variants"]}
    wt_mono = ipsae("lecanemab_WT")
    con = duckdb.connect(str(DB))
    rows = []
    for vid in args.vids:
        epi = t2[vid]; mono = ipsae(vid)
        dT = round(epi - WT_EPITOPE, 3); dM = round(mono - wt_mono, 3)
        margin = round(dT - dM, 3)
        flag = "MONOMER-DRIFT" if dM > 0.05 else ("ok" if margin > 0 else "neutral/neg")
        mut = con.execute("SELECT mutations FROM variants WHERE variant_id=?", [vid]).fetchone()[0]
        con.execute("UPDATE variants SET sel_monomer_delta=? WHERE variant_id=?", [margin, vid])
        rows.append({"variant_id": vid, "mutation": mut, "ipsae_epitope": epi, "ipsae_monomer": mono,
                     "delta_target": dT, "delta_monomer": dM, "sel_margin": margin, "flag": flag})
    con.execute("COPY (SELECT * FROM variants ORDER BY variant_id) TO ? (HEADER, DELIMITER ',')", [str(EXPORT)])
    con.close()
    rows.sort(key=lambda r: -r["sel_margin"])
    out = {"stage": 6, "step": "monomer_selectivity_topT2", "metric": "M2 (monovalent proxy)",
           "wt_ipsae_epitope": WT_EPITOPE, "wt_ipsae_monomer": round(wt_mono, 3),
           "caveat": "Monovalent proxy; true monomer selectivity is avidity-based (Stage 7/wet-lab). "
                     "Target=Aβ1-16 peptide (not protofibril). CAA/fixed-N axis deferred (needs fibril template). "
                     "Guardrail 5: soft prioritization; display decides.",
           "variants": rows}
    (REPO / "results/stage6/selectivity_topT2.json").write_text(json.dumps(out, indent=2))
    print(f"WT ipSAE: epitope {WT_EPITOPE:.3f} | monomer {wt_mono:.3f}")
    print(f"{'variant':16s} {'mutation':22s} ΔT(epi) ΔM(mono) sel_margin  flag")
    for r in rows:
        print(f"  {r['variant_id']:14s} {r['mutation']:22s} {r['delta_target']:+.3f}  {r['delta_monomer']:+.3f}   {r['sel_margin']:+.3f}   {r['flag']}")
    print("SELECTIVITY_DONE")


if __name__ == "__main__":
    main()
