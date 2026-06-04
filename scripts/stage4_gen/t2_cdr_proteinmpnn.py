#!/usr/bin/env python
"""Stage 4 — T2 track: CDR redesign with ProteinMPNN (reuses ../protein/ProteinMPNN + mpnn env).

Designs the 6 IMGT CDRs on the WT Fv-Aβ complex with the Aβ peptide (P) AND all framework
FIXED (so CDRs are conditioned on the bound peptide). Parses designs, diffs vs WT at CDR
positions, registers conservative-edit variants in the ledger as T2 (mutations in IMGT).

Pose is a HYPOTHESIS (D-002) -> designs inherit pose uncertainty; selectivity counter-screen
(Stage 6) is MANDATORY for CDR variants (guardrail 1). Edit-distance cap keeps it conservative.

Run (mpnn env): env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib \
   conda run -n mpnn python scripts/stage4_gen/t2_cdr_proteinmpnn.py --run-id t2-YYYYMMDD
"""
import argparse, csv, json, os, subprocess, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MPNN = Path("/global/project/hpcg6049/protein/ProteinMPNN")
NUM = REPO / "data/interim/fv_numbering"
COMPLEX = REPO / "data/interim/flexddg/wt_complex.pdb"   # H (VH), L (VL), P (Aβ1-16)
CDRS = {"H": ["GFTFSSFG", "ISSGSSTI", "AREGGYYYGRSYYTMDY"],
        "L": ["QSIVHSNGNTY", "KVS", "FQGSHVPPT"]}


def read_fv():
    s, n = {}, None
    for ln in (REPO / "data/raw/lecanemab_fv.fasta").read_text().splitlines():
        if ln.startswith(">"): n = "H" if "VH" in ln else ("L" if "VL" in ln else None)
        elif n: s[n] = s.get(n, "") + ln.strip()
    return s["H"], s["L"]


def cdr_pos(seq, ch):
    p = []
    for sub in CDRS[ch]:
        i = seq.find(sub)
        p += list(range(i + 1, i + 1 + len(sub)))
    return sorted(p)


def imgt_map(tsv):
    out = {}
    for k, ln in enumerate(Path(tsv).read_text().splitlines()[1:], 1):
        c = ln.split("\t"); out[k] = f"{c[0]}{c[1] if len(c)>1 else ''}".strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--num-seq", type=int, default=48)
    ap.add_argument("--temps", default="0.2 0.3")
    ap.add_argument("--seed", type=int, default=37)
    ap.add_argument("--edit-cap", type=int, default=6, help="max CDR mutations vs WT to keep (conservative)")
    ap.add_argument("--panel-cap", type=int, default=30)
    args = ap.parse_args()

    VH, VL = read_fv()
    cdrH, cdrL = cdr_pos(VH, "H"), cdr_pos(VL, "L")
    imgt = {"H": imgt_map(NUM / "VH_imgt.tsv"), "L": imgt_map(NUM / "VL_imgt.tsv")}

    out = REPO / "results/stage4" / args.run_id
    mpnn_out = out / "mpnn"; mpnn_out.mkdir(parents=True, exist_ok=True)
    pdbdir = out / "pdb"; pdbdir.mkdir(exist_ok=True)
    (pdbdir / "wt_complex.pdb").write_bytes(COMPLEX.read_bytes())

    def run(cmd): subprocess.run(cmd, check=True, cwd=str(MPNN))
    py = "python"
    run([py, str(MPNN / "helper_scripts/parse_multiple_chains.py"),
         "--input_path", str(pdbdir), "--output_path", str(mpnn_out / "parsed.jsonl")])
    run([py, str(MPNN / "helper_scripts/assign_fixed_chains.py"),
         "--input_path", str(mpnn_out / "parsed.jsonl"),
         "--output_path", str(mpnn_out / "assigned.jsonl"), "--chain_list", "H L"])  # design H,L; fix P
    poslist = " ".join(str(p) for p in cdrH) + ", " + " ".join(str(p) for p in cdrL)
    run([py, str(MPNN / "helper_scripts/make_fixed_positions_dict.py"),
         "--input_path", str(mpnn_out / "parsed.jsonl"),
         "--output_path", str(mpnn_out / "fixed.jsonl"),
         "--chain_list", "H L", "--position_list", poslist, "--specify_non_fixed"])  # CDRs designable
    run([py, str(MPNN / "protein_mpnn_run.py"),
         "--jsonl_path", str(mpnn_out / "parsed.jsonl"),
         "--chain_id_jsonl", str(mpnn_out / "assigned.jsonl"),
         "--fixed_positions_jsonl", str(mpnn_out / "fixed.jsonl"),
         "--out_folder", str(mpnn_out), "--num_seq_per_target", str(args.num_seq),
         "--sampling_temp", args.temps, "--seed", str(args.seed), "--batch_size", "1"])

    fa = mpnn_out / "seqs" / "wt_complex.fa"
    lines = fa.read_text().splitlines()
    wt = {"H": VH, "L": VL}
    designs = []
    for i in range(0, len(lines), 2):
        hdr, seq = lines[i], lines[i + 1]
        chains = seq.split("/")
        if i == 0:
            continue                       # native/WT entry
        dH, dL = chains[0], chains[1]
        muts = []
        for ch, dseq, cdr in (("H", dH, cdrH), ("L", dL, cdrL)):
            for pos in cdr:
                w, m = wt[ch][pos - 1], dseq[pos - 1]
                if m != w:
                    muts.append((ch, pos, w, m))
        if not muts or len(muts) > args.edit_cap:
            continue
        key = tuple(sorted(muts))
        designs.append((key, muts, dH, dL))

    # dedup, sort by fewest mutations (conservative first), cap
    seen, uniq = set(), []
    for key, muts, dH, dL in sorted(designs, key=lambda x: len(x[1])):
        if key in seen: continue
        seen.add(key); uniq.append((muts, dH, dL))
    uniq = uniq[: args.panel_cap]

    rows, fasta = [], []
    for k, (muts, dH, dL) in enumerate(uniq, 1):
        vid = f"LEC-AM-T2-{k:04d}"
        chs = sorted(set("HC" if c == "H" else "LC" for c, _, _, _ in muts))
        mutstr = ";".join(f"{'HC' if c=='H' else 'LC'}:{w}{imgt[c][p]}{m}" for c, p, w, m in muts)
        src = json.dumps({"method": "ProteinMPNN vanilla CDR redesign (Fv-Aβ complex, framework+P fixed)",
                          "n_cdr_mut": len(muts), "run_id": args.run_id, "temps": args.temps,
                          "pose": "results/stage2/cofold-wt-Abeta1-16-11544623 seed2/model_3",
                          "caveat": "pose=hypothesis; selectivity counter-screen mandatory (guardrail 1)"})
        rows.append({"variant_id": vid, "parent": "lecanemab_WT", "track": "T2",
                     "chain": "both" if len(chs) > 1 else chs[0], "mutations": mutstr,
                     "n_mut": len(muts), "edit_dist_to_wt": len(muts),
                     "status": "generated", "source_config": src})
        fasta.append(f">{vid} {mutstr} n_mut={len(muts)}\n{dH}:{dL}")

    cols = ["variant_id", "parent", "track", "chain", "mutations", "n_mut",
            "edit_dist_to_wt", "status", "source_config"]
    with open(out / "t2_variants.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    (out / "t2_variants.fasta").write_text("\n".join(fasta) + "\n")
    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    (out / "manifest.json").write_text(json.dumps(
        {"stage": 4, "track": "T2", "run_id": args.run_id, "tool": "ProteinMPNN (vanilla)",
         "mpnn_repo": str(MPNN), "designed": "6 IMGT CDRs on Fv-Aβ complex; framework+P fixed",
         "num_seq": args.num_seq, "temps": args.temps, "seed": args.seed,
         "edit_cap": args.edit_cap, "panel_cap": args.panel_cap, "n_registered": len(rows),
         "cdr_positions": {"H": cdrH, "L": cdrL}, "git_commit": commit,
         "outputs": ["t2_variants.csv", "t2_variants.fasta", "mpnn/seqs/wt_complex.fa"]}, indent=2))
    from collections import Counter
    dist = Counter(r["n_mut"] for r in rows)
    print(f"T2 registered {len(rows)} CDR variants (edit-dist cap {args.edit_cap}); n_mut dist:", dict(sorted(dist.items())))
    for r in rows[:8]:
        print(f"  {r['variant_id']}  {r['mutations']}")
    print("T2_GEN_DONE ->", out)


if __name__ == "__main__":
    main()
