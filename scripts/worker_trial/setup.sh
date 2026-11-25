#!/bin/sh
# Install the Pi versions the trials compare under tmp/worker-trial/pi/<version>,
# leaving the global Pi alone. Codex, Claude Code and agy use their global installs.
set -eu
repo=$(cd "$(dirname "$0")/../.." && pwd)
for version in 1.5.2 1.6.0; do
    prefix=$repo/tmp/worker-trial/pi/$version
    [ -x "$prefix/node_modules/.bin/pi" ] && continue
    npm install --silent --prefix "$prefix" "@earendil-works/pi-coding-agent@$version"
done
for version in 1.5.2 1.6.0; do
    printf 'pi %s: ' "$version"
    "$repo/tmp/worker-trial/pi/$version/node_modules/.bin/pi" --version
done
