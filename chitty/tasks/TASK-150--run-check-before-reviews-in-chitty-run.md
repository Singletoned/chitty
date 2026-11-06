---
title: Run `check` before reviews in `chitty run`
status: doing
priority: high
depends_on:
  - TASK-120
parent: TASK-106
created: 2026-11-04
---

## Description

Second part of `TASK-120`, which rebases a ticket before its review. Add a `check` command, so no review is spent on work that cannot pass.

Add `check` to `chitty.toml`, with no default for the same reason as `setup`, parsed without a shell like `setup`, and read from the main checkout's config. Unset is a loud error in the `chitty run` preflight, in every mode, so a repository finds out before work starts. Set `check = "make check"` in this repository. `make check` already runs the Node tests. Existing repositories get it only as a commented example, as `setup` does.

Run it in the ticket's worktree after `TASK-120`'s rebase and `setup`. Capture stdout and stderr together with stdin at `DEVNULL`, printing a line first because the output is not shown live. On failure, move the ticket to `doing` with `Review failed (work): ...` and the last 20 lines of output, through `Repo.edit` so it counts towards the failure limit, and do not start the agent. `chitty run` exits 0 because the status changed. Ctrl-C exits 130.

Existing `chitty run` tests will need `check` in their configuration.

Out of scope: a timeout, and landing.

## Acceptance Criteria

- [x] Tests show a failing `check` not starting the agent and moving the ticket to `doing` with the last 20 lines, and a passing one starting it
- [x] Tests show a quoted argument parsed without a shell, an unset `check` failing before anything changes, and `chitty init` adding it only as a comment
- [ ] This repository sets `check`, `PLAN.md`, `README.md` and the template describe it, and `__version__` is bumped above `main`'s

## Plan

Inspect the runner, config, init templates, docs, and existing tests; add strict check configuration and preflight execution after rebase/setup, covering output and status handling; update repository docs/version and verify with focused tests plus make check.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: how output is captured, and the effect on existing tests.

Under `TASK-212`, a branch may not change `chitty.toml`. Setting `check = "make check"` in this repository is done on the main checkout by a human-run session after this lands, not on the branch.

The check progress line is written to stderr so existing status output remains machine-friendly; check output itself is captured and included only on failure. Repository chitty.toml was intentionally not changed because TASK-212 notes require that main-checkout setting to land in a human session.

Review failed (integration): rebasing onto `main` conflicts in `src/chitty/__init__.py`.

Resolved the review rebase conflict in src/chitty/__init__.py by retaining 0.1.37, which remains above main's 0.1.36.

Review failed (integration): the repository's root chitty.toml does not set check = "make check"; neither this branch nor main contains that setting, so acceptance criterion 3 is unmet. make format && make check passed (336 tests plus Node tests).

1: pass - Regression tests cover failing and passing check behavior.

2: pass - Tests cover shell-free quoting, unset preflight configuration, and commented init output.

3: fail - The repository configuration does not set check = "make check".

## Summary

Implemented and verified `check` preflight support. Checks now run after setup and before work-ticket claims, parse commands without a shell, capture combined output, record the last 20 lines on failure, and prevent agent startup. Added regression coverage for failure output, quoted arguments, unset preflight config, and init comments. Rebased onto main and resolved the version bump conflict. Verification: make check (ruff, pyright, 337 unittest tests, Node tests).

## History

- 2026-11-04T15:11:33Z mellow-newt → todo
- 2026-11-04T15:17:36Z mellow-newt: changed description, notes
- 2026-11-06T16:24:13Z youthful-toad: changed priority
- 2026-11-06T16:44:17Z youthful-toad: changed notes
- 2026-11-06T18:30:21Z witty-gannet todo → doing
- 2026-11-06T18:30:36Z witty-gannet: wrote the plan
- 2026-11-06T18:50:06Z witty-gannet: changed notes
- 2026-11-06T18:50:07Z witty-gannet: ticked acceptance criteria
- 2026-11-06T18:50:08Z witty-gannet: changed summary
- 2026-11-06T18:50:08Z witty-gannet doing → review
- 2026-11-06T19:01:25Z brisk-lapwing: changed notes
- 2026-11-06T19:01:25Z brisk-lapwing review → doing
- 2026-11-06T19:41:35Z able-yellowhammer: changed notes, summary
- 2026-11-06T19:41:35Z able-yellowhammer doing → review
- 2026-11-06T19:41:47Z able-yellowhammer: changed summary
- 2026-11-06T19:47:57Z tidy-badger: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-06T19:47:57Z tidy-badger review → doing
