---
title: Refuse ticket branches that change `AGENTS.md`'s managed block
status: doing
priority: high
depends_on:
  - TASK-212
created: 2026-11-06
---

## Description

Only `chitty init` on the main checkout writes Chitty's managed block in `AGENTS.md` (the human's decision, 2026-11-06), just as only it writes `chitty.toml` (`TASK-212`). In the same `_prepare_review` check in `src/chitty/run.py` that `TASK-212` adds, fail the ticket if the branch changes the managed block compared with `main`. Use the note `Review failed (work): the branch changes Chitty's managed block in `AGENTS.md`; only `chitty init` on the main checkout may change it. Restore that block from `main`.`.

- **The block.** It is the text from the `GUIDE_BEGIN` line to the `GUIDE_END` line (`src/chitty/store.py`). A file without markers uses the legacy `## Chitty` section. Factor the lookup out of `_managed_agents` into a public `managed_block`, so both use one function. Read file contents at a ref with a new `git.file_at(root, ref, path)`.
- **Allowed.** Edits to the rest of `AGENTS.md` are allowed.
- **Edge cases.**
  - Broken markers on the branch count as a change.
  - `AGENTS.md`, or its block, present on only one side counts as a change.
  - Absent on both sides is no change.
  - A rebase conflict in `AGENTS.md` already fails as `integration`.
- **Tests.** `chitty run` refreshes `AGENTS.md` on the main checkout before the rebase, so a test fixture's block must be the real `guide()` text, or the rebase conflicts for the wrong reason. Assert the exact note. Test the legacy-section lookup through `managed_block` directly.
- **This repository.** A branch that changes `src/chitty/guide.md` leaves `AGENTS.md` alone; the main checkout's setup refresh regenerates it after landing. `task-179` and `task-181` edit the block today and must restore it before they can pass.

Out of scope: `CLAUDE.md`, which is a symlink here.

## Acceptance Criteria

- [x] Tests show a branch that edits inside the managed block failing review with that note and no agent run, and a branch that edits only outside it passing.
- [x] A unit test of `managed_block` covers marked and legacy files, and `_managed_agents` uses it with its behaviour unchanged (existing `init` tests pass).

## Plan

Add git.file_at to read a committed path at a ref, and factor store.managed_block so marked and legacy AGENTS.md content is normalized through one public lookup. Extend review preparation to compare the branch and main managed blocks after rebase, failing with the exact ticket note before setup or agent execution when they differ. Add unit coverage for marked/legacy lookup and review coverage for inside-block rejection and outside-block allowance, using the real guide text in fixtures. Run the focused tests, then make format and check.

## Notes

Verified with make check: 340 Python tests and Node tests pass. /Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-144--mark-chitty-s-block-in-agents-md-with-strict-begin-and-end-c.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-148--log-usage-for-failed-and-interrupted-runs.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-169--find-what-leaves-temporary-projects-in-the-real-inbox.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-177--count-other-branches-tickets-when-allocating-an-id.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-191--keep-tickets-in-random-id-contexts-in-backlog.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-199--exit-3-when-chitty-next-or-chitty-run-has-no-ticket.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/TASK-72--show-status-glyphs-and-why-chitty-next-skips-a-ticket-in-chi.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-1--reject-setext-headings-in-task-bodies.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-15--add-bash-and-zsh-completion.md: warning: Description contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-178--stop-chitty-run-from-a-ticket-worktree-changing-main-s-setup.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Summary contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-45--write-chitty-toml-inline-comments-with-a-single-space.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-47--guide-tells-agents-to-put-paths-globs-and-code-in-backticks.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-49--warn-in-chitty-check-when-task-text-has-markdown-characters.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-218/chitty/tasks/archive/TASK-56--remove-prefix-from-chitty-init-prefixes-name-queues-not-proj.md: warning: Acceptance Criteria #2 contains literal '*' Markdown delimiter; use backticks for code completed with pre-existing Markdown delimiter warnings in unrelated tickets.

Verification note: make check passed; the fix command reported only pre-existing Markdown delimiter warnings in unrelated tickets.

Review failed (work): _changed_agents_block treats an AGENTS.md file present only on the branch as unchanged when main has no AGENTS.md (or no managed block). A branch containing only outside text returns False, violating the required one-sided-file edge case. Compare file presence/block presence separately and add regression coverage; restore criterion 1 after verification.
1: fail - one-sided AGENTS.md presence is not detected
2: pass - managed_block and _managed_agents coverage is present

Regression test failed before the fix: a branch-only AGENTS.md containing only outside text was incorrectly treated as unchanged. The comparison now checks file presence before managed-block content. Focused review tests and full make check pass; chitty fix reported only pre-existing Markdown delimiter warnings in unrelated task files.

Review failed (integration): rebasing onto `main` conflicts in `src/chitty/git.py`.

## Summary

Fixed one-sided AGENTS.md detection in _changed_agents_block and added regression coverage. Verification: focused tests, make format, make check, and chitty fix passed. Commit 854991d includes Task: TASK-218.

## History

- 2026-11-06T18:13:06Z youthful-toad → backlog
- 2026-11-06T18:13:30Z youthful-toad backlog → todo
- 2026-11-06T20:03:40Z eager-crane todo → doing
- 2026-11-06T20:04:20Z eager-crane: wrote the plan
- 2026-11-06T20:12:21Z eager-crane: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:12:21Z eager-crane doing → review
- 2026-11-06T20:12:37Z eager-crane: changed notes
- 2026-11-06T20:15:23Z nimble-otter: changed acceptance criteria, notes
- 2026-11-06T20:15:23Z nimble-otter review → doing
- 2026-11-06T20:21:23Z lively-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:21:23Z lively-adder doing → review
- 2026-11-06T20:23:12Z rosy-ibis: changed notes
- 2026-11-06T20:23:12Z rosy-ibis review → doing
