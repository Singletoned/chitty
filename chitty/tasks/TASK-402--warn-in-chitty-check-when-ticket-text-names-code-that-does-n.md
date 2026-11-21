---
title: Warn in `chitty check` when ticket text names code that does not exist
status: planning
labels:
  - question
created: 2026-11-18
---

## Description

Planners write claims about code from memory: in the 2026-11-18 ticket-state planning, cold reads spent rounds on a nonexistent `chitty restore` command, wrong test classes and similar (see `docs/plan/pipeline-and-feedback.md`, Cold read). The plan guide now says to run `chitty check` before a cold read. Proposal: warn when a backticked repository path in a ticket does not exist, and perhaps when a backticked identifier appears nowhere in the tracked files. Needs planning: which tokens count, how to avoid noise from paths a ticket will create, and whether the check runs on `main` or the ticket branch.

## Notes

The description leaves three blocking design questions open: which backticked tokens count as code identifiers versus prose/commands; how to avoid flagging valid paths or identifiers a ticket intends to create; and whether lookup uses the current ticket branch, main, or both. The requested warning cannot be implemented or tested consistently until these are decided. In particular, a main-only lookup would miss names introduced on an active branch, while branch-only lookup could regard branch-specific work as valid; proposed paths need an explicit rule. Planner: define token/path recognition and exclusions, baseline semantics, and user-visible severity/failure behavior, then add verifiable acceptance criteria.

Question for the owner (2026-11-21, overnight planner): the worker's blockers above are policy choices, so they were not settled overnight. Proposal to confirm or change: (1) only backticked spans that look like a repository path (contain `/` or end in a known source extension) or a `file.py:symbol`/`module.function` reference count; (2) check them against the tree of the checkout running `chitty check` (the ticket branch in a worktree, `main` in the main checkout), so names a branch adds are found; (3) a warning, never an error, and skipped for tickets that are `done` or archived. Is this worth building, and are these the right rules?

## History

- 2026-11-18T20:24:11Z lively-quartz-crane → todo
- 2026-11-18T23:24:21Z friendly-indigo-wren todo → doing
- 2026-11-18T23:25:30Z friendly-indigo-wren: changed owner, notes
- 2026-11-18T23:25:30Z friendly-indigo-wren doing → planning
- 2026-11-21T23:23:08Z lively-zinc-newt: changed labels, notes
