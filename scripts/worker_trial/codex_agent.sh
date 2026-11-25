#!/bin/sh
# Adapt `chitty run`'s agent interface to `codex exec`.
# Usage: codex_agent.sh --model <model> <prompt> [-c]
# The runner adds `-c` to continue the latest session; for Codex that is
# `codex exec resume --last`. Reasoning effort matches Pi's `medium`.
set -eu
[ "$1" = --model ] || { echo "usage: codex_agent.sh --model <model> <prompt> [-c]" >&2; exit 2; }
model=$2
prompt=$3
shift 3
common="--dangerously-bypass-approvals-and-sandbox -m $model -c model_reasoning_effort=medium"
if [ "${1:-}" = -c ]; then
    exec codex exec resume --last $common "$prompt" </dev/null
fi
exec codex exec $common "$prompt" </dev/null
