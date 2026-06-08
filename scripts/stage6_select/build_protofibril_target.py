#!/usr/bin/env python
"""Stage 6 / S2-3 option A — build a protofibril-target complex by grafting the WT Fv pose
onto the real 9CO4 protofibril, and test epitope ACCESSIBILITY.

Method: superpose the Stage-2 WT co-fold (Fv + bound Aβ1-16, chain P) onto a central 9CO4
chain by aligning the OVERLAPPING ordered epitope residues (Aβ 9-16) — the part resolved in
both. This carries the Fv into its binding orientation relative to the rigid, stacked
protofibril core (9CO4 res 9-42), with the bound Aβ1-16 providing the flexible N-terminus (1-8)
in its engaged conformation. Then measure:
  - Fv–epitope contacts (sanity: binding pose preserved),
  - Fv vs protofibril-core CLASHES (the accessibility test: does engaging the protruding
    N-terminus force the Fv into the fibril core? low clash = epitope accessible = B3-consistent).
Writes the assembled complex PDB + a metrics JSON. Run in lecam (biotite).
"""
import argparse, json
from pathlib import Path
import numpy as np
import biotite.structure as struc
import biotite.structure.io.pdb as pdb
import biotite.structure.io.pdbx as pdbx

REPO = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fv-complex", default=str(REPO / "data/interim/flexddg/wt_complex.pdb"))
    ap.add_argument("--protofibril-cif", default=str(REPO / "data/raw/antigen/coords/9co4.cif"))
    ap.add_argument("--align-res", default="9-16", help="overlapping epitope residues to superpose on")
    ap.add_argument("--clash-A", type=float, default=2.5)
    ap.add_argument("--contact-A", type=float, default=4.5)
    ap.add_argument("--out", default=str(REPO / "results/stage6/protofibril_model"))
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.align_res.split("-"))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    # load
    fv = pdb.PDBFile.read(args.fv_complex).get_structure(model=1)
    fv = fv[fv.element != "H"]
    pf = pdbx.CIFFile.read(args.protofibril_cif)
    pf = pdbx.get_structure(pf, model=1)
    pf = pf[pf.element != "H"]
    chains = sorted(set(pf.chain_id))
    central = chains[len(chains) // 2]                       # middle of the stack
    print(f"protofibril chains {chains}; central={central}")

    # matched CA for alignment: Aβ(P) 9-16 vs central chain 9-16
    def ca(arr, chain, lo, hi):
        m = (arr.chain_id == chain) & (arr.atom_name == "CA") & (arr.res_id >= lo) & (arr.res_id <= hi)
        sub = arr[m]
        order = np.argsort(sub.res_id)
        return sub[order]
    pep = ca(fv, "P", lo, hi)
    cen = ca(pf, central, lo, hi)
    assert len(pep) == len(cen) and len(pep) > 3, f"align mismatch P={len(pep)} central={len(cen)}"

    fitted_pep, transform = struc.superimpose(cen, pep)
    rmsd_align = float(struc.rmsd(cen, fitted_pep))
    fv_moved = transform.apply(fv)                            # whole Fv+P into protofibril frame

    fv_HL = fv_moved[np.isin(fv_moved.chain_id, ["H", "L"])]
    epi_P = fv_moved[fv_moved.chain_id == "P"]
    core = pf                                                 # 9CO4 stacked core (res 9-42, all chains)

    from scipy.spatial import cKDTree
    tcore = cKDTree(core.coord)
    # Fv vs epitope contacts (sanity)
    tepi = cKDTree(epi_P.coord)
    fv_epi_contacts = int(np.sum([len(x) > 0 for x in tepi.query_ball_point(fv_HL.coord, args.contact_A)]))
    # Fv vs protofibril CORE clashes + contacts (accessibility)
    fv_core_clashes = int(np.sum([len(x) > 0 for x in tcore.query_ball_point(fv_HL.coord, args.clash_A)]))
    fv_core_contacts = int(np.sum([len(x) > 0 for x in tcore.query_ball_point(fv_HL.coord, args.contact_A)]))

    # write assembled complex (Fv + bound epitope P + protofibril core, relabel core chains)
    core2 = core.copy()
    # keep chain ids; ensure no collision with H/L/P (9CO4 uses A..J)
    combined = fv_moved + core2
    pdb.PDBFile().set_structure(combined)  # placeholder to satisfy API in some versions
    f = pdb.PDBFile(); f.set_structure(combined); f.write(str(out / "wt_fv_protofibril.pdb"))

    verdict = "ACCESSIBLE (epitope engageable on protofibril)" if fv_core_clashes <= 5 \
        else ("PARTIAL/OCCLUDED — Fv clashes protofibril core; needs docking refinement" if fv_core_clashes <= 40
              else "OCCLUDED — pose incompatible with protofibril core (real docking needed)")
    res = {"step": "S2-3A_protofibril_graft", "protofibril": "9CO4", "central_chain": central,
           "align_residues": args.align_res, "align_rmsd_A": round(rmsd_align, 3),
           "fv_epitope_contact_atoms": fv_epi_contacts,
           "fv_core_clash_atoms_<%.1fA" % args.clash_A: fv_core_clashes,
           "fv_core_contact_atoms_<%.1fA" % args.contact_A: fv_core_contacts,
           "verdict": verdict,
           "note": "Graft via overlapping ordered epitope (9-16); bound Aβ1-16 supplies the flexible "
                   "N-term in engaged conformation. Low core-clash = epitope accessible on the rigid "
                   "stacked core (B3). Next: refine + Rosetta interface score; repeat vs 8QN7 (CAA, "
                   "fixed-N) which should occlude (B4)."}
    (out / "protofibril_graft_metrics.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print("PROTOFIBRIL_BUILD_DONE ->", out)


if __name__ == "__main__":
    main()
