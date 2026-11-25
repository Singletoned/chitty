#!/bin/sh
# Run a done ticket's landed tests against a trial branch's code.
# Usage: TRIAL_DIR=... hidden_tests.sh <variant> <ticket>
# The landed implementation commit's test files are copied onto a temporary
# checkout of the trial branch and run there. A failure can mean the trial got
# the behaviour wrong, or only that it chose other names than the landed code;
# read the failures before scoring. Prints one summary line.
set -eu
[ $# -eq 2 ] || { sed -n '3,7p' "$0" >&2; exit 2; }
variant=$1
ticket=$2
: "${TRIAL_DIR:?set TRIAL_DIR to this round\'s folder}"
branch=$(printf '%s' "$ticket" | tr 'A-Z' 'a-z')
dir=$(cd "$TRIAL_DIR" && pwd)/runs/$variant--$branch
repo=$(cd "$(dirname "$0")/../.." && pwd)
# Look in the real repository: the clone's main was reset to before the work,
# so the landed commit is in the clone's objects but on none of its branches.
ref=$(git -C "$repo" log --format='%H %s' --grep="^Task: $ticket\$" main | grep -v ' chitty: ' | head -1 | cut -d' ' -f1)
[ -n "$ref" ] || { echo "no landed implementation commit for $ticket" >&2; exit 1; }
files=$(git -C "$dir" diff --name-only "$ref^" "$ref" -- tests)
checkout=$(mktemp -d)
git -C "$dir" worktree add --quiet --detach "$checkout" "$branch"
trap 'git -C "$dir" worktree remove --force "$checkout"' EXIT
(cd "$checkout" && git checkout --quiet "$ref" -- $files)
# Plain unittest: every test is a unittest.TestCase, and older bases have no pytest.
modules=$(printf '%s\n' $files | grep '/test_.*\.py$' | sed 's|\.py$||; s|/|.|g')
output=$(cd "$checkout" && PYTHONPATH=src "$dir/.venv/bin/python" -m unittest $modules 2>&1 || true)
summary="$(printf '%s\n' "$output" | grep '^Ran ' | tail -1); $(printf '%s\n' "$output" | grep -E '^(OK|FAILED)' | tail -1)"
printf '%s\t%s\t%s\n' "$variant" "$ticket" "$summary"
