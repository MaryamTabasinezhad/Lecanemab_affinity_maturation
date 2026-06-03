#!/usr/bin/env python
"""Aggregate Boltz-2 co-fold confidence across seeds/samples (Stage 2.2 / reusable for variants).

Walks <scratch-dir>/seed_*/.../confidence_*.json, collects per-sample metrics
(iptm/ptm/complex_plddt + chain-pair iptm for the Fv–peptide interface if present),
and writes summary.json (per-sample list + aggregate stats + best sample) to both the
scratch run dir and a small committable copy under <repo-out> (+ manifest.json).
"""
import argparse, glob, hashlib, json, os, statistics as st, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"n": len(xs), "mean": round(st.mean(xs), 4),
            "std": round(st.pstdev(xs), 4) if len(xs) > 1 else 0.0,
            "min": round(min(xs), 4), "max": round(max(xs), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch-dir", required=True)
    ap.add_argument("--repo-out", required=True)
    ap.add_argument("--input-yaml", required=True)
    ap.add_argument("--seeds", default="")
    ap.add_argument("--samples", type=int, default=0)
    args = ap.parse_args()

    scratch = Path(args.scratch_dir)
    files = sorted(glob.glob(str(scratch / "seed_*" / "**" / "confidence_*.json"), recursive=True))
    samples = []
    for f in files:
        d = json.load(open(f))
        # seed from path .../seed_<S>/...
        seed = next((p.split("seed_")[1] for p in Path(f).parts if p.startswith("seed_")), None)
        rec = {"file": str(Path(f).relative_to(scratch)), "seed": seed}
        for k, v in d.items():
            if isinstance(v, (int, float)):
                rec[k] = v
        # chain-pair iptm for the antibody(H/L)–peptide(P) interface, if Boltz emits it
        pair = d.get("pair_chains_iptm")
        if isinstance(pair, dict):
            rec["pair_chains_iptm"] = pair
        samples.append(rec)

    iptm = [s.get("iptm") for s in samples]
    ptm = [s.get("ptm") for s in samples]
    plddt = [s.get("complex_plddt") for s in samples]
    best = max(samples, key=lambda s: (s.get("iptm") or -1)) if samples else None
    summary = {
        "stage": 2, "step": "2.2_cofold_wt_Abeta1-16",
        "n_samples": len(samples), "seeds": args.seeds, "samples_per_seed": args.samples,
        "aggregate": {"iptm": stats(iptm), "ptm": stats(ptm), "complex_plddt": stats(plddt)},
        "best_by_iptm": best,
        "samples": samples,
        "note": "WT baseline. iptm = interface confidence (Fv+Aβ1-16). Pose is a hypothesis (D-002); "
                "single-sequence mode; deltas vs WT use identical settings.",
    }
    (scratch / "summary.json").write_text(json.dumps(summary, indent=2))

    repo_out = Path(args.repo_out); repo_out.mkdir(parents=True, exist_ok=True)
    (repo_out / "summary.json").write_text(json.dumps(summary, indent=2))
    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    yaml_p = Path(args.input_yaml)
    manifest = {
        "stage": 2, "step": "2.2_cofold_wt_Abeta1-16", "tool": "Boltz-2 (lecam-fold)",
        "input_yaml": str(yaml_p.relative_to(REPO)) if yaml_p.is_absolute() else args.input_yaml,
        "input_yaml_sha256": hashlib.sha256(yaml_p.read_bytes()).hexdigest(),
        "seeds": args.seeds, "samples_per_seed": args.samples, "n_samples": len(samples),
        "scratch_outputs": str(scratch), "git_commit": commit,
        "outputs": ["summary.json"],
    }
    (repo_out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("AGG: n_samples", len(samples), "| iptm", summary["aggregate"]["iptm"],
          "| ptm", summary["aggregate"]["ptm"])
    print("BEST iptm", (best or {}).get("iptm"), "seed", (best or {}).get("seed"))
    print("COFOLD_AGG_DONE")


if __name__ == "__main__":
    main()
