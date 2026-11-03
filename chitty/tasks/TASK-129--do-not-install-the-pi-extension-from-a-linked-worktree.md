---
title: Do not install the Pi extension from a linked worktree
status: done
labels:
  - bug
priority: high
created: 2026-11-03
---

## Description

`init_repo` in `src/chitty/store.py` calls `install_pi_extension`, which copies the running code's `src/chitty/integrations/pi/chitty.ts` to `~/.pi/agent/extensions/chitty.ts`. When code on a ticket branch runs `chitty init`, or a write that triggers the setup upgrade, unfinished extension code becomes active for every Pi session on the machine. On 2026-11-03 at 20:21 the `TASK-126` worker did this. The next `chitty run`, still on `main` code, started Pi in the main checkout, and the leaked extension refused to start.

Only install from a main checkout, not a linked Git worktree. Add `git.is_linked_worktree(directory)`, comparing `git rev-parse --git-dir` with `--git-common-dir` as resolved paths: a plain string comparison wrongly says "linked" in a subdirectory of the main checkout, where they are `/abs/.git` and `../.git`. It returns false outside Git or if `git` is missing, so `chitty init` there still installs, as now; it needs its own `subprocess` call, because `git._git` raises. In a linked worktree, also skip `validate_pi_extension` and `remove_pi_session_environment`: both concern the same machine-wide Pi setup. Report a skip on stderr from `init_repo`, so both `chitty init` and the upgrade on write show it; otherwise `init` just says it is up to date. Immediate repair was to run `chitty init` from the main checkout.

Rollout: the extension then only reaches `~/.pi` when `chitty init` runs in the main checkout. `TASK-120` automates that; until then, run it by hand after landing. If `main` already has this version when the ticket is ready for review, bump again: identical bumps merge silently, and repositories would then never learn about the later change.

Out of scope: code from a branch deliberately run against the main checkout, because the rule looks at the directory being set up and this was not the incident; other setup writes from a worktree, such as `chitty.toml`, which belong to the branch.

## Acceptance Criteria

- [x] A test with a real `git worktree` and a temporary `PI_CODING_AGENT_DIR` runs `chitty init` in the worktree and shows the installed extension unchanged, and it fails before the fix
- [x] A test shows `chitty init` in the main checkout still installs and updates the extension
- [x] `PLAN.md` states the rule, and `__version__` is bumped only if setup output changes
- [x] Tests show `chitty init` installing from a subdirectory of the main checkout and outside Git, and a skip in a worktree printing a message on stderr while leaving `settings.json` unchanged
- [x] A test with `autocommit = true` and a stale `chitty_version` shows a write from a worktree upgrading setup without installing the extension

## Plan

1. Add black-box regression coverage for `chitty init` and setup upgrades in a real linked worktree, first confirming the regression fails.
2. Add Git worktree detection that resolves Git directory paths and treats non-Git directories or unavailable Git as eligible for installation.
3. Gate the machine-wide Pi extension operations in linked worktrees, with a stderr explanation, while retaining ordinary setup writes.
4. Update the design rule and version only when generated setup changes, then format, run checks, and verify every criterion.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03, with `TASK-130`. Fixed: the subdirectory comparison bug, which it reproduced in a scratch repository; failure handling outside Git; skipping the two other machine-wide steps; reporting the skip; and the rollout and version bump. Test hints: `tests/support.py` points `HOME` at a directory that does not exist, so create `PI_CODING_AGENT_DIR`; `test_cli.py:158-190` shows a real worktree. Rejected: its finding that `TASK-126`'s claim would leak worktree code. The source is the running code's package data, and `chitty run` runs the global `main` code, so a claim installs `main`'s extension. Branch code running as `.venv/bin/chitty` is the leak. A main checkout on another branch still installing, because the rule is about checkouts. Submodules, because their two directories match. `TASK-129` is ordered first after `TASK-126` by adding it as a dependency to the others.

Landing moved from `TASK-120` to `TASK-131`, so read references to that step accordingly.

Default recorded for review: non-Git directories and systems without `git` remain eligible to install the extension. This preserves existing `chitty init` behaviour outside Git and is specified in the ticket; the implementation will document the default at the detection boundary.

Verified all criteria with `make check`: the real-worktree test first failed on the missing skip message, then now confirms skipped validation, settings cleanup, extension installation, and stale autocommit setup upgrades; the subdirectory and outside-Git test confirms installation remains enabled. `PLAN.md` records the rule and `__version__` is `0.1.22` because `init` now emits linked-worktree setup output.

Ready for independent review. Re-checked every acceptance criterion after the final code commit with `make check`; the working tree is clean and `git diff --check main...HEAD` passes.

Reviewed: all five acceptance criteria independently passed; uv run ruff format --check .
183 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run python -m unittest discover -s tests -t .
[ticket 09920ba] worker change
 1 file changed, 1 insertion(+), 1 deletion(-) passed (215 tests), and  passed.

## History

- 2026-11-03T20:41:13Z lively-panda → todo
- 2026-11-03T20:44:52Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T20:46:22Z lively-panda: changed notes
- 2026-11-03T21:04:30Z kind-marten: changed notes; wrote the plan
- 2026-11-03T21:04:30Z kind-marten todo → doing
- 2026-11-03T21:10:29Z kind-marten: changed notes; ticked acceptance criteria
- 2026-11-03T21:11:59Z kind-marten: changed notes
- 2026-11-03T21:11:59Z kind-marten doing → review
- 2026-11-03T21:18:50Z daring-gecko: changed notes
- 2026-11-03T21:18:50Z daring-gecko review → done
