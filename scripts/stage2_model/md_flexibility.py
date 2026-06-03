#!/usr/bin/env python
"""Stage 2.3 — short MD ensemble to test the B3 'flexible Aβ N-terminus' hypothesis.

Seeds from the best-ipSAE WT co-fold pose; implicit-solvent (GBn2, amber14) Langevin MD
at 300 K with WEAK position restraints on the Fv FRAMEWORK CA only (CDR loops + the Aβ
peptide left free) so the binding frame is stable while the epitope/paratope sample.
Reports per-residue Aβ RMSF + DSSP coil fraction (N-term vs core vs C-term) and CDR-H3
RMSF. B3 = engaged Aβ N-terminus remains flexible/unstructured (vs fixed-N counter-targets).

Run on A100 (CUDA) or CPU fallback:
  env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib conda run -n lecam-md \
    python scripts/stage2_model/md_flexibility.py --pdb <pose.pdb> --repo-out <dir> --ns 5
"""
import argparse, json, subprocess
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
VH = "EVQLVESGGGLVQPGGSLRLSCSASGFTFSSFGMHWVRQAPGKGLEWVAYISSGSSTIYYGDTVKGRFTISRDNAKNSLFLQMSSLRAEDTAVYYCAREGGYYYGRSYYTMDYWGQGTTVTVSS"
VL = "DVVMTQSPLSLPVTPGAPASISCRSSQSIVHSNGNTYLEWYLQKPGQSPKLLIYKVSNRFSGVPDRFSGSGSGTDFTLRISRVEAEDVGIYYCFQGSHVPPTFGPGTKLEIK"
CDRS = {"H1": ("H", "GFTFSSFG"), "H2": ("H", "ISSGSSTI"), "H3": ("H", "AREGGYYYGRSYYTMDY"),
        "L1": ("L", "QSIVHSNGNTY"), "L2": ("L", "KVS"), "L3": ("L", "FQGSHVPPT")}


def cdr_resids():
    out = {}
    for nm, (ch, seq) in CDRS.items():
        s = VH if ch == "H" else VL
        i = s.find(seq)
        out[nm] = (ch, set(range(i + 1, i + 1 + len(seq))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdb", required=True)
    ap.add_argument("--repo-out", required=True)
    ap.add_argument("--ns", type=float, default=5.0)
    ap.add_argument("--report-ps", type=float, default=10.0)
    args = ap.parse_args()

    import openmm as mm
    import openmm.app as app
    from openmm import unit
    from pdbfixer import PDBFixer
    import mdtraj as md

    out = Path(args.repo_out); out.mkdir(parents=True, exist_ok=True)
    scratch_pref = out  # trajectory written here (caller points repo-out at scratch run dir)

    # ---- prep: fix + protonate ----
    fixer = PDBFixer(filename=args.pdb)
    fixer.findMissingResidues(); fixer.findMissingAtoms(); fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    ff = app.ForceField("amber14-all.xml", "implicit/gbn2.xml")
    modeller = app.Modeller(fixer.topology, fixer.positions)
    system = ff.createSystem(modeller.topology, nonbondedMethod=app.CutoffNonPeriodic,
                             nonbondedCutoff=2.0 * unit.nanometer, constraints=app.HBonds)

    # ---- weak CA restraints on Fv FRAMEWORK only (chains H/L, non-CDR) ----
    cdr = cdr_resids()
    cdr_by_chain = {"H": set().union(*[rs for (c, rs) in cdr.values() if c == "H"]),
                    "L": set().union(*[rs for (c, rs) in cdr.values() if c == "L"])}
    restraint = mm.CustomExternalForce("0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)")
    restraint.addGlobalParameter("k", 2.0 * unit.kilocalories_per_mole / unit.angstrom**2)
    for p in ("x0", "y0", "z0"):
        restraint.addPerParticleParameter(p)
    pos = modeller.positions
    n_restr = 0
    for atom in modeller.topology.atoms():
        if atom.name == "CA":
            ch = atom.residue.chain.id
            rid = atom.residue.id
            try:
                rid_i = int(rid)
            except ValueError:
                rid_i = -1
            if ch in ("H", "L") and rid_i not in cdr_by_chain.get(ch, set()):
                x = pos[atom.index]
                restraint.addParticle(atom.index, [x.x, x.y, x.z])
                n_restr += 1
    system.addForce(restraint)

    integrator = mm.LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 0.002 * unit.picoseconds)
    try:
        platform = mm.Platform.getPlatformByName("CUDA")
        plat_name = "CUDA"
    except Exception:
        platform = mm.Platform.getPlatformByName("CPU")
        plat_name = "CPU"
    sim = app.Simulation(modeller.topology, system, integrator, platform)
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy()
    sim.context.setVelocitiesToTemperature(300 * unit.kelvin)
    sim.step(50000)  # 100 ps equilibration

    steps = int(args.ns * 1000 / 0.002)            # ns -> 2fs steps
    report_every = int(args.report_ps * 1000 / 2)  # report-ps -> steps
    traj_dcd = str(scratch_pref / "md_traj.dcd")
    sim.reporters.append(app.DCDReporter(traj_dcd, report_every))
    sim.reporters.append(app.StateDataReporter(str(scratch_pref / "md.log"), report_every,
                         step=True, potentialEnergy=True, temperature=True))
    top_pdb = str(scratch_pref / "md_top.pdb")
    with open(top_pdb, "w") as fh:
        app.PDBFile.writeFile(modeller.topology, modeller.positions, fh)
    sim.step(steps)

    # ---- analysis (mdtraj) ----
    t = md.load(traj_dcd, top=top_pdb)
    fv_ca = t.topology.select("(chainid 0 or chainid 1) and name CA")
    t.superpose(t, 0, atom_indices=fv_ca)
    # chain index: H=0, L=1, P=2 (order in the Boltz pdb)
    rmsf = md.rmsf(t, t, 0, atom_indices=None)  # per-atom
    ab_ca = t.topology.select("chainid 2 and name CA")
    ab_resid = [t.topology.atom(i).residue.resSeq for i in ab_ca]
    ab_rmsf = {int(r): round(float(rmsf[i] * 10), 3) for r, i in zip(ab_resid, ab_ca)}  # nm->A
    # DSSP -> coil fraction per Aβ residue
    dssp = md.compute_dssp(t, simplified=True)  # (frames, residues) 'H','E','C'
    ab_res_idx = [t.topology.atom(i).residue.index for i in ab_ca]
    coil_frac = {int(r): round(float((dssp[:, idx] == "C").mean()), 3)
                 for r, idx in zip(ab_resid, ab_res_idx)}

    def mean_rmsf(rng): return round(float(np.mean([ab_rmsf[r] for r in rng if r in ab_rmsf])), 3)
    h3 = cdr["H3"][1]
    h3_ca = [i for i in t.topology.select("chainid 0 and name CA")
             if t.topology.atom(i).residue.resSeq in h3]
    h3_rmsf = round(float(np.mean([rmsf[i] * 10 for i in h3_ca])), 3) if h3_ca else None

    nterm, core, cterm = range(1, 6), range(6, 12), range(12, 17)
    result = {
        "stage": 2, "step": "2.3_md_flexibility", "platform": plat_name,
        "seed_pose": args.pdb, "ns": args.ns, "n_frames": t.n_frames,
        "n_framework_CA_restrained": n_restr,
        "abeta_rmsf_A": ab_rmsf, "abeta_coil_fraction": coil_frac,
        "abeta_rmsf_means_A": {"Nterm_1_5": mean_rmsf(nterm), "core_6_11": mean_rmsf(core),
                               "Cterm_12_16": mean_rmsf(cterm)},
        "abeta_coil_means": {"Nterm_1_5": round(float(np.mean([coil_frac[r] for r in nterm if r in coil_frac])), 3),
                             "core_6_11": round(float(np.mean([coil_frac[r] for r in core if r in coil_frac])), 3),
                             "Cterm_12_16": round(float(np.mean([coil_frac[r] for r in cterm if r in coil_frac])), 3)},
        "cdrh3_rmsf_A": h3_rmsf,
        "B3_verdict": {
            "abeta_largely_coil": float(np.mean(list(coil_frac.values()))) >= 0.6,
            "nterm_flexible": mean_rmsf(nterm) >= 1.5,
            "note": "B3 = engaged Aβ N-terminus stays flexible/unstructured. Implicit-solvent MD with "
                    "Fv-framework CA restraints; short timescale -> qualitative. Pose=hypothesis (D-002).",
        },
    }
    (out / "md_flexibility.json").write_text(json.dumps(result, indent=2))
    try:
        commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = None
    (out / "manifest_md.json").write_text(json.dumps(
        {"stage": 2, "step": "2.3_md", "tool": f"OpenMM ({plat_name}) + mdtraj (lecam-md)",
         "forcefield": "amber14-all + implicit/gbn2", "ns": args.ns, "seed_pose": args.pdb,
         "git_commit": commit, "outputs": ["md_flexibility.json", "md_traj.dcd", "md_top.pdb", "md.log"]}, indent=2))
    print("PLATFORM", plat_name, "| frames", t.n_frames)
    print("Aβ RMSF means (Å):", result["abeta_rmsf_means_A"])
    print("Aβ coil fraction:", result["abeta_coil_means"])
    print("CDR-H3 RMSF (Å):", h3_rmsf)
    print("B3 verdict:", result["B3_verdict"])
    print("MD_FLEX_DONE")


if __name__ == "__main__":
    main()
