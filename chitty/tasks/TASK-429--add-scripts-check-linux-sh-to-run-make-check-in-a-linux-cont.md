---
title: Add `scripts/check_linux.sh` to run `make check` in a Linux container
status: doing
priority: medium
created: 2026-11-19
---

## Description

On 2026-11-19 the `v0.6.0` release failed on GitHub (run `44579941402`) with two tests that pass on macOS: `test_main_behind_origin_is_refused` (the runner's Git default branch is `master`) and `test_wrapped_criterion_is_one_criterion` (temp files are in `/tmp`, which the old `.gitignore` entry `tmp/` matched). Both were fixed in `251c161a` and `b4bd8406`. Nothing checks Linux before a release tag is pushed. This ticket adds a script that runs `make install` and `make check` in a Linux container; later tickets call it on landing and in `make release`.

Decisions:

- New `scripts/check_linux.sh` (POSIX `sh`, `set -eu`), run from the repository root with no arguments: `sh scripts/check_linux.sh`. It checks the committed `HEAD` only; uncommitted changes are not included, and it says so in a comment at the top.
- New `scripts/linux-check.Dockerfile`, with exact pins: `FROM ghcr.io/astral-sh/uv:0.13.5 AS uv`, then `FROM node:22.23.5-bookworm` (the `Install Node` step of release run `44579941402` printed `node: v22.23.5`), `COPY --from=uv /uv /uvx /usr/local/bin/`, `USER node`, `RUN mkdir -p /home/node/.cache/uv /home/node/.npm && uv python install 3.12`, `WORKDIR /home/node`. It runs as the image's non-root `node` user, as GitHub runners do, so permission tests behave as in CI.
- The script runs `docker build --quiet -t chitty-linux-check -f scripts/linux-check.Dockerfile scripts`, then pipes `git archive --format=tar HEAD` into `docker run --rm -i -v chitty-linux-uv:/home/node/.cache/uv -v chitty-linux-npm:/home/node/.npm chitty-linux-check sh -c '...'`. Inside, `set -e`: make `work`, extract the archive there, `git init -q -b main`, `git add -A`, commit with `git -c user.name=check -c user.email=check@example.invalid commit -qm snapshot`, then `make install` and `make check`. The snapshot is on `main`, like the developer checkout it copies. No global Git config is set in the container, so the repositories the tests create get a fresh runner's Git defaults (`master`, no identity), which is what broke `v0.6.0`.
- It never mounts the checkout, so the host's macOS `.venv` and `node_modules` are untouched. The named volumes only cache downloads.
- The script exits with `make check`'s status. When Docker is missing or not running, `docker` fails and the script exits non-zero with its error; it never skips.
- No Makefile target: later tickets call the script. Add one line about it to the `make check` bullet in `AGENTS.md`, and correct that bullet while there: it says `make check` runs "Node tests", but the `Makefile` runs none; the Node dependency is the pinned prettier used by `tests/test_formatters.py`.

A prototype of exactly this, run on 2026-11-19, took about 20 seconds with warm caches. It passed at `main` (`a6dcd13b`) and at `251c161a^` (before both fixes) it failed exactly `test_main_behind_origin_is_refused` and `test_wrapped_criterion_is_one_criterion`. The output names failing tests in the `unittest` summary (`test_x (tests.module.Class.test_x)` lines after `=====`); `unittest-parallel` prints no `FAIL:` prefix.

No property and no unit test: the behaviour is real Docker and Git processes, with no pure core to take out. The evidence is running the script.

Out of scope: running it on landing (later tickets) or in `make release`, CI changes, x86_64 emulation (the container uses the host architecture).

## Acceptance Criteria

- [ ] At `HEAD`, `sh scripts/check_linux.sh` exits 0 and the last line of its output is the `unittest` summary `OK`; a note records the command, exit status, that last line and the run time
- [ ] With the script committed, a temporary commit made in the ticket worktree by `git revert --no-edit 251c161a b4bd8406` then `git reset --soft HEAD~2` and `git commit -m revert-fixes` (it undoes both 2026-11-19 Linux fixes) makes `sh scripts/check_linux.sh > <log> 2>&1` exit non-zero, and `grep -F test_main_behind_origin_is_refused <log>` and `grep -F test_wrapped_criterion_is_one_criterion <log>` each match; a note records the exit status and both matches. If the script passes, return the ticket to `planning` with its output instead. Then, whatever the exit status, `git reset --hard HEAD~1` removes the temporary commit
- [ ] In the ticket worktree, `touch <stamp>` immediately before one `sh scripts/check_linux.sh` run, then `find .venv node_modules -newer <stamp> | wc -l` prints `0`, and `git status --porcelain` is the same before and after the run; a note records both. `make check` in the ticket worktree exits 0
- [ ] A note records the output of `grep -n -E "^FROM|^COPY|^USER|uv python install" scripts/linux-check.Dockerfile`, showing exactly the pins under Decisions, and of `head -5 scripts/check_linux.sh`, showing the comment that it checks committed `HEAD` only. `env PATH=/usr/bin:/bin /bin/sh scripts/check_linux.sh` (no `docker` on that path on this Mac) exits non-zero with an error naming `docker`, and the note records it

## Plan

Add the pinned Linux Dockerfile and POSIX check script exactly as specified. Update the make-check guidance in AGENTS.md to describe the actual checks and Linux script. Verify the script and environment behavior, run make check, record criterion evidence in ticket notes, then commit implementation files with Task: TASK-429.

## Notes

Criterion 1: `sh scripts/check_linux.sh` exited 0; last output line `OK`; elapsed 18 seconds (warm cache, run after commit 0442e9c5).

Criterion 2: temporary `revert-fixes` commit caused script exit status 2; both `grep -F` checks matched `test_main_behind_origin_is_refused` and `test_wrapped_criterion_is_one_criterion`. Removed temporary commit with `git reset --hard HEAD~1`; branch restored to 0442e9c5.

Criterion 3: `touch` stamp immediately before script run; `find .venv node_modules -newer <stamp> | wc -l` printed 0; `git status --porcelain` identical before and after (AGENTS.md modified and two scripts untracked at that point). `make check` exited 0: ruff format/check, pyright and all 765 unittest suites passed.

Criterion 4: Dockerfile inspection printed the exact pinned FROM/COPY/USER/uv install lines; `head -5 scripts/check_linux.sh` showed committed-HEAD-only comment. `env PATH=/usr/bin:/bin /bin/sh scripts/check_linux.sh` exited 127 with `docker: command not found`.

## Summary

Implemented and committed Linux Docker check as 0442e9c5. Verified Linux check passes (18s), demonstrated both regressions without the prior fixes and removed the temporary revert commit. `make check` passes. Working tree clean.

## History

- 2026-11-19T18:36:33Z daring-amber-kestrel → planning
- 2026-11-19T18:36:49Z daring-amber-kestrel: changed description
- 2026-11-19T18:37:05Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T18:37:20Z daring-amber-kestrel planning → cold-read
- 2026-11-19T18:38:25Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T18:38:25Z daring-amber-kestrel cold-read → planning
- 2026-11-19T18:38:29Z daring-amber-kestrel planning → cold-read
- 2026-11-19T18:39:44Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T18:39:44Z daring-amber-kestrel cold-read → planning
- 2026-11-19T18:39:55Z daring-amber-kestrel planning → todo
- 2026-11-19T20:11:21Z calm-ochre-quail todo → doing
- 2026-11-19T20:17:28Z calm-ochre-quail: wrote the plan
- 2026-11-19T20:34:16Z calm-ochre-quail: changed notes, summary
