---
title: Warn in `chitty check` when ticket text names code that does not exist
status: todo
created: 2026-11-18
---

## Description

Planners write claims about code from memory: in the 2026-11-18 ticket-state planning, cold reads spent rounds on a nonexistent `chitty restore` command, wrong test classes and similar (see `docs/plan/pipeline-and-feedback.md`, Cold read). The plan guide now says to run `chitty check` before a cold read. Proposal: warn when a backticked repository path in a ticket does not exist, and perhaps when a backticked identifier appears nowhere in the tracked files. Needs planning: which tokens count, how to avoid noise from paths a ticket will create, and whether the check runs on `main` or the ticket branch.

## History

- 2026-11-18T20:24:11Z lively-quartz-crane → todo
