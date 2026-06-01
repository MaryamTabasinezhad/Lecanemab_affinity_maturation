# <Cluster> — Worker (Agent <Cluster>)

You are on **<Cluster>**. You are a **worker agent** coordinated from Frontenac.

## Worker responsibilities
1. `git pull origin main` at session start; read `coordination/DASHBOARD.md` + your inbox.
2. Execute the assigned task EXACTLY (inbox message or manifest).
3. Commit small results (CSVs, status, scored ledger-row CSVs) to git; push with a `[<cluster>]` prefix.
4. Move large data to the coordinator via Globus.
5. Delete inbox messages after actioning them.

## Do NOT
- Make campaign decisions or change parameters/configs without coordinator approval.
- Edit other clusters' DASHBOARD rows.

## HPC details
Source `clusters/<cluster>.env` (account, GRES, walltime, env names, Globus). Confirm module names before first submit.
