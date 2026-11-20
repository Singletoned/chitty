#!/bin/sh
# Release from a temporary worktree, so the main checkout may be dirty and
# commits landing on `main` meanwhile (runners, other sessions) cannot break
# the release. Run by `make release`; takes no arguments.
#
# Steps: fetch; make a detached worktree at `main`; install, choose the version,
# bump `src/chitty/__init__.py`, run `make check`, commit, run the Linux check,
# and tag there; push the
# commit to `origin/main` and the tag atomically; merge the tag into the local
# `main`; remove the worktree; wait for the publish workflow.
set -eu

root=$(git rev-parse --show-toplevel)
worktree="$root/.worktrees/release"

git -C "$root" fetch origin
if ! git -C "$root" merge-base --is-ancestor origin/main main; then
	echo "release: main is behind origin/main; merge origin/main first" >&2
	exit 1
fi
if [ -e "$worktree" ]; then
	echo "release: $worktree exists; remove it with git worktree remove --force $worktree" >&2
	exit 1
fi

git -C "$root" worktree add --quiet --detach "$worktree" main
trap 'git -C "$root" worktree remove --force "$worktree"' EXIT
cd "$worktree"

# Use the release worktree's own environment, not one exported by direnv.
unset VIRTUAL_ENV
export UV_PROJECT_ENVIRONMENT="$worktree/.venv"

make install
version=$(uv run python scripts/release_version.py)
python3 -c '
import re, sys
from pathlib import Path
path = Path("src/chitty/__init__.py")
path.write_text(re.sub(r"__version__ = \"[^\"]+\"", f"__version__ = \"{sys.argv[1]}\"", path.read_text()))
' "$version"
if ! make check; then
	echo "release: checks failed at $version; nothing was committed" >&2
	exit 1
fi
git add src/chitty/__init__.py
git commit --quiet -m "Release $version"
if ! sh scripts/check_linux.sh; then
	echo "release: Linux check failed at $version; nothing was pushed" >&2
	exit 1
fi
git tag "v$version"
if ! git push --atomic origin "HEAD:refs/heads/main" "v$version"; then
	echo "release: push failed; delete the local tag with git tag -d v$version" >&2
	exit 1
fi

# The release commit's parent is the `main` this script started from. If
# `main` has moved since, this makes a merge commit; otherwise it fast-forwards.
if ! git -C "$root" merge --quiet --no-edit "v$version"; then
	echo "release: v$version is published, but merging it into main failed;" \
		"run git merge v$version in $root" >&2
	exit 1
fi

pending="${XDG_DATA_HOME:-$HOME/.local/share}/chitty/pending-release"
mkdir -p "$(dirname "$pending")"
echo "$version" >"$pending"
python3 "$root/scripts/watch_release.py" "$version"
