---
title: Run the Linux check in `make release` before tagging
status: cold-read
priority: medium
depends_on:
  - TASK-429
created: 2026-11-19
---

## Description

`scripts/release.sh` runs `make check` in its temporary release worktree, then commits the version bump, tags and pushes. A Linux-only failure is found only by the GitHub publish workflow after the tag is pushed, which is how `v0.6.0` was lost on 2026-11-19. After `TASK-429` adds `scripts/check_linux.sh`, run it in `make release` before anything is tagged or pushed.

Decisions:

- In `scripts/release.sh`, after `git commit --quiet -m "Release $version"` and before `git tag "v$version"`, run `sh scripts/check_linux.sh`. It checks committed `HEAD` only, so it must follow the commit. On failure, print `release: Linux check failed at $version; nothing was pushed` to stderr and exit 1. No tag is made; the existing `EXIT` trap removes the release worktree, and the release commit, on a detached `HEAD`, is left unreferenced.
- Update the step list in the comment at the top of `scripts/release.sh` and the release bullet in `AGENTS.md` (`make release` ... checks the version there) to mention the Linux check.

Tests, in `tests/test_release_script.py` (`TestReleaseScript`). Its `setUp` copies only `release.sh` and `release_version.py` into the fixture repository, so also write a fake `scripts/check_linux.sh` there before the `base` commit, with two lines: `git log -1 --format=%s >> "<tmp>/linux-ran"` and `sh "<tmp>/linux.sh"`, where `<tmp>` is `self.tmp` and `self.tmp / "linux.sh"` holds `true` by default (as `check_script` holds `true`).

- `test_releases_while_main_moves_and_the_checkout_is_dirty`: also assert `linux-ran` reads exactly `Release 0.1.1\n` (the Linux check ran once, on the release commit).
- New `test_failed_linux_check_pushes_nothing_and_removes_the_worktree`: `linux.sh` holds `exit 1`. Assert a non-zero exit; stderr contains `Linux check failed at 0.1.1`; `origin_git("rev-parse", "main")` and local `git rev-parse main` are unchanged; `git tag --list v0.1.1` and `origin_git("tag", "--list", "v0.1.1")` are empty; `.worktrees/release` does not exist; `self.watched` does not exist. Today it exits 0 and pushes.
- `test_failed_check_publishes_nothing_and_removes_the_worktree`: also assert `linux-ran` does not exist (a failing `make check` stops before the Linux check).

No property: one fixed step in a shell script, driven through real Git with every outcome listed above and tested.

Out of scope: the landing check (`HUMAN-13`), retrying, and the GitHub workflows.

## Acceptance Criteria

- [ ] The new `test_failed_linux_check_pushes_nothing_and_removes_the_worktree` passes with every assertion in the Description; a note records that it fails against `scripts/release.sh` without the change
- [ ] The two existing tests named in the Description pass with their added `linux-ran` assertions; a note records that the success-path assertion fails without the change
- [ ] The comment in `scripts/release.sh` and the release bullet in `AGENTS.md` mention the Linux check; `make check` passes

## History

- 2026-11-19T18:45:25Z daring-amber-kestrel → planning
- 2026-11-19T18:46:31Z daring-amber-kestrel planning → cold-read
