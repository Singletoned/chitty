---
title: Shrink Chitty's block in `AGENTS.md`
status: review
priority: medium
depends_on:
  - TASK-142
  - TASK-144
parent: TASK-140
created: 2026-11-04
---

## Description

Third of three parts of `TASK-140`. `AGENTS.md` belongs to the repository, so reduce Chitty's block there to what every session needs, now that each role has its own instructions.

Rewrite `src/chitty/guide.md` to about ten lines: tasks live in `chitty/`; use the CLI or MCP and do not hand-edit task files; backticks for paths and code; `chitty --help` for commands; and which `chitty guide <role>` to run, for a person who starts an agent by hand, keeping the pointer to `chitty guide plan` from `TASK-187`. `TASK-141` has already given every other rule a home and accounted for them in a note: check that against the final text.

`chitty init` already replaces the block, so existing repositories pick this up through the version bump. `TASK-144` makes that replacement exact. Run it here so this repository's `AGENTS.md` matches. In this repository's own section, replace the cold-read pointer with `chitty guide plan`, and drop anything the block no longer needs.

Out of scope: the rest of a repository's `AGENTS.md`, which Chitty does not own.

## Acceptance Criteria

- [x] This repository's `AGENTS.md` matches and its cold-read line names `chitty guide plan`, and `__version__` is bumped above `main`'s
- [x] `README.md` and `PLAN.md` describe where instructions live
- [x] `src/chitty/guide.md` is about ten lines and names `chitty guide <role>`, and every rule removed appears in the `TASK-141` accounting
- [x] A test shows `chitty init` replacing the old long block in an existing repository with the new one

## Plan

Update the managed guide template and this repository's instructions to the concise role-oriented block, preserving the strict-marker format. Bump the package patch version, add or adjust the init regression coverage for replacing legacy blocks, update README/PLAN instruction pointers, then run formatting and the full check suite.

## Notes

Same cold read. Fixed: the blank line consumed before a following section, which would have failed the old criterion 2, confirmed by reading the code at `init_repo`; `re.subn` treating the guide as a template; and exactly one `## ` line. Rule accounting moved to `TASK-141`, which writes the role files. Rejected: an end marker for the block, because it adds format for every repository to protect text after the block that nobody has reported. Raised with the human as a question, since that text is replaced today.

Changed 2026-11-04: the human decided the block should have strict markers, in `TASK-144`. That replaces the blank-line, template and single-heading fixes this ticket had taken from its cold read, and the end-marker rejection in that note no longer stands.

Implemented the concise managed guide, refreshed this repository with updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty.toml
updated /Users/singletoned/.local/share/chitty/inbox/chitty
updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/AGENTS.md, and verified legacy-block replacement. The version is 0.1.39 because the version-bump check reported main at 0.1.38 despite the branch ref showing 0.1.37;  was left unchanged per repository instructions.

## Summary

Handoff:  now contains the concise pointer block; , , and  document the role-guide split; init regression coverage verifies replacing a legacy block; version bumped to 0.1.39. Verification: focused init/guide tests, uv run ruff check --exit-zero .
All checks passed!
uv run ruff format .
296 files left unchanged, uv run python scripts/check_version_bump.py
uv run ruff format --check .
296 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Deleted branch task-1 (was a9b8968).
Deleted branch task-1 (was 3a7eaf5).
Deleted branch task-2 (was d1e0319).
npm test

> test
> node --experimental-strip-types --test-reporter=dot --test src/chitty/integrations/pi/tests/chitty.test.ts

....................
......, /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-144--mark-chitty-s-block-in-agents-md-with-strict-begin-and-end-c.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-148--log-usage-for-failed-and-interrupted-runs.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-169--find-what-leaves-temporary-projects-in-the-real-inbox.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-177--count-other-branches-tickets-when-allocating-an-id.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-191--keep-tickets-in-random-id-contexts-in-backlog.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-199--exit-3-when-chitty-next-or-chitty-run-has-no-ticket.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-72--show-status-glyphs-and-why-chitty-next-skips-a-ticket-in-chi.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-1--reject-setext-headings-in-task-bodies.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-15--add-bash-and-zsh-completion.md: warning: Description contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-178--stop-chitty-run-from-a-ticket-worktree-changing-main-s-setup.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Summary contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-45--write-chitty-toml-inline-comments-with-a-single-space.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-47--guide-tells-agents-to-put-paths-globs-and-code-in-backticks.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-49--warn-in-chitty-check-when-task-text-has-markdown-characters.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-56--remove-prefix-from-chitty-init-prefixes-name-queues-not-proj.md: warning: Acceptance Criteria #2 contains literal '*' Markdown delimiter; use backticks for code, and /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-144--mark-chitty-s-block-in-agents-md-with-strict-begin-and-end-c.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-148--log-usage-for-failed-and-interrupted-runs.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-169--find-what-leaves-temporary-projects-in-the-real-inbox.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-177--count-other-branches-tickets-when-allocating-an-id.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-191--keep-tickets-in-random-id-contexts-in-backlog.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-199--exit-3-when-chitty-next-or-chitty-run-has-no-ticket.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/TASK-72--show-status-glyphs-and-why-chitty-next-skips-a-ticket-in-chi.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-1--reject-setext-headings-in-task-bodies.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-15--add-bash-and-zsh-completion.md: warning: Description contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-178--stop-chitty-run-from-a-ticket-worktree-changing-main-s-setup.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Summary contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-45--write-chitty-toml-inline-comments-with-a-single-space.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-47--guide-tells-agents-to-put-paths-globs-and-code-in-backticks.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-49--warn-in-chitty-check-when-task-text-has-markdown-characters.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty/tasks/archive/TASK-56--remove-prefix-from-chitty-init-prefixes-name-queues-not-proj.md: warning: Acceptance Criteria #2 contains literal '*' Markdown delimiter; use backticks for code (warnings only for pre-existing ticket Markdown).

## History

- 2026-11-04T11:56:20Z lively-panda → todo
- 2026-11-04T12:00:40Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T12:32:19Z lively-panda: changed dependencies, description, acceptance criteria, notes
- 2026-11-05T14:23:17Z mellow-newt: changed description
- 2026-11-06T20:15:30Z open-urchin todo → doing
- 2026-11-06T20:15:48Z open-urchin: wrote the plan
- 2026-11-06T20:22:51Z open-urchin: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:22:51Z open-urchin doing → review
