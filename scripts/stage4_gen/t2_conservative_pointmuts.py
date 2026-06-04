#!/usr/bin/env python
"""Stage 4 — T2 (CONSERVATIVE): ProteinMPNN conditional-probability CDR point mutations.

Instead of aggressive full-CDR sampling (which rewrote ~55% of CDRs — see T2_FINDING.md),
use ProteinMPNN --conditional_probs_only on the WT Fv–Aβ complex to get, per CDR position,
log p(aa | rest-of-seq WT + backbone + bound Aβ). Propose single CDR mutations where the
model prefers a non-WT residue (log-odds = log_p[mut]-log_p[wt] >= threshold), plus a few
low-edit combos of the top singles (cap). CDR-conditioned, conservative, paratope-respecting;
selectivity counter-screen still mandatory (Stage 6).

Run (mpnn env): env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib \
   conda run -n mpnn python scripts/stage4_gen/t2_conservative_pointmuts.py --run-id t2c-YYYYMMDD
"""
import argparse, csv, itertools, json, subprocess
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
MPNN = Path("/global/project/hpcg6049/protein/ProteinMPNN")
NUM = REPO / "data/interim/fv_numbering"
PRIOR = REPO / "results/stage4/t2-20260604/mpnn"   # reuse parsed/assigned/fixed jsonls
ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"
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
        i = seq.find(sub); p += list(range(i + 1, i + 1 + len(sub)))
    return sorted(p)


def imgt_map(tsv):
    out = {}
    for k, ln in enumerate(Path(tsv).read_text().splitlines()[1:], 1):
        c = ln.split("\t"); out[k] = f"{c[0]}{c[1] if len(c)>1 else ''}".strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--logodds", type=float, default=1.0)
    ap.add_argument("--max-combo", type=int, default=3, help="max edits in a combo variant (<=cap)")
    ap.add_argument("--panel-cap", type=int, default=30)
    args = ap.parse_args()

    VH, VL = read_fv()
    cdrH, cdrL = cdr_pos(VH, "H"), cdr_pos(VL, "L")
    imgt = {"H": imgt_map(NUM / "VH_imgt.tsv"), "L": imgt_map(NUM / "VL_imgt.tsv")}
    out = REPO / "results/stage4" / args.run_id
    cpo = out / "mpnn"; cpo.mkdir(parents=True, exist_ok=True)

    subprocess.run(["python", str(MPNN / "protein_mpnn_run.py"),
                    "--jsonl_path", str(PRIOR / "parsed.jsonl"),
                    "--chain_id_jsonl", str(PRIOR / "assigned.jsonl"),
                    "--fixed_positions_jsonl", str(PRIOR / "fixed.jsonl"),
                    "--out_folder", str(cpo), "--conditional_probs_only", "1",
                    "--seed", "37", "--batch_size", "1", "--num_seq_per_target", "1"],
                   check=True, cwd=str(MPNN))
    npz = np.load(cpo / "conditional_probs_only" / "wt_complex.npz")
    log_p = npz["log_p"]                      # (N, L, 21)
    log_p = log_p.mean(axis=0)                # average over passes -> (L,21)
    S = npz["S"]                              # WT sequence indices (L,)

    def gidx(ch, i): return (i - 1) if ch == "H" else 124 + (i - 1)
    aa_i = {a: k for k, a in enumerate(ALPHABET)}
    singles = []
    for ch, cdr, seq in (("H", cdrH, VH), ("L", cdrL, VL)):
        for i in cdr:
            g = gidx(ch, i); wt = seq[i - 1]
            assert ALPHABET[S[g]] == wt, f"seq mismatch {ch}{i}: {ALPHABET[S[g]]} vs {wt}"
            row = log_p[g]
            cand = [(ALPHABET[a], float(row[a] - row[aa_i[wt]])) for a in range(20) if ALPHABET[a] != wt]
            aa, lo = max(cand, key=lambda x: x[1])
            if lo >= args.logodds:
                singles.append({"ch": ch, "pos": i, "wt": wt, "mut": aa, "lo": round(lo, 3)})
    singles.sort(key=lambda x: -x["lo"])

    # build variant set: all singles + combos (<=max_combo) of the top singles at distinct positions
    variants = [[s] for s in singles]
    top = singles[: min(6, len(singles))]
    for k in range(2, args.max_combo + 1):
        for combo in itertools.combinations(top, k):
            variants.append(list(combo))
    # dedup by mutation set, prefer fewer edits then higher summed log-odds
    seen, uniq = set(), []
    for v in sorted(variants, key=lambda v: (len(v), -sum(m["lo"] for m in v))):
        key = tuple(sorted((m["ch"], m["pos"], m["mut"]) for m in v))
        if key in seen: continue
        seen.add(key); uniq.append(v)
    uniq = uniq[: args.panel_cap]

    rows, fasta = [], []
    for k, v in enumerate(uniq, 1):
        vid = f"LEC-AM-T2-{k:04d}"
        muts = sorted(v, key=lambda m: (m["ch"], m["pos"]))
        chs = sorted(set("HC" if m["ch"] == "H" else "LC" for m in muts))
        mutstr = ";".join(f"{'HC' if m['ch']=='H' else 'LC'}:{m['wt']}{imgt[m['ch']][m['pos']]}{m['mut']}" for m in muts)
        dH, dL = list(VH), list(VL)
        for m in muts:
            (dH if m["ch"] == "H" else dL)[m["pos"] - 1] = m["mut"]
        src = json.dumps({"method": "ProteinMPNN conditional-probs CDR point-muts (Fv-Aβ complex)",
                          "logodds": [m["lo"] for m in muts], "logodds_threshold": args.logodds,
                          "run_id": args.run_id, "pose": "cofold-wt-Abeta1-16-11544623 seed2/model_3",
                          "caveat": "pose=hypothesis; selectivity counter-screen mandatory (guardrail 1)"})
        rows.append({"variant_id": vid, "parent": "lecanemab_WT", "track": "T2",
                     "chain": "both" if len(chs) > 1 else chs[0], "mutations": mutstr,
                     "n_mut": len(muts), "edit_dist_to_wt": len(muts),
                     "status": "generated", "source_config": src})
        fasta.append(f">{vid} {mutstr} n_mut={len(muts)}\n{''.join(dH)}:{''.join(dL)}")

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
        {"stage": 4, "track": "T2", "subtrack": "conservative_point_mutations", "run_id": args.run_id,
         "tool": "ProteinMPNN --conditional_probs_only (vanilla)", "mpnn_repo": str(MPNN),
         "logodds_threshold": args.logodds, "max_combo": args.max_combo, "panel_cap": args.panel_cap,
         "n_singles": len(singles), "n_registered": len(rows), "git_commit": commit,
         "outputs": ["t2_variants.csv", "t2_variants.fasta"]}, indent=2))
    print(f"T2-conservative: {len(singles)} single-mut candidates (lo>={args.logodds}); registered {len(rows)} (singles+combos<= {args.max_combo})")
    for s in singles[:12]:
        print(f"  {('HC' if s['ch']=='H' else 'LC')}:{s['wt']}{imgt[s['ch']][s['pos']]}{s['mut']}  lo={s['lo']}")
    print("T2C_GEN_DONE ->", out)


if __name__ == "__main__":
    main()
