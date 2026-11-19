#!/bin/sh
# Checks committed HEAD only; uncommitted changes are not included.
set -eu

docker build --quiet -t chitty-linux-check \
    -f scripts/linux-check.Dockerfile scripts
git archive --format=tar HEAD | docker run --rm -i \
    -v chitty-linux-uv:/home/node/.cache/uv \
    -v chitty-linux-npm:/home/node/.npm \
    chitty-linux-check sh -c '
        set -e
        mkdir work
        tar -xf - -C work
        cd work
        git init -q -b main
        git add -A
        git -c user.name=check -c user.email=check@example.invalid \
            commit -qm snapshot
        make install
        make check
    '
