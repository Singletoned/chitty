#!/bin/sh
# Print the commit just before a done ticket was claimed: main as the worker found it.
# Usage: find_base.sh TASK-N   (run from the repository root)
# Fails if the ticket never reached `todo` before its implementation commit.
set -eu
t=$1
impl=$(git log --reverse --format='%H %s' --grep="^Task: $t\$" main | grep -v ' chitty: ' | head -1 | cut -d' ' -f1)
c=$impl^
status() { f=$(git ls-tree -r --name-only "$1" -- chitty | grep "/$t--" | head -1); git show "$1:$f" 2>/dev/null | sed -n 's/^status: //p' | head -1; }
while [ "$(status "$c")" != todo ]; do
    case "$(git log -1 --format=%s "$c")" in
        "chitty: edit $t "*|"chitty: "*" $t "*) c=$c^ ;;
        *) echo "no todo state before the work on $t (stopped at $(git rev-parse --short "$c"))" >&2; exit 1 ;;
    esac
done
git rev-parse "$c"
