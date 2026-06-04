#!/usr/bin/env python
"""Aggregate flex_ddG trajectories for one mutation -> ddG (REU + zemu-GAM kcal).

Reads <case-dir>/*/ddG.db3 (one per nstruct trajectory). Per trajectory:
  ddG = (bound_mut - unbound_mut) - (bound_wt - unbound_wt)   [binding; +ve = weaker]
using the final backrub checkpoint per state, for both raw talaris total_score (REU)
and the zemu-GAM-reweighted total (kcal, the published flex_ddG calibration).
Averages over trajectories. Run in lecam (pandas/sqlite).
"""
import argparse, glob, json, sqlite3
from pathlib import Path
import numpy as np

GAM = {"fa_sol": (6.940, -6.722), "hbond_sc": (1.902, -1.999), "hbond_bb_sc": (0.063, 0.452),
       "fa_rep": (1.659, -0.836), "fa_elec": (0.697, -0.122), "hbond_lr_bb": (2.738, -1.179),
       "fa_atr": (2.313, -1.649)}
STATES = ["bound_wt", "unbound_wt", "bound_mut", "unbound_mut"]


def gam(x, term):
    a, b = GAM[term]
    return -np.exp(a) + 2 * np.exp(a) / (1.0 + np.exp(-x * np.exp(b)))


def state_scores(db3):
    """{state: {score_term: value}} at the final backrub checkpoint."""
    c = sqlite3.connect(db3)
    q = """SELECT batches.name n, structure_scores.struct_id sid, score_types.score_type_name t,
                  structure_scores.score_value v
           FROM structure_scores
           INNER JOIN batches ON batches.batch_id=structure_scores.batch_id
           INNER JOIN score_types ON score_types.batch_id=structure_scores.batch_id
                AND score_types.score_type_id=structure_scores.score_type_id"""
    rows = c.execute(q).fetchall(); c.close()
    # latest struct_id per state
    last = {}
    for n, sid, t, v in rows:
        st = n[:-9] if n.endswith("_dbreport") else n
        last.setdefault(st, {})
        last[st].setdefault("_maxsid", -1)
        if sid >= last[st]["_maxsid"]:
            if sid > last[st]["_maxsid"]:
                last[st] = {"_maxsid": sid}
            last[st][t] = v
    return {st: {k: v for k, v in d.items() if k != "_maxsid"} for st, d in last.items()}


def ddg_one(db3):
    s = state_scores(db3)
    if not all(st in s for st in STATES):
        return None
    reu = (s["bound_mut"]["total_score"] - s["unbound_mut"]["total_score"]) - \
          (s["bound_wt"]["total_score"] - s["unbound_wt"]["total_score"])
    g = {st: sum(gam(s[st][t], t) for t in GAM) for st in STATES}
    kcal = (g["bound_mut"] - g["unbound_mut"]) - (g["bound_wt"] - g["unbound_wt"])
    return float(reu), float(kcal)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", required=True)
    ap.add_argument("--variant-id", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    db3s = sorted(glob.glob(f"{args.case_dir}/*/ddG.db3"))
    reus, kcals = [], []
    for f in db3s:
        r = ddg_one(f)
        if r:
            reus.append(r[0]); kcals.append(r[1])
    res = {"variant_id": args.variant_id, "n_trajectories": len(kcals),
           "ddg_reu_mean": round(float(np.mean(reus)), 3) if reus else None,
           "ddg_reu_std": round(float(np.std(reus)), 3) if len(reus) > 1 else 0.0,
           "ddg_gam_kcal_mean": round(float(np.mean(kcals)), 3) if kcals else None,
           "ddg_gam_kcal_std": round(float(np.std(kcals)), 3) if len(kcals) > 1 else 0.0,
           "per_traj_kcal": [round(x, 3) for x in kcals]}
    Path(args.out).write_text(json.dumps(res, indent=2))
    print(f"{args.variant_id}: ddG_gam {res['ddg_gam_kcal_mean']}±{res['ddg_gam_kcal_std']} kcal "
          f"(REU {res['ddg_reu_mean']}±{res['ddg_reu_std']}, n={res['n_trajectories']})")
    print("FLEXDDG_AGG_DONE")


if __name__ == "__main__":
    main()
