#!/usr/bin/env python
"""Stage 2.x — compute ipSAE (Dunbrack 2025) for the 25 WT Fv+Aβ1-16 co-fold poses.

ipSAE is interface-specific and down-weights the trivially-confident intra-Fv (VH-VL)
pairing that inflates Boltz iptm — so it is the metric the WT baseline / variant deltas
should use (guardrail 4 / metrics.yaml M1). Wraps the official scripts/_tools/ipsae.py
(pae_cutoff=10, dist_cutoff=10), parses per chain-pair 'max' ipSAE, aggregates, writes
ipsae_summary.json (+ manifest) to --repo-out.
"""
import argparse, glob, json, subprocess, statistics as st
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
IPSAE = REPO / "scripts/_tools/ipsae.py"


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"n": len(xs), "mean": round(st.mean(xs), 4),
            "std": round(st.pstdev(xs), 4) if len(xs) > 1 else 0.0,
            "min": round(min(xs), 4), "max": round(max(xs), 4)}


def parse_max(txt):
    """Return {frozenset(chnpair): {'ipsae':x,'pdockq':y}} from Type==max rows."""
    out = {}
    for ln in Path(txt).read_text().splitlines():
        p = ln.split()
        if len(p) < 11 or p[4] != "max":
            continue
        out[frozenset((p[0], p[1]))] = {"ipsae": float(p[5]), "pdockq": float(p[10])}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch-dir", required=True)
    ap.add_argument("--repo-out", required=True)
    ap.add_argument("--pae-cutoff", default="10")
    ap.add_argument("--dist-cutoff", default="10")
    args = ap.parse_args()

    pdbs = sorted(glob.glob(f"{args.scratch_dir}/seed_*/**/*_model_*.pdb", recursive=True))
    assert pdbs, "no pose pdbs"
    rows = []
    for pdb in pdbs:
        d = Path(pdb).parent
        stem = Path(pdb).stem
        pae = d / f"pae_{stem.split('_model')[0]}_model_{stem.split('_model_')[1]}.npz"
        subprocess.run(["python", str(IPSAE), str(pae), pdb, args.pae_cutoff, args.dist_cutoff],
                       check=True, capture_output=True)
        txt = d / f"{stem}_{args.pae_cutoff}_{args.dist_cutoff}.txt"
        m = parse_max(txt)
        seed = next((x.split("seed_")[1] for x in Path(pdb).parts if x.startswith("seed_")), None)
        hp = m.get(frozenset(("H", "P")), {})
        lp = m.get(frozenset(("L", "P")), {})
        hl = m.get(frozenset(("H", "L")), {})
        rows.append({
            "pose": f"seed{seed}/{stem}", "seed": seed,
            "ipsae_HP": hp.get("ipsae"), "ipsae_LP": lp.get("ipsae"),
            "ipsae_FvAb_max": max([v for v in (hp.get("ipsae"), lp.get("ipsae")) if v is not None], default=None),
            "ipsae_HL_intraFv": hl.get("ipsae"),
            "pdockq_HP": hp.get("pdockq"), "pdockq_LP": lp.get("pdockq"),
        })

    summary = {
        "stage": 2, "step": "2.x_ipSAE_wt_Abeta1-16", "n_poses": len(rows),
        "pae_cutoff": int(args.pae_cutoff), "dist_cutoff": int(args.dist_cutoff),
        "tool": "ipsae.py v4 (Dunbrack 2025, doi:10.1101/2025.02.10.637595)",
        "aggregate": {
            "ipsae_FvAb_max": stats([r["ipsae_FvAb_max"] for r in rows]),
            "ipsae_HP": stats([r["ipsae_HP"] for r in rows]),
            "ipsae_LP": stats([r["ipsae_LP"] for r in rows]),
            "ipsae_HL_intraFv": stats([r["ipsae_HL_intraFv"] for r in rows]),
            "pdockq_HP": stats([r["pdockq_HP"] for r in rows]),
        },
        "poses": rows,
        "note": "ipSAE is the interface-specific WT baseline (use for delta-vs-WT, M1). Contrast "
                "with iptm 0.961 (inflated by intra-Fv VH-VL). Pose is a hypothesis (D-002).",
    }
    repo_out = Path(args.repo_out); repo_out.mkdir(parents=True, exist_ok=True)
    (repo_out / "ipsae_summary.json").write_text(json.dumps(summary, indent=2))
    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    (repo_out / "manifest_ipsae.json").write_text(json.dumps(
        {"stage": 2, "step": "ipSAE", "tool": "ipsae.py v4", "n_poses": len(rows),
         "pae_cutoff": int(args.pae_cutoff), "dist_cutoff": int(args.dist_cutoff),
         "scratch_dir": args.scratch_dir, "git_commit": commit,
         "outputs": ["ipsae_summary.json"]}, indent=2))
    a = summary["aggregate"]
    print("ipSAE Fv-Aβ (max H/L per pose):", a["ipsae_FvAb_max"])
    print("ipSAE H-P:", a["ipsae_HP"], "| L-P:", a["ipsae_LP"])
    print("ipSAE H-L intra-Fv (sanity, high):", a["ipsae_HL_intraFv"])
    print("IPSAE_DONE")


if __name__ == "__main__":
    main()
