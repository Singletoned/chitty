---
title: "Number bankruptcy: start ticket numbering again"
status: backlog
created: 2026-11-26
provisional: true
---

## Description

The person, 2026-11-26: "need a number bankruptcy system where we start again". Ticket numbers grow without bound (this repository jumped to `TASK-10000` through a placeholder mention, TASK-YST8KG) and long numbers are harder to read and say.

Open questions for the person before planning:

1. What restarts. A: renumber the active (not `done`, not archived) tickets from 1 and leave `done` and archived tickets on their old numbers, which then clash. B: start a new prefix (for example `T2-1`), so old IDs stay unique and readable in Git history. C: renumber every ticket, archived too, from 1, rewriting references; old commit messages and other repositories' mentions then point at the wrong tickets.
2. What old references become: rewritten in ticket text, or recorded in `moved_from` only.

Planner's preference: B. It keeps every old ID unique, so commit messages, branch names (`task-<n>`) and other repositories' citations stay correct, and it needs no rewriting.

## History

- 2026-11-26T11:11:53Z calm-ochre-quail → backlog
