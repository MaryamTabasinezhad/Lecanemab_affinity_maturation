#!/usr/bin/env python
"""Collect Stage-4 variant co-fold scores, compute Δ-ipSAE vs WT, update the ledger.

For each scored variant reads results/stage4/score-<vid>/{ipsae_summary,summary}.json,
compares ipSAE(Fv-Aβ) to the WT Stage-2.2 baseline, writes boltz_ipsae/boltz_iptm/
status='scored'/stage_reached=5 to db/variants.duckdb, and re-exports the CSV.

Run (lecam): env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib \
   conda run -n lecam python scripts/stage4_score/collect_scores.py --vids LEC-AM-T1-0001 ...
"""
import argparse, json
from pathlib import Path
import duckdb

REPO = Path(__file__).resolve().parents[2]
DB = REPO / "db/variants.duckdb"
EXPORT = REPO / "db/exports/variants.csv"
WT_IPSAE = REPO / "results/stage2/cofold-wt-Abeta1-16-11544623/ipsae_summary.json"
WT_SUMMARY = REPO / "results/stage2/cofold-wt-Abeta1-16-11544623/summary.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vids", nargs="+", required=True)
    args = ap.parse_args()

    wt_ipsae = json.load(open(WT_IPSAE))["aggregate"]["ipsae_FvAb_max"]["mean"]
    wt_iptm = json.load(open(WT_SUMMARY))["aggregate"]["iptm"]["mean"]

    con = duckdb.connect(str(DB))
    rows = []
    for vid in args.vids:
        d = REPO / "results/stage4" / f"score-{vid}"
        ip = json.load(open(d / "ipsae_summary.json"))["aggregate"]["ipsae_FvAb_max"]
        sm = json.load(open(d / "summary.json"))["aggregate"]["iptm"]
        mut = con.execute("SELECT mutations FROM variants WHERE variant_id=?", [vid]).fetchone()
        mut = mut[0] if mut else "?"
        delta = round(ip["mean"] - wt_ipsae, 4)
        con.execute("UPDATE variants SET boltz_ipsae=?, boltz_iptm=?, status='scored', stage_reached=5 "
                    "WHERE variant_id=?", [ip["mean"], sm["mean"], vid])
        rows.append({"variant_id": vid, "mutation": mut, "ipsae_mean": ip["mean"],
                     "ipsae_std": ip["std"], "delta_ipsae_vs_wt": delta, "iptm_mean": sm["mean"]})
    con.execute("COPY (SELECT * FROM variants ORDER BY variant_id) TO ? (HEADER, DELIMITER ',')", [str(EXPORT)])
    con.close()

    rows.sort(key=lambda r: -r["delta_ipsae_vs_wt"])
    summary = {"stage": 5, "step": "score_T1_cofold_Abeta1-16",
               "wt_baseline": {"ipsae_FvAb_mean": wt_ipsae, "iptm_mean": wt_iptm,
                               "run": "results/stage2/cofold-wt-Abeta1-16-11544623"},
               "variants": rows,
               "note": "Δ-ipSAE vs WT (single-seq Aβ1-16). Ab-Ag interface confidence noisy "
                       "(ipSAE std ~0.25); |Δ|<~1 std is within noise. T1 framework changes are expected "
                       "~neutral on binding (value is developability/humanness). Pose=hypothesis (D-002)."}
    (REPO / "results/stage4/t1_scores_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"WT ipSAE baseline: {wt_ipsae}")
    for r in rows:
        print(f"  {r['variant_id']} {r['mutation']:12s} ipSAE {r['ipsae_mean']:.3f}±{r['ipsae_std']:.3f}  "
              f"Δ={r['delta_ipsae_vs_wt']:+.3f}  iptm {r['iptm_mean']:.3f}")
    print("SCORE_COLLECT_DONE")


if __name__ == "__main__":
    main()
