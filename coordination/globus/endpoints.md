# Globus endpoints — lecanemab-am

Large files (PDBs, model weights, MD/diffusion samples, containers) move via Globus, NOT git.

| Cluster   | Endpoint UUID | Type          | Base path |
|-----------|---------------|---------------|-----------|
| Frontenac | CONFIRM       | personal      | /global/project/hpcg6049/lecanemab-am |
| Narval    | a1713da6-...  | institutional | CONFIRM (.../lecanemab-am) |
| Nibi      | CONFIRM       | institutional | CONFIRM (.../lecanemab-am) |

Initiate transfers via the `globus transfer` CLI or web UI; store reusable
commands in `transfer_recipes.sh`.
