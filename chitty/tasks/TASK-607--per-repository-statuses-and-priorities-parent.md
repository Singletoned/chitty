---
title: Per-repository statuses and priorities (parent)
status: backlog
created: 2026-11-23
---

## Description

Parent for configurable statuses and priorities. Requested from a personal todo repository (2026-11-23), which needs statuses `open`, `waiting`, `done`, `dropped` (maybe `someday`) and priorities as time horizons (`now`, `soon`, `later`, `someday`) rather than `low`/`medium`/`high`. `docs/plan/non-goals.md` lists "Configurable statuses"; the person said (2026-11-23) to reconsider that and to build both, priorities included.

Proposal from the suggestion: `chitty.toml` declares the vocabulary, for example `statuses = ["open", "waiting", "done", "dropped"]` and `priorities = ["now", "soon", "later", "someday"]` (highest first), with today's values as the default so existing repositories are unchanged.

Children: configurable priorities (two tickets, no design decision needed); a design ticket that settles the status rules with the person; then status tickets that depend on it. Related: TASK-599 (`dropped` status) and TASK-601.

## Notes

Suggestion origin: /Users/singletoned/src/singletoned/todo

Decided with the person, 2026-11-23: `priorities` is an ordered list, highest first, in which `""` marks where tickets with no priority rank (default `["high", "medium", "", "low"]`). Named sets, such as t-shirt sizes, may come later as shorthand for a list. The same approach (a list that defines the order) is a likely model for statuses in TASK-634.

## History

- 2026-11-23T10:23:57Z witty-russet-gannet → backlog
- 2026-11-23T10:23:59Z witty-russet-gannet: changed notes
- 2026-11-23T10:40:37Z witty-russet-gannet: changed title, description
- 2026-11-23T12:39:09Z witty-russet-gannet: changed notes
