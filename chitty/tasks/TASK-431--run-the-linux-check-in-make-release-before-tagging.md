---
title: Run the Linux check in `make release` before tagging
status: review
priority: medium
depends_on:
  - TASK-429
created: 2026-11-19
---

## Description

`scripts/release.sh` runs `make check` in its temporary release worktree, then commits the version bump, tags and pushes. A Linux-only failure is found only by the GitHub publish workflow after the tag is pushed, which is how `v0.6.0` was lost on 2026-11-19. This ticket depends on `TASK-429`, which adds `scripts/check_linux.sh`; start it only once that has landed. Then run it in `make release` before anything is tagged or pushed.

Decisions:

- In `scripts/release.sh`, after `git commit --quiet -m "Release $version"` and before `git tag "v$version"`, run it as `if ! sh scripts/check_linux.sh; then ... fi`, the same form as the `make check` step (a bare call under `set -eu` would exit without the message). It checks committed `HEAD` only, so it must follow the commit. Its own output, including a `docker` error when Docker is missing or not running, goes straight to the terminal, so the real cause stays visible; `make release` therefore needs Docker running. On failure, after that output, print `release: Linux check failed at $version; nothing was pushed` to stderr and exit 1. No tag is made; the existing `EXIT` trap removes the release worktree, and the release commit, on a detached `HEAD`, is left unreferenced.
- Update the step list in the comment at the top of `scripts/release.sh` and the release bullet in `AGENTS.md` (`make release` ... checks the version there) to mention the Linux check.

Tests, in `tests/test_release_script.py` (`TestReleaseScript`). Its `setUp` copies only `release.sh` and `release_version.py` into the fixture repository, so also write a fake `scripts/check_linux.sh` there before the `base` commit, with two lines: `git log -1 --format=%s >> "<tmp>/linux-ran"` and `sh "<tmp>/linux.sh"`, where `<tmp>` is `self.tmp`. `setUp` also writes `self.tmp / "linux.sh"` containing `true`, next to where it writes `check_script` (also `true`); tests that need a failure overwrite it.

- `test_releases_while_main_moves_and_the_checkout_is_dirty`: also assert `linux-ran` reads exactly `Release 0.1.1\n` (the Linux check ran once, on the release commit).
- New `test_failed_linux_check_pushes_nothing_and_removes_the_worktree`: `linux.sh` holds `exit 1`. Assert a non-zero exit; stderr contains `Linux check failed at 0.1.1`; `origin_git("rev-parse", "main")` and local `git rev-parse main` are unchanged; `git tag --list v0.1.1` and `origin_git("tag", "--list", "v0.1.1")` are empty; `.worktrees/release` does not exist; `self.watched` does not exist. Today it exits 0 and pushes. This test is the evidence that the check runs before the tag and push; the success-path assertion only shows it ran once, on the release commit.
- `test_failed_check_publishes_nothing_and_removes_the_worktree`: also assert `linux-ran` does not exist (a failing `make check` stops before the Linux check). This assertion passes on today's code too: it guards the order of the two checks and is not evidence for the change.

No property: one fixed step in a shell script, driven through real Git with every outcome listed above and tested.

Out of scope: the landing check (`HUMAN-13`), retrying, and the GitHub workflows.

## Acceptance Criteria

- [ ] The new `test_failed_linux_check_pushes_nothing_and_removes_the_worktree` passes with every assertion in the Description; a note records that it fails against `scripts/release.sh` without the change
- [ ] The two existing tests named in the Description pass with their added `linux-ran` assertions; a note records that the success-path assertion fails without the change
- [ ] The comment in `scripts/release.sh` and the release bullet in `AGENTS.md` mention the Linux check; `make check` passes

## Plan

Add a fixture Linux-check script and assertions proving it runs on the committed release commit and prevents tag/push on failure. Run regression tests before changing release.sh, then implement the check and update release documentation. Verify with focused tests and make check, then commit implementation files.

## Notes

Regression evidence: before changing scripts/release.sh, the new Linux-failure test failed because release returned 0 and pushed; the success-path test also errored because linux-ran was absent.

The success-path linux-ran assertion also failed before implementation (linux-ran did not exist); it now proves the check ran once against Release 0.1.1. Focused release tests and make check pass.

## Summary

Implemented Linux check after release commit and before tag/push; failure aborts with required diagnostic and leaves no tag/push/worktree. Updated fixture regression coverage and release docs. Verified focused release tests and make check (788 tests). Follow-up: none.

## History

- 2026-11-19T18:45:25Z daring-amber-kestrel → planning
- 2026-11-19T18:46:31Z daring-amber-kestrel planning → cold-read
- 2026-11-19T20:34:52Z daring-amber-kestrel: changed description
- 2026-11-19T20:34:52Z daring-amber-kestrel cold-read → planning
- 2026-11-19T20:34:57Z daring-amber-kestrel planning → todo
- 2026-11-20T00:24:32Z intrepid-lilac-ibis todo → doing
- 2026-11-20T00:27:18Z intrepid-lilac-ibis: wrote the plan
- 2026-11-20T00:27:47Z intrepid-lilac-ibis: changed notes
- 2026-11-20T00:30:22Z intrepid-lilac-ibis: changed notes, summary
- 2026-11-20T00:30:35Z intrepid-lilac-ibis doing → review
