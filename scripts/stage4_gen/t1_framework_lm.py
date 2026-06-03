#!/usr/bin/env python
"""Stage 4 — T1 track: framework/Vernier point mutations, CDR-PRESERVING (D-003).

OAS-derived evolutionary prior (AbLang2, paired) proposes single substitutions at
framework positions where the model prefers a residue over WT (per-position log-odds
= logit[mut]-logit[wt]; normalization-free -> guardrail 4). ALL IMGT CDRs are protected.
Vernier positions (CDR-conformation-shaping) are tagged higher-risk, not excluded.

Emits a ledger-ready CSV + per-variant FASTA + manifest to results/stage4/<run-id>/.
The ledger load (DuckDB) is a separate step (lecam env).

Run: env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib conda run -n lecam-ab \
       python scripts/stage4_gen/t1_framework_lm.py --run-id t1-YYYYMMDD [--logodds 2.0 --cap 40]
"""
import argparse, csv, json, subprocess
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
NUM = REPO / "data/interim/fv_numbering"
AAs = list("ACDEFGHIKLMNPQRSTVWY")
CDRS = {"H1": ("H", "GFTFSSFG"), "H2": ("H", "ISSGSSTI"), "H3": ("H", "AREGGYYYGRSYYTMDY"),
        "L1": ("L", "QSIVHSNGNTY"), "L2": ("L", "KVS"), "L3": ("L", "FQGSHVPPT")}
# Vernier-zone Kabat positions (Stage-1 docs/sources/fv_cdr_vernier_map.md)
VERNIER_KABAT = {"H": {2, 27, 28, 29, 30, 47, 48, 49, 67, 69, 71, 73, 78, 93, 94},
                 "L": {2, 4, 35, 36, 46, 47, 48, 49, 64, 66, 68, 69, 71}}


def read_fv():
    s, name = {}, None
    for ln in (REPO / "data/raw/lecanemab_fv.fasta").read_text().splitlines():
        if ln.startswith(">"):
            name = "H" if "VH" in ln else ("L" if "VL" in ln else None)
        elif name:
            s[name] = s.get(name, "") + ln.strip()
    return s["H"], s["L"]


def read_num(tsv):
    rows = []
    for ln in Path(tsv).read_text().splitlines()[1:]:
        p = ln.split("\t")
        rows.append((p[0], p[1] if len(p) > 1 else "", p[2] if len(p) > 2 else ""))
    return rows  # in sequence order: (pos, ins, aa)


def cdr_positions(seq, ch):
    s = set()
    for nm, (c, sub) in CDRS.items():
        if c != ch:
            continue
        i = seq.find(sub)
        if i >= 0:
            s |= set(range(i + 1, i + 1 + len(sub)))   # 1-based seq positions
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--logodds", type=float, default=2.0)
    ap.add_argument("--cap", type=int, default=40)
    args = ap.parse_args()

    VH, VL = read_fv()
    seqs = {"H": VH, "L": VL}
    imgt = {"H": read_num(NUM / "VH_imgt.tsv"), "L": read_num(NUM / "VL_imgt.tsv")}
    kab = {"H": read_num(NUM / "VH_kabat.tsv"), "L": read_num(NUM / "VL_kabat.tsv")}
    cdr = {ch: cdr_positions(seqs[ch], ch) for ch in "HL"}

    import ablang2
    m = ablang2.pretrained()
    a2t = m.tokenizer.aa_to_token
    L = np.asarray(m([(VH, VL)], mode="likelihood"))[0]   # (241,26) logits

    def tokidx(ch, i):                 # 1-based residue -> token index
        return i if ch == "H" else 127 + i

    cand = []
    for ch in "HL":
        seq = seqs[ch]
        for i in range(1, len(seq) + 1):
            if i in cdr[ch]:
                continue                                   # CDR protected
            wt = seq[i - 1]
            tok = tokidx(ch, i)
            wt_lg = L[tok, a2t[wt]]
            los = [(aa, float(L[tok, a2t[aa]] - wt_lg)) for aa in AAs if aa != wt]
            aa, lo = max(los, key=lambda x: x[1])
            if lo < args.logodds:
                continue
            kpos = kab[ch][i - 1][0]
            ipos, iins, iaa = imgt[ch][i - 1]
            assert iaa == wt, f"IMGT/seq mismatch {ch}{i}: {iaa} vs {wt}"
            vernier = int(kpos) in VERNIER_KABAT[ch] if kpos.isdigit() else False
            mutseq = dict(seqs); mutseq[ch] = seq[:i - 1] + aa + seq[i:]
            cand.append({
                "chain": "HC" if ch == "H" else "LC", "ch": ch, "seq_pos": i,
                "imgt": f"{ipos}{iins}".strip(), "wt": wt, "mut": aa,
                "logodds": round(lo, 3), "region": "vernier" if vernier else "framework",
                "VH": mutseq["H"], "VL": mutseq["L"],
            })

    cand.sort(key=lambda c: -c["logodds"])
    cand = cand[: args.cap]

    out = REPO / "results/stage4" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    # ledger-ready CSV (subset of variants schema)
    rows = []
    for k, c in enumerate(cand, 1):
        vid = f"LEC-AM-T1-{k:04d}"
        mut = f"{c['chain']}:{c['wt']}{c['imgt']}{c['mut']}"
        src = json.dumps({"method": "AbLang2(paired) OAS prior", "logodds": c["logodds"],
                          "region": c["region"], "seq_pos": c["seq_pos"], "run_id": args.run_id,
                          "logodds_threshold": args.logodds})
        rows.append({"variant_id": vid, "parent": "lecanemab_WT", "track": "T1",
                     "chain": c["chain"], "mutations": mut, "n_mut": 1, "edit_dist_to_wt": 1,
                     "status": "generated", "source_config": src})
    cols = ["variant_id", "parent", "track", "chain", "mutations", "n_mut",
            "edit_dist_to_wt", "status", "source_config"]
    with open(out / "t1_variants.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    # FASTA (full mutated Fv per variant)
    with open(out / "t1_variants.fasta", "w") as fh:
        for r, c in zip(rows, cand):
            fh.write(f">{r['variant_id']} {r['mutations']} logodds={c['logodds']} {c['region']}\n")
            fh.write(f"{c['VH']}:{c['VL']}\n")
    # readable detail
    (out / "t1_candidates.json").write_text(json.dumps(cand, indent=2))
    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    (out / "manifest.json").write_text(json.dumps(
        {"stage": 4, "track": "T1", "run_id": args.run_id,
         "method": "AbLang2 paired (OAS prior), CDR-preserving framework/Vernier point mutants",
         "tool": "ablang2", "logodds_threshold": args.logodds, "cap": args.cap,
         "n_candidates": len(rows), "n_vernier": sum(c["region"] == "vernier" for c in cand),
         "n_framework": sum(c["region"] == "framework" for c in cand),
         "cdr_protected": {ch: sorted(cdr[ch]) for ch in "HL"}, "git_commit": commit,
         "outputs": ["t1_variants.csv", "t1_variants.fasta", "t1_candidates.json"]}, indent=2))

    nv = sum(c["region"] == "vernier" for c in cand)
    print(f"T1 candidates: {len(rows)} (framework {len(rows)-nv}, vernier {nv})")
    for c in cand[:12]:
        print(f"  {c['chain']}:{c['wt']}{c['imgt']}{c['mut']}  lo={c['logodds']}  {c['region']}")
    print("T1_GEN_DONE ->", out)


if __name__ == "__main__":
    main()
