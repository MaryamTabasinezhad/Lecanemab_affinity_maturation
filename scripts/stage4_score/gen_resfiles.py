#!/usr/bin/env python
"""Build flex_ddG resfiles from a ledger CSV's IMGT mutation strings.

Inverts the Stage-1 IMGT map to recover Boltz sequential resnums (the PDB numbering
flex_ddG needs). Handles multi-mutation variants (one PIKAA line each). Writes
data/interim/flexddg/<variant_id>.resfile and a variant list (id<TAB>resfile) for the array.
"""
import argparse, csv
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
NUM = REPO / "data/interim/fv_numbering"


def inv_imgt(tsv):
    m = {}
    for k, ln in enumerate(Path(tsv).read_text().splitlines()[1:], 1):
        c = ln.split("\t"); m[f"{c[0]}{c[1] if len(c)>1 else ''}".strip()] = k
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--outdir", default="data/interim/flexddg")
    ap.add_argument("--list-out", required=True)
    args = ap.parse_args()
    inv = {"H": inv_imgt(NUM / "VH_imgt.tsv"), "L": inv_imgt(NUM / "VL_imgt.tsv")}
    out = REPO / args.outdir; out.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in csv.DictReader(open(REPO / args.csv)):
        vid = r["variant_id"]
        lines = ["NATAA", "start"]
        for tok in r["mutations"].split(";"):
            chtag, mut = tok.split(":")           # e.g. HC:R112BD
            ch = "H" if chtag == "HC" else "L"
            wt, m, label = mut[0], mut[-1], mut[1:-1]
            seqpos = inv[ch][label]
            lines.append(f"{seqpos} {ch} PIKAA {m}")
        (out / f"{vid}.resfile").write_text("\n".join(lines) + "\n")
        rows.append(f"{vid}\t{out / (vid + '.resfile')}")
    Path(REPO / args.list_out).write_text("\n".join(rows) + "\n")
    print(f"wrote {len(rows)} resfiles + list {args.list_out}")


if __name__ == "__main__":
    main()
