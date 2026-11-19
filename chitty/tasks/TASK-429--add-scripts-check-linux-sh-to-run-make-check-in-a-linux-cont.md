---
title: Add `scripts/check_linux.sh` to run `make check` in a Linux container
status: planning
priority: medium
created: 2026-11-19
---

## Description

On 2026-11-19 the `v0.6.0` release failed on GitHub (run `44579941402`) with two tests that pass on macOS: `test_main_behind_origin_is_refused` (the runner'\''s Git default branch is `master`) and `test_wrapped_criterion_is_one_criterion` (temp files are in `/tmp`, which the old `.gitignore` entry `tmp/` matched). Both were fixed in `251c161a` and `b4bd8406`. Nothing checks Linux before a release tag is pushed. This ticket adds a script that runs `make install` and `make check` in a Linux container; later tickets call it on landing and in `make release`.

Decisions:

- New `scripts/check_linux.sh` (POSIX `sh`, `set -eu`), run from the repository root with no arguments: `sh scripts/check_linux.sh`. It checks the committed `HEAD` only; uncommitted changes are not included, and it says so in a comment at the top.
- New `scripts/linux-check.Dockerfile`, with exact pins: `FROM ghcr.io/astral-sh/uv:0.13.5 AS uv`, then `FROM node:22.23.5-bookworm` (the Node version the `v0.6.0` run used), `COPY --from=uv /uv /uvx /usr/local/bin/`, `USER node`, `RUN mkdir -p /home/node/.cache/uv /home/node/.npm && uv python install 3.12`, `WORKDIR /home/node`. It runs as the image'\''s non-root `node` user, as GitHub runners do, so permission tests behave as in CI.
- The script runs `docker build --quiet -t chitty-linux-check -f scripts/linux-check.Dockerfile scripts`, then pipes `git archive --format=tar HEAD` into `docker run --rm -i -v chitty-linux-uv:/home/node/.cache/uv -v chitty-linux-npm:/home/node/.npm chitty-linux-check sh -c '\''...'\''`. Inside, `set -e`: make `work`, extract the archive there, `git init -q -b main`, `git add -A`, commit with `git -c user.name=check -c user.email=check@example.invalid commit -qm snapshot`, then `make install` and `make check`. No global Git config is set in the container, so Git defaults match a fresh runner.
- It never mounts the checkout, so the host'\''s macOS `.venv` and `node_modules` are untouched. The named volumes only cache downloads.
- The script exits with `make check`'\''s status. When Docker is missing or not running, `docker` fails and the script exits non-zero with its error; it never skips.
- No Makefile target: later tickets call the script. Add one line about it to the `make check` bullet in `AGENTS.md`.

A prototype of exactly this, run on 2026-11-19, took about 20 seconds with warm caches. It passed at `main` (`a6dcd13b`) and at `251c161a^` it failed exactly `test_main_behind_origin_is_refused` and `test_wrapped_criterion_is_one_criterion`. The output names failing tests in the `unittest` summary (`test_x (tests.module.Class.test_x)` lines after `=====`); `unittest-parallel` prints no `FAIL:` prefix.

No property and no unit test: the behaviour is real Docker and Git processes, with no pure core to take out. The evidence is running the script.

Out of scope: running it on landing (`TASK` for the landing check) or in `make release`, CI changes, x86_64 emulation (the container uses the host architecture).

## Acceptance Criteria

- [ ] At `HEAD`, `sh scripts/check_linux.sh` exits 0 and its output ends with the `unittest` `OK` summary; a note records the command, exit status and run time
- [ ] In a scratch worktree at `251c161a^` with the new script files copied in and committed, the script exits non-zero and its output names `test_main_behind_origin_is_refused` and `test_wrapped_criterion_is_one_criterion` as failing; a note records this. The scratch worktree and branch are then removed
- [ ] After a run, `git status --porcelain` in the checkout is unchanged, and `.venv` and `node_modules` were not modified (record their modification times before and after in the note); `make check` passes

## History

- 2026-11-19T18:36:33Z daring-amber-kestrel → planning
