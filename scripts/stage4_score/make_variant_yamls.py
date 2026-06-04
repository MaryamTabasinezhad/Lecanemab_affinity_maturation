#!/usr/bin/env python
"""Write a Boltz-2 co-fold YAML per variant (VH+VL + Aβ1-16, single-seq) + an array index.
Reuses the WT Stage-2.2 setup so variant scores are comparable (deltas vs WT)."""
import argparse
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
ABETA = "DAEFRHDSGYEVHHQK"
TMPL = """# Stage 4 scoring — {vid} ({mut}) co-fold vs Aβ1-16. Same settings as WT Stage 2.2.
version: 1
sequences:
  - protein:
      id: H
      sequence: {VH}
      msa: empty
  - protein:
      id: L
      sequence: {VL}
      msa: empty
  - protein:
      id: P
      sequence: {AB}
      msa: empty
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", required=True)
    ap.add_argument("--outdir", default="configs/stage4")
    ap.add_argument("--list-name", default="variant_yaml_list.tsv")
    args = ap.parse_args()
    out = REPO / args.outdir; out.mkdir(parents=True, exist_ok=True)
    entries, vid, mut = [], None, None
    pairs = []
    for ln in Path(args.fasta).read_text().splitlines():
        if ln.startswith(">"):
            p = ln[1:].split()
            vid, mut = p[0], (p[1] if len(p) > 1 else "")
        elif ln.strip():
            vh, vl = ln.strip().split(":")
            pairs.append((vid, mut, vh, vl))
    rows = []
    for vid, mut, vh, vl in sorted(pairs):
        yml = out / f"cofold_{vid}.yaml"
        yml.write_text(TMPL.format(vid=vid, mut=mut, VH=vh, VL=vl, AB=ABETA))
        rows.append(f"{vid}\t{yml}")
    (out / args.list_name).write_text("\n".join(rows) + "\n")
    print(f"wrote {len(rows)} variant YAMLs + variant_yaml_list.tsv")
    for r in rows:
        print(" ", r)


if __name__ == "__main__":
    main()
