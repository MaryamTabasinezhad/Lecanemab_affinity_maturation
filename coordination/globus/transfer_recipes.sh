#!/usr/bin/env bash
# Reusable Globus transfer recipes for lecanemab-am. Fill endpoint UUIDs from endpoints.md.
# Requires: globus-cli (`pip install globus-cli`; `globus login`).
set -euo pipefail

FRONTENAC_EP="CONFIRM"
NARVAL_EP="a1713da6-098f-40e6-b3aa-034efe8b6e5b"   # confirm
NIBI_EP="CONFIRM"

# Example: push antigen templates Frontenac -> Narval
# globus transfer "$FRONTENAC_EP:/global/project/hpcg6049/lecanemab-am/data/raw/antigen" \
#                 "$NARVAL_EP:<narval lecanemab-am path>/data/raw/antigen" \
#                 --recursive --label "antigen->narval"

# Example: pull worker model samples Narval -> Frontenac
# globus transfer "$NARVAL_EP:<path>/results" \
#                 "$FRONTENAC_EP:/global/scratch/hpc6049/lecanemab-am/results" \
#                 --recursive --label "narval-results->frontenac"
echo "Edit this file with concrete endpoint UUIDs + paths before use."
