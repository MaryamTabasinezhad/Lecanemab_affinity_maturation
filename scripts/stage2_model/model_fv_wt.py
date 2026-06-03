#!/usr/bin/env python
"""Stage 2.1 — model the WT lecanemab Fv (ABodyBuilder2) and validate geometry.

Reads VH/VL from data/raw/lecanemab_fv.fasta, predicts the Fv with ImmuneBuilder
ABodyBuilder2 (4-model ensemble + per-residue predicted error in the B-factor
column), saves the refined top model, and reports CDR-H3 vs framework confidence
(the CDR-H3 caution from DEVELOPMENT_PLAN Stage 2 / guardrail 2).

Run (login node; weights cached; offline-OK):
  env -u PYTHONPATH PYTHONNOUSERSITE=1 conda run -n lecam-ab \
      python scripts/stage2_model/model_fv_wt.py --run-id fv-wt-YYYYMMDD

Outputs -> results/stage2/<run-id>/ : fv_model.pdb, fv_model_unrefined.pdb,
           geometry_report.json, manifest.json ; plus a copy to data/interim/fv_model.pdb
"""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FASTA = REPO / "data/raw/lecanemab_fv.fasta"
# CDR-H3 IMGT residue span from the Stage-1 map (docs/sources/fv_cdr_vernier_map.md)
CDRH3_SEQ = "AREGGYYYGRSYYTMDY"   # used to locate CDR-H3 residues in the H chain


def read_fv(path):
    seqs, name = {}, None
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            name = "H" if "VH" in line else ("L" if "VL" in line else None)
        elif name:
            seqs[name] = seqs.get(name, "") + line.strip()
    assert "H" in seqs and "L" in seqs, "need VH and VL in fasta"
    return seqs


def bfactors_by_residue(pdb_path, chain):
    """Mean B-factor (= ABodyBuilder2 predicted error, Angstrom) per residue of a chain."""
    res = {}
    for ln in Path(pdb_path).read_text().splitlines():
        if ln.startswith("ATOM") and ln[21] == chain:
            resnum = int(ln[22:26]); b = float(ln[60:66])
            res.setdefault(resnum, []).append(b)
    return {r: sum(v) / len(v) for r, v in res.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    out = REPO / "results/stage2" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    seqs = read_fv(FASTA)

    from ImmuneBuilder import ABodyBuilder2
    import torch
    from importlib.metadata import version as _pkgver
    try:
        ib_version = _pkgver("ImmuneBuilder")
    except Exception:
        ib_version = "unknown"
    predictor = ABodyBuilder2()
    ab = predictor.predict(seqs)               # 4-model ensemble, ranked
    refined = out / "fv_model.pdb"
    ab.save(str(refined))                       # refined top model; B-factor = predicted error (A)

    # geometry: CDR-H3 predicted error vs framework (B-factor col of refined model)
    hb = bfactors_by_residue(refined, "H")
    # locate CDR-H3 residues by matching the loop sequence against the H chain CA records
    h_resnums = sorted(hb)
    seqH = seqs["H"]
    idx = seqH.find(CDRH3_SEQ)
    cdrh3_nums = h_resnums[idx: idx + len(CDRH3_SEQ)] if idx >= 0 else []
    cdrh3_err = [hb[r] for r in cdrh3_nums]
    fw_err = [hb[r] for r in h_resnums if r not in set(cdrh3_nums)]
    report = {
        "n_residues_H": len(hb),
        "mean_pred_error_overall_H": round(sum(hb.values()) / len(hb), 3),
        "cdrh3_residues": cdrh3_nums,
        "cdrh3_mean_pred_error": round(sum(cdrh3_err) / len(cdrh3_err), 3) if cdrh3_err else None,
        "cdrh3_max_pred_error": round(max(cdrh3_err), 3) if cdrh3_err else None,
        "framework_mean_pred_error_H": round(sum(fw_err) / len(fw_err), 3) if fw_err else None,
        "note": "predicted error in Angstrom (ABodyBuilder2 B-factor); CDR-H3 expected highest (guardrail 2).",
    }
    (out / "geometry_report.json").write_text(json.dumps(report, indent=2))

    # mirror top model to data/interim per plan output
    interim = REPO / "data/interim/fv_model.pdb"
    interim.parent.mkdir(parents=True, exist_ok=True)
    interim.write_bytes(refined.read_bytes())

    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    manifest = {
        "stage": 2, "step": "2.1_fv_model", "run_id": args.run_id,
        "tool": "ImmuneBuilder.ABodyBuilder2", "immunebuilder_version": ib_version,
        "torch_version": torch.__version__, "env": "lecam-ab",
        "input_fasta": str(FASTA.relative_to(REPO)),
        "input_fasta_sha256": hashlib.sha256(FASTA.read_bytes()).hexdigest(),
        "seq_H": seqs["H"], "seq_L": seqs["L"],
        "git_commit": commit,
        "outputs": ["fv_model.pdb", "geometry_report.json"],
        "interim_copy": str(interim.relative_to(REPO)),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("WROTE", refined)
    print("GEOMETRY", json.dumps(report))
    print("STAGE2_FV_DONE")


if __name__ == "__main__":
    main()
