#!/usr/bin/env python
"""Stage 6 / S2-3A — local-dock the Fv onto a fibril N-terminal epitope (rigid receptor).

Two modes:
  --mode seed : geometrically place the Fv just outside the epitope with the paratope facing it
                (clash-free start — what the rigid graft failed to achieve). Writes a seed PDB +
                clash report. (numpy/biotite; run in lecam.)
  --mode dock : PyRosetta local docking from the seed (receptor rigid) + InterfaceAnalyzer score.
                (run in lecam-rosetta with LD_LIBRARY_PATH=$CONDA_PREFIX/lib.)

Receptor = N central chains of a fibril cif (res range kept). Epitope = central chain N-terminal
residues. Paratope = Fv CDR residues (located by sequence). Used for the 9CO4 target (should dock
clash-free / favourably) AND the 8QN7 CAA counter (N-term ordered/packed -> should be occluded).
"""
import argparse, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
VH = "EVQLVESGGGLVQPGGSLRLSCSASGFTFSSFGMHWVRQAPGKGLEWVAYISSGSSTIYYGDTVKGRFTISRDNAKNSLFLQMSSLRAEDTAVYYCAREGGYYYGRSYYTMDYWGQGTTVTVSS"
VL = "DVVMTQSPLSLPVTPGAPASISCRSSQSIVHSNGNTYLEWYLQKPGQSPKLLIYKVSNRFSGVPDRFSGSGSGTDFTLRISRVEAEDVGIYYCFQGSHVPPTFGPGTKLEIK"
CDRS = {"H": ["GFTFSSFG", "ISSGSSTI", "AREGGYYYGRSYYTMDY"], "L": ["QSIVHSNGNTY", "KVS", "FQGSHVPPT"]}


def rot_align(a, b):
    """rotation matrix aligning unit vector a onto unit vector b (Rodrigues)."""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-8:
        return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


def cdr_positions(seq, ch):
    p = []
    for sub in CDRS[ch]:
        i = seq.find(sub); p += list(range(i + 1, i + 1 + len(sub)))
    return set(p)


def seed(args):
    import biotite.structure as struc
    import biotite.structure.io.pdb as pdb
    import biotite.structure.io.pdbx as pdbx
    from scipy.spatial import cKDTree
    # receptor (fibril chains)
    rec = pdbx.get_structure(pdbx.CIFFile.read(args.receptor_cif), model=1)
    rec = rec[rec.element != "H"]
    chains = args.receptor_chains.split()
    rec = rec[np.isin(rec.chain_id, chains)]
    central = chains[len(chains) // 2]
    lo, hi = (int(x) for x in args.epitope_res.split("-"))
    epi = rec[(rec.chain_id == central) & (rec.res_id >= lo) & (rec.res_id <= hi)]
    epi_cen = epi[epi.atom_name == "CA"].coord.mean(0)
    core_cen = rec[rec.atom_name == "CA"].coord.mean(0)
    outward = epi_cen - core_cen; outward /= np.linalg.norm(outward)

    # Fv (drop antigen chain P if present)
    fv = pdb.PDBFile.read(args.fv_pdb).get_structure(model=1)
    fv = fv[(fv.element != "H") & np.isin(fv.chain_id, ["H", "L"])]
    parH = cdr_positions(VH, "H"); parL = cdr_positions(VL, "L")
    pmask = ((fv.chain_id == "H") & np.isin(fv.res_id, list(parH))) | \
            ((fv.chain_id == "L") & np.isin(fv.res_id, list(parL)))
    par = fv[pmask & (fv.atom_name == "CA")]
    fv_cen = fv[fv.atom_name == "CA"].coord.mean(0)
    par_cen = par.coord.mean(0)

    # rotate so paratope faces epitope (paratope vector -> -outward), then place paratope d out
    R = rot_align(par_cen - fv_cen, -outward)
    coords = (R @ (fv.coord - fv_cen).T).T + fv_cen
    par_cen_new = R @ (par_cen - fv_cen) + fv_cen
    target = epi_cen + outward * args.standoff
    coords += (target - par_cen_new)
    fv2 = fv.copy(); fv2.coord = coords

    clashes = int(np.sum([len(x) > 0 for x in cKDTree(rec.coord).query_ball_point(fv2.coord, 2.5)]))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    combined = fv2 + rec
    f = pdb.PDBFile(); f.set_structure(combined); f.write(str(out / "seed.pdb"))
    rep = {"mode": "seed", "receptor": Path(args.receptor_cif).stem, "chains": chains,
           "central": central, "epitope_res": args.epitope_res, "standoff_A": args.standoff,
           "fv_receptor_clashes_<2.5A": clashes,
           "ok": clashes <= 5, "note": "clash-free seed ready for local docking" if clashes <= 5
           else "seed still clashes — increase standoff or pick a more exposed epitope face"}
    (out / "seed_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2)); print("SEED_DONE")


def dock(args):
    import pyrosetta
    from pyrosetta import pose_from_pdb
    pyrosetta.init("-mute all -ignore_unrecognized_res -ignore_zero_occupancy false -ex1 -ex2")
    out = Path(args.out)
    pose = pose_from_pdb(str(out / "seed.pdb"))
    # partners: receptor chains _ Fv chains (Fv = H,L moved as one rigid body)
    rec_ch = "".join(args.receptor_chains.split())
    partners = f"{rec_ch}_HL"
    from pyrosetta.rosetta.protocols.docking import setup_foldtree, DockMCMProtocol
    scorefxn = pyrosetta.create_score_function("ref2015")
    from pyrosetta.rosetta.protocols.docking import DockingSlideIntoContact
    from pyrosetta.rosetta.protocols.analysis import InterfaceAnalyzerMover
    setup_foldtree(pose, partners, pyrosetta.rosetta.utility.vector1_int(1))
    DockingSlideIntoContact(1).apply(pose)
    best = None
    for i in range(args.ndecoys):
        p = pose.clone()
        dock = DockMCMProtocol(); dock.set_scorefxn(scorefxn)
        dock.apply(p)
        ia = InterfaceAnalyzerMover(partners); ia.set_compute_packstat(False)
        ia.apply(p)
        data = ia.get_all_data()
        dG = ia.get_interface_dG(); nres = ia.get_num_interface_residues(); sasa = ia.get_interface_delta_sasa()
        rec_i = {"decoy": i, "dG_separated": round(dG, 2), "n_interface_res": int(nres),
                 "interface_dSASA": round(sasa, 1)}
        if best is None or dG < best["dG_separated"]:
            best = rec_i; p.dump_pdb(str(out / "best_dock.pdb"))
        print("decoy", i, "dG", round(dG, 2), "nres", int(nres))
    (out / "dock_report.json").write_text(json.dumps(
        {"mode": "dock", "partners": partners, "ndecoys": args.ndecoys, "best": best,
         "note": "dG_separated = Rosetta interface binding energy (REU, more negative=stronger). "
                 "Compare 9CO4 target vs 8QN7 CAA counter (B3 vs B4) and vs WT before scoring variants."}, indent=2))
    print("BEST", json.dumps(best)); print("DOCK_DONE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["seed", "dock"], required=True)
    ap.add_argument("--receptor-cif", required=True)
    ap.add_argument("--receptor-chains", default="E F G")
    ap.add_argument("--epitope-res", default="9-16")
    ap.add_argument("--fv-pdb", default=str(REPO / "data/interim/flexddg/wt_complex.pdb"))
    ap.add_argument("--standoff", type=float, default=12.0)
    ap.add_argument("--ndecoys", type=int, default=10)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    (seed if args.mode == "seed" else dock)(args)


if __name__ == "__main__":
    main()
