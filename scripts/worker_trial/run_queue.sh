#!/bin/sh
# Run every "<variant> <ticket> <base> [<branch-start>]" line of a queue file.
# Usage: TRIAL_DIR=tmp/worker-trial/round2 run_queue.sh <queue-file> [<parallel>]
# Keep `parallel` at 2-4: each run's `make check` is heavy. agy lines must run
# one at a time (see run_trial.sh), so give them their own queue with parallel 1.
set -eu
[ $# -ge 1 ] || { sed -n '3,5p' "$0" >&2; exit 2; }
here=$(cd "$(dirname "$0")" && pwd)
grep -v '^#' "$1" | grep . | xargs -P "${2:-2}" -L 1 "$here/run_trial.sh"
