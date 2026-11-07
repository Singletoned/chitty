---
title: Stop telling workers to run `chitty inbox --pull`
status: doing
priority: medium
depends_on:
  - TASK-142
created: 2026-11-05
---

## Description

A worker's first step is `chitty inbox --pull`, from `src/chitty/roles/work.md` line 6 and `src/chitty/guide.md` line 8, which also reaches `AGENTS.md`'s managed block through `chitty init`. `chitty run` already pulls before it starts an agent (`src/chitty/run.py`), so this only spends a call. Seen on 2026-11-05 in a real session on `TASK-142`, where the human said it should not be doing that.

Remove the instruction from both files, leaving `chitty show <ID>` as the first step. In `work.md` the instruction wraps onto line 7, so rejoin the line, and keep each file's own word, `ticket` or `task`. Edit only this bullet: `TASK-173` also edits `work.md`, and `TASK-143` rewrites `guide.md`. No test expects the old text. `chitty list` already tells people when suggestions are waiting (`src/chitty/cli.py`), which covers manual sessions, and `review.md` and `plan.md` never had the instruction. `--pull` mentions in `src/chitty/cli.py` and `tests/test_cli.py` are other hints, and stay.

## Acceptance Criteria

- [x] `chitty guide work` and `chitty guide` no longer contain `inbox --pull`, shown by a test, and `chitty inbox --pull` itself still works
- [x] `AGENTS.md` no longer contains `inbox --pull`, after running `uv run chitty init` from the worktree, and `__version__` is bumped above `main`'s at the time of review

## Plan

Update the two managed worker-instruction source files only: remove the initial `chitty inbox --pull` wording while preserving each file’s existing `ticket`/`task` terminology and joining the wrapped `work.md` line. Bump the package patch version because `chitty init` output changes. Add or update focused tests proving both guides omit the pull instruction and that the inbox command remains functional, then run init and the required checks.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: how to check `AGENTS.md`, the wrapped line, and who loses the pull, since `chitty list`'s hint covers them. Dependency on `TASK-142` kept, though soft: it is in review, and it bumps the same version. Rejected: mentioning that the pull is skipped on the first run after a project is added, which this change does not affect.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`.

Rebased onto main after the prior integration review failure; resolved the guide test and version conflicts while retaining both TASK-179 and main coverage.

Owner set to `human` so the review loop skips this until `TASK-212` lands: the branch records `0.1.35` and `main`'s `0.1.34` `chitty` refuses to write here. Clear the owner then.

Owner cleared: the branch now has `main`'s `chitty.toml` again, so `main`'s `chitty` can write here.

1: pass - Guide output omits inbox --pull and chitty inbox --pull still works.
2: fail - __version__ is 0.1.35 on this branch and on main, so the required version bump above main is unmet; make check fails its version-bump check. Bump the package version above current main and rerun the checks.

This branch edits Chitty's managed block in `AGENTS.md`. Under `TASK-218`, branches may not: restore the block from `main` (`git checkout main -- AGENTS.md` if the rest of the file is unchanged) and change only `src/chitty/guide.md` or `src/chitty/roles/`. The main checkout regenerates `AGENTS.md` after landing.

Bumped __version__ to 0.1.36 because main was already 0.1.35. updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-179/chitty.toml
updated /Users/singletoned/.local/share/chitty/inbox/chitty regenerated the managed guide and updated chitty.toml locally; chitty.toml was restored per repository guidance that ticket branches only bump __version__. Full unittest suite passed (330 tests); npm test emitted 26 passing dots but did not exit within 300 seconds.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Unblocked by a human-run session. All three failed reviews were rebase conflicts with `main`, mostly on `tests/test_cli.py`'s guide tests and `__version__`, not problems with the work. Rebased onto `main` (`0.1.40`):
- Both sides of each conflicting guide test are kept.
- The new `main` guide text sits alongside this ticket's change; the role files keep `TASK-219`'s sentence.
- `chitty.toml` and `AGENTS.md` match `main` (`TASK-212`, `TASK-218`).
- `__version__` is `0.1.41`.
`make check` passes (360 tests). Several open tickets also use `0.1.41`, so whichever lands second will need its version bumped again.

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/work.md
make: *** [check] Error 1

## Summary

Removed the redundant inbox pull from the worker and general guide sources, preserving each file's ticket/task wording, and regenerated AGENTS.md. Bumped __version__ to 0.1.36 above main. Verified guide and inbox regression tests, uv run chitty init, chitty fix, Ruff, Pyright, version check, and 330 unittest tests. Node tests started and emitted passing results but did not exit within 300 seconds.

## History

- 2026-11-05T09:37:44Z mellow-newt → backlog
- 2026-11-05T09:40:00Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T09:40:01Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T09:40:02Z mellow-newt backlog → todo
- 2026-11-05T23:20:21Z open-dormouse todo → doing
- 2026-11-05T23:20:36Z open-dormouse: wrote the plan
- 2026-11-05T23:29:50Z open-dormouse: ticked acceptance criteria
- 2026-11-05T23:29:51Z open-dormouse: ticked acceptance criteria
- 2026-11-05T23:29:52Z open-dormouse: changed summary
- 2026-11-05T23:30:02Z open-dormouse doing → review
- 2026-11-06T14:40:24Z jolly-kestrel: changed notes
- 2026-11-06T14:40:24Z jolly-kestrel review → doing
- 2026-11-06T16:07:57Z jolly-stoat: changed notes, summary
- 2026-11-06T16:07:57Z jolly-stoat doing → review
- 2026-11-06T16:25:04Z youthful-toad: changed owner, notes
- 2026-11-06T16:43:39Z youthful-toad: changed owner, notes
- 2026-11-06T16:54:52Z honest-gannet: changed acceptance criteria, notes
- 2026-11-06T16:54:52Z honest-gannet review → doing
- 2026-11-06T18:13:32Z youthful-toad: changed notes
- 2026-11-06T18:28:21Z mellow-urchin: ticked acceptance criteria
- 2026-11-06T18:28:35Z mellow-urchin: changed notes
- 2026-11-06T18:28:36Z mellow-urchin: changed summary
- 2026-11-06T18:28:37Z mellow-urchin doing → review
- 2026-11-06T18:34:28Z upbeat-newt: changed owner, notes
- 2026-11-06T18:34:28Z upbeat-newt review → blocked
- 2026-11-06T21:40:59Z youthful-toad: changed owner, notes
- 2026-11-06T21:40:59Z youthful-toad blocked → review
- 2026-11-06T21:48:16Z brisk-newt: changed notes
- 2026-11-06T21:48:16Z brisk-newt review → doing
- 2026-11-06T21:51:03Z eager-jay: changed notes
- 2026-11-06T21:52:18Z mellow-gannet: changed notes
- 2026-11-06T21:53:25Z kind-yellowhammer: changed notes
- 2026-11-06T22:00:28Z witty-ibis: changed notes
- 2026-11-06T22:01:35Z upbeat-heron: changed notes
- 2026-11-06T22:02:42Z able-otter: changed notes
- 2026-11-06T22:03:54Z vivid-puffin: changed notes
- 2026-11-06T22:05:01Z upbeat-urchin: changed notes
- 2026-11-06T22:06:07Z plucky-toad: changed notes
- 2026-11-06T22:07:14Z plucky-quail: changed notes
- 2026-11-06T22:08:21Z golden-vole: changed notes
- 2026-11-07T08:51:08Z sunny-crane: changed notes
- 2026-11-07T08:52:16Z able-badger: changed notes
- 2026-11-07T08:53:23Z kind-adder: changed notes
- 2026-11-07T08:54:30Z brisk-crane: changed notes
- 2026-11-07T08:55:37Z calm-jay: changed notes
- 2026-11-07T08:56:44Z friendly-yellowhammer: changed notes
- 2026-11-07T08:57:51Z brisk-jay: changed notes
- 2026-11-07T08:58:58Z friendly-badger: changed notes
- 2026-11-07T09:00:05Z honest-ibis: changed notes
- 2026-11-07T09:01:12Z zesty-raven: changed notes
- 2026-11-07T09:02:19Z witty-newt: changed notes
- 2026-11-07T09:03:26Z golden-puffin: changed notes
- 2026-11-07T09:04:34Z youthful-newt: changed notes
- 2026-11-07T09:05:41Z calm-wren: changed notes
- 2026-11-07T09:06:48Z tidy-ibis: changed notes
- 2026-11-07T09:07:56Z sunny-ibis: changed notes
- 2026-11-07T09:09:03Z youthful-quail: changed notes
- 2026-11-07T09:10:10Z jolly-dormouse: changed notes
- 2026-11-07T09:11:18Z plucky-puffin: changed notes
