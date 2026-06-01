#!/usr/bin/env bash
# Detect the current cluster and source its env file.
# Usage:  source scripts/_detect_cluster.sh   (sets $CLUSTER and exports env vars)
_REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
case "$(hostname -f 2>/dev/null || hostname)" in
  *frontenac*|frnt*) CLUSTER=frontenac ;;   # COORDINATOR
  *nibi*)            CLUSTER=nibi ;;         # worker (when activated)
  *narval*)          CLUSTER=narval ;;       # worker (when activated)
  *) echo "ERROR: unknown cluster: $(hostname -f 2>/dev/null || hostname)" >&2; return 1 2>/dev/null || exit 1 ;;
esac
export CLUSTER
# shellcheck disable=SC1090
source "${_REPO_ROOT}/clusters/${CLUSTER}.env"
