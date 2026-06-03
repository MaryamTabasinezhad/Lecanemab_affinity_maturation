#!/usr/bin/env python
"""Stage 2.4 — pose clustering + epitope-register analysis (the Stage-2 gate, OQ-1).

For the 25 Boltz-2 co-fold poses (WT Fv + Aβ1-16):
  - per-pose Aβ residue -> Fv heavy-atom contacts (<4.5 A) => epitope footprint,
  - paratope Fv residues mapped to CDRs,
  - cluster poses by Aβ-peptide CA RMSD (Fv-superposed) => pose families,
  - compare consensus footprint to B6 hotspots {Y10,E11,H13,H14,Q15,K16} and the
    literature "N-terminal, tolerant 3-7" register; emit a gate verdict.
Writes pose_hypotheses.json (+ manifest) to --repo-out. Pose stays a HYPOTHESIS (D-002).

Run (lecam, force env lib for compiled biotite/scipy):
  env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib conda run -n lecam \
    python scripts/stage2_model/analyze_poses.py --scratch-dir <run> --repo-out <run>
"""
import argparse, glob, json, subprocess
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import biotite.structure as struc
import biotite.structure.io.pdb as pdb

REPO = Path(__file__).resolve().parents[2]
ABETA = "DAEFRHDSGYEVHHQK"                 # Aβ1-16 (P chain)
VH = "EVQLVESGGGLVQPGGSLRLSCSASGFTFSSFGMHWVRQAPGKGLEWVAYISSGSSTIYYGDTVKGRFTISRDNAKNSLFLQMSSLRAEDTAVYYCAREGGYYYGRSYYTMDYWGQGTTVTVSS"
VL = "DVVMTQSPLSLPVTPGAPASISCRSSQSIVHSNGNTYLEWYLQKPGQSPKLLIYKVSNRFSGVPDRFSGSGSGTDFTLRISRVEAEDVGIYYCFQGSHVPPTFGPGTKLEIK"
CDRS = {  # IMGT loop sequences -> located by substring (1-based sequential resid in the PDB chain)
    "H1": ("H", "GFTFSSFG"), "H2": ("H", "ISSGSSTI"), "H3": ("H", "AREGGYYYGRSYYTMDY"),
    "L1": ("L", "QSIVHSNGNTY"), "L2": ("L", "KVS"), "L3": ("L", "FQGSHVPPT"),
}
B6_HOTSPOTS = [10, 11, 13, 14, 15, 16]
CONTACT_A = 4.5


def cdr_ranges():
    out = {}
    for name, (ch, seq) in CDRS.items():
        s = VH if ch == "H" else VL
        i = s.find(seq)
        out[name] = (ch, set(range(i + 1, i + 1 + len(seq)))) if i >= 0 else (ch, set())
    return out


def load_pose(path):
    arr = pdb.PDBFile.read(path).get_structure(model=1)
    return arr[arr.element != "H"]            # heavy atoms only


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch-dir", required=True)
    ap.add_argument("--repo-out", required=True)
    args = ap.parse_args()

    files = sorted(glob.glob(f"{args.scratch_dir}/seed_*/**/*_model_*.pdb", recursive=True))
    assert files, "no pose PDBs found"
    cdr = cdr_ranges()

    n_ab = len(ABETA)
    contact_freq = np.zeros(n_ab)                 # per Aβ position: fraction of poses contacting Fv
    contact_vecs = []                             # per-pose binary contact vector (for clustering/Jaccard)
    fv_contact_count = {}                         # (chain,resid) -> #poses contacted
    ab_ca_frames = []                             # Aβ CA coords in pose0 Fv frame
    ref_fv_ca = None

    for k, f in enumerate(files):
        arr = load_pose(f)
        fv = arr[np.isin(arr.chain_id, ["H", "L"])]
        ab = arr[arr.chain_id == "P"]
        tree = cKDTree(fv.coord)
        vec = np.zeros(n_ab)
        pose_fv = set()                            # unique Fv residues contacted in THIS pose
        for res in np.unique(ab.res_id):
            ratoms = ab[ab.res_id == res]
            d, idx = tree.query(ratoms.coord, k=1)
            if d.min() <= CONTACT_A:
                vec[res - 1] = 1
                for lst in tree.query_ball_point(ratoms.coord, CONTACT_A):
                    for ai in lst:
                        pose_fv.add((str(fv.chain_id[ai]), int(fv.res_id[ai])))
        for key in pose_fv:                        # count once per pose -> true fraction
            fv_contact_count[key] = fv_contact_count.get(key, 0) + 1 / len(files)
        contact_vecs.append(vec)
        contact_freq += vec / len(files)

        # superpose this pose's Fv CA onto pose0, carry Aβ CA into the common frame
        ca = arr[arr.atom_name == "CA"]
        fv_ca = ca[np.isin(ca.chain_id, ["H", "L"])]
        ab_ca = ca[ca.chain_id == "P"]
        if ref_fv_ca is None:
            ref_fv_ca = fv_ca
            ab_ca_frames.append(ab_ca.coord.copy())
        else:
            _, transform = struc.superimpose(ref_fv_ca, fv_ca)
            ab_ca_frames.append(transform.apply(ab_ca).coord)

    contact_vecs = np.array(contact_vecs)
    ab_ca_frames = np.array(ab_ca_frames)         # (n_pose, 16, 3)

    # pairwise Aβ CA RMSD (Fv-superposed) -> cluster
    n = len(files)
    dmat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            r = np.sqrt(((ab_ca_frames[i] - ab_ca_frames[j]) ** 2).sum(axis=1).mean())
            dmat[i, j] = dmat[j, i] = r
    Z = linkage(squareform(dmat), method="average")
    labels = fcluster(Z, t=3.0, criterion="distance")    # 3 A Aβ-CA RMSD cluster cutoff
    sizes = {int(c): int((labels == c).sum()) for c in np.unique(labels)}
    largest = max(sizes.values())

    # self-consistency: mean pairwise Jaccard of contact footprints
    jac = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = contact_vecs[i].astype(bool), contact_vecs[j].astype(bool)
            u = (a | b).sum()
            jac.append((a & b).sum() / u if u else 1.0)

    consensus = [i + 1 for i in range(n_ab) if contact_freq[i] >= 0.5]
    paratope = sorted([{"chain": c, "resid": r,
                        "cdr": next((nm for nm, (cc, rs) in cdr.items() if cc == c and r in rs), "FR"),
                        "freq": round(v, 3)}
                       for (c, r), v in fv_contact_count.items() if v >= 0.5],
                      key=lambda x: -x["freq"])

    result = {
        "stage": 2, "step": "2.4_pose_cluster_epitope_register", "n_poses": n,
        "epitope_footprint_freq": {str(i + 1): round(float(contact_freq[i]), 3) for i in range(n_ab)},
        "consensus_epitope_positions_ge50pct": consensus,
        "consensus_epitope_residues": "".join(ABETA[i - 1] for i in consensus),
        "paratope_cdr_residues_ge50pct": paratope,
        "pose_clusters": {"n_clusters": len(sizes), "sizes": sizes,
                          "largest_fraction": round(largest / n, 3),
                          "mean_pairwise_Abeta_ca_rmsd": round(float(dmat[np.triu_indices(n, 1)].mean()), 3),
                          "cutoff_A": 3.0},
        "footprint_self_consistency_mean_jaccard": round(float(np.mean(jac)), 3),
        "register_comparison": {
            "B6_hotspots": B6_HOTSPOTS,
            "B6_hotspots_in_consensus": sorted(set(consensus) & set(B6_HOTSPOTS)),
            "lit_3to7": [3, 4, 5, 6, 7],
            "lit_3to7_in_consensus": sorted(set(consensus) & {3, 4, 5, 6, 7}),
        },
        "gate": {
            "self_consistent_pose_family": largest / n >= 0.5,
            "n_terminal_engaged_B3": bool(set(consensus) & set(range(1, 17))),
            "not_contradicting_B6": bool(set(consensus) & set(B6_HOTSPOTS)) or bool(set(consensus) & {3, 4, 5, 6, 7}),
            "note": "Pose is a hypothesis (D-002); Ab-Ag iptm overconfident (guardrail 2). "
                    "B3 flexible-N check is the MD step (2.3). Register treated as a hypothesis set (B6).",
        },
    }
    repo_out = Path(args.repo_out); repo_out.mkdir(parents=True, exist_ok=True)
    (repo_out / "pose_hypotheses.json").write_text(json.dumps(result, indent=2))
    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    (repo_out / "manifest_2.4.json").write_text(json.dumps(
        {"stage": 2, "step": "2.4_pose_analysis", "tool": "biotite+scipy (lecam)",
         "n_poses": n, "scratch_dir": args.scratch_dir, "contact_cutoff_A": CONTACT_A,
         "git_commit": commit, "outputs": ["pose_hypotheses.json"]}, indent=2))

    print("EPITOPE consensus (>=50%):", consensus, result["consensus_epitope_residues"])
    print("FOOTPRINT freq:", {k: v for k, v in result["epitope_footprint_freq"].items()})
    print("CLUSTERS:", result["pose_clusters"])
    print("self-consistency mean Jaccard:", result["footprint_self_consistency_mean_jaccard"])
    print("GATE:", result["gate"])
    print("POSE_ANALYSIS_DONE")


if __name__ == "__main__":
    main()
