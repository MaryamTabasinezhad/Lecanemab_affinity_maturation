#!/usr/bin/env python
"""Run ONE flex_ddG backrub trajectory via PyRosetta (no compiled rosetta_scripts binary).

Drives the Kortemme-lab ddG-backrub.xml through PyRosetta's RosettaScriptsParser with
script_vars; writes ddG.db3 (+ struct.db3) to <out>. One process = one nstruct trajectory
(parallelize via a SLURM array). Aggregate db3s with analyze_flexddg.py.
"""
import argparse, os
HERE = os.path.dirname(os.path.abspath(__file__))
XML = os.path.join(HERE, "ddG-backrub.xml")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdb", required=True)
    ap.add_argument("--resfile", required=True)
    ap.add_argument("--chains", required=True, help="chains to move (the partner separated for unbound), e.g. P")
    ap.add_argument("--out", required=True)
    ap.add_argument("--backrub", type=int, default=35000)
    ap.add_argument("--min-iter", type=int, default=5000)
    ap.add_argument("--stride", type=int, default=35000)
    ap.add_argument("--abs-thresh", type=float, default=1.0)
    args = ap.parse_args()

    pdb = os.path.abspath(args.pdb); resfile = os.path.abspath(args.resfile)
    os.makedirs(args.out, exist_ok=True)
    import pyrosetta
    flags = (
        "-restore_talaris_behavior -in:file:fullatom -ignore_unrecognized_res "
        "-ignore_zero_occupancy false -ex1 -ex2 -mute all "
        f"-parser:script_vars chainstomove={args.chains} "
        f"mutate_resfile_relpath={resfile} "
        f"number_backrub_trials={args.backrub} max_minimization_iter={args.min_iter} "
        f"abs_score_convergence_thresh={args.abs_thresh} backrub_trajectory_stride={args.stride}"
    )
    pyrosetta.init(flags)
    pose = pyrosetta.pose_from_pdb(pdb)
    os.chdir(args.out)                 # ddG.db3 / struct.db3 land in cwd
    from pyrosetta.rosetta.protocols.rosetta_scripts import RosettaScriptsParser
    mover = RosettaScriptsParser().generate_mover(XML)
    mover.apply(pose)
    print("FLEXDDG_TRAJ_DONE", os.path.abspath("ddG.db3"))


if __name__ == "__main__":
    main()
