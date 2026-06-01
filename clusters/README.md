# clusters/ — per-cluster config & how to add a worker

Each cluster has `clusters/<name>.env` (sourceable paths/SLURM/Globus) and
`clusters/<name>/CLAUDE.md` (agent role). Scripts detect the cluster via
`scripts/_detect_cluster.sh` and source the right `.env`.

## Activate a new worker (~5 min)
1. `cp clusters/_cluster.env.template clusters/<name>.env` and fill it in (CONFIRM all paths/accounts).
2. `mkdir -p clusters/<name> && cp clusters/_worker_CLAUDE.template.md clusters/<name>/CLAUDE.md` (set <Cluster>).
3. `mkdir -p coordination/inbox/<name> && touch coordination/inbox/<name>/.gitkeep`.
4. Add a row for <name> in `coordination/DASHBOARD.md` and the registry in `coordination/COORDINATION.md`.
5. Add the hostname pattern to the `case` in root `CLAUDE.md` §0 AND `scripts/_detect_cluster.sh`.
6. Add the Globus endpoint to `coordination/globus/endpoints.md`.
7. On the worker: clone `git@github.com:MaryamTabasinezhad/Lecanemab_affinity_maturation.git`; run `hostname -f` to verify detection.

Candidates (from the lab's prior bispecific project): **Narval**, **Nibi** — env stubs present, marked CONFIRM.
