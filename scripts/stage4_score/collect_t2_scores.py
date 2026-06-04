#!/usr/bin/env python
"""Collect T2 variant scores: Boltz-2 Δ-ipSAE (vs WT) + reduced flex_ddG ΔΔG -> consensus.

Per variant: ipSAE(Fv-Aβ) from results/stage4/score-<vid>/ipsae_summary.json; flex_ddG by
aggregating <scratch>/results/stage5/flexddg/<vid>/*/ddG.db3. Consensus rank = mean of the
two z-scored signals (favoured = higher Δ-ipSAE, more-negative ΔΔG). Updates the ledger
(boltz_ipsae, boltz_iptm, flexddg_kcal, consensus_rank, status=scored). Run in lecam.
"""
import argparse, csv, glob, json
from pathlib import Path
import numpy as np
import duckdb
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_tools/flexddg"))
from aggregate_flexddg import ddg_one  # reuse

REPO = Path(__file__).resolve().parents[2]
DB = REPO / "db/variants.duckdb"
EXPORT = REPO / "db/exports/variants.csv"
WT_IPSAE = json.load(open(REPO / "results/stage2/cofold-wt-Abeta1-16-11544623/ipsae_summary.json"))["aggregate"]["ipsae_FvAb_max"]["mean"]


def flexddg_mean(scratch, vid):
    kc = []
    for f in sorted(glob.glob(f"{scratch}/results/stage5/flexddg/{vid}/*/ddG.db3")):
        r = ddg_one(f)
        if r: kc.append(r[1])
    return (round(float(np.mean(kc)), 3), round(float(np.std(kc)), 3), len(kc)) if kc else (None, None, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True, help="variant_yaml_list_t2.tsv (id<TAB>yaml)")
    ap.add_argument("--scratch", required=True)
    args = ap.parse_args()
    vids = [ln.split("\t")[0] for ln in Path(args.list).read_text().splitlines() if ln.strip()]
    con = duckdb.connect(str(DB))
    rows = []
    for vid in vids:
        ip = json.load(open(REPO / "results/stage4" / f"score-{vid}" / "ipsae_summary.json"))["aggregate"]
        ipsae = ip["ipsae_FvAb_max"]["mean"]; iptm = json.load(open(REPO / "results/stage4" / f"score-{vid}" / "summary.json"))["aggregate"]["iptm"]["mean"]
        dd, ddstd, n = flexddg_mean(args.scratch, vid)
        mut = con.execute("SELECT mutations FROM variants WHERE variant_id=?", [vid]).fetchone()[0]
        rows.append({"variant_id": vid, "mutation": mut, "ipsae": round(ipsae, 3),
                     "delta_ipsae": round(ipsae - WT_IPSAE, 3), "iptm": round(iptm, 3),
                     "flexddg_kcal": dd, "flexddg_std": ddstd, "flexddg_n": n})
    # consensus: z(Δipsae) - z(flexddg)  (higher Δipsae good; lower ΔΔG good)
    di = np.array([r["delta_ipsae"] for r in rows], float)
    fd = np.array([r["flexddg_kcal"] if r["flexddg_kcal"] is not None else np.nan for r in rows], float)
    zi = (di - np.nanmean(di)) / (np.nanstd(di) or 1)
    zf = (fd - np.nanmean(fd)) / (np.nanstd(fd) or 1)
    cons = zi - zf
    order = np.argsort(-cons)
    rank = {int(idx): r + 1 for r, idx in enumerate(order)}
    for i, r in enumerate(rows):
        r["consensus_score"] = round(float(cons[i]), 3); r["consensus_rank"] = rank[i]
        con.execute("UPDATE variants SET boltz_ipsae=?, boltz_iptm=?, flexddg_kcal=?, "
                    "consensus_rank=?, status='scored', stage_reached=5 WHERE variant_id=?",
                    [r["ipsae"], r["iptm"], r["flexddg_kcal"], r["consensus_rank"], r["variant_id"]])
    con.execute("COPY (SELECT * FROM variants ORDER BY variant_id) TO ? (HEADER, DELIMITER ',')", [str(EXPORT)])
    con.close()
    rows.sort(key=lambda r: r["consensus_rank"])
    out = {"stage": 5, "step": "score_T2", "wt_ipsae_baseline": WT_IPSAE,
           "scorers": ["Boltz-2 multi-seed Δ-ipSAE (25 samples)", "flex_ddG zemu-GAM kcal (5 traj, REDUCED backrub=10000 TRIAGE)"],
           "note": "Reduced flex_ddG is a TRIAGE pass; re-run top hits at full nstruct=35/backrub=35000. "
                   "In-silico = soft prioritization (guardrail 5). Selectivity counter-screen (Stage 6) still MANDATORY.",
           "variants": rows}
    (REPO / "results/stage4/t2_scores_summary.json").write_text(json.dumps(out, indent=2))
    print(f"WT ipSAE baseline {WT_IPSAE}. Top 10 T2 by consensus:")
    for r in rows[:10]:
        print(f"  #{r['consensus_rank']:2d} {r['variant_id']} {r['mutation']:20s} "
              f"Δipsae {r['delta_ipsae']:+.3f}  flexddg {r['flexddg_kcal']:+.2f}")
    print("T2_COLLECT_DONE")


if __name__ == "__main__":
    main()
