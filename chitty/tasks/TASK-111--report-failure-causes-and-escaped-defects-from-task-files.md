---
title: Report failure causes and escaped defects from task files
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-03
---

## Description

Retros need the causes and escapes described in `PLAN.md` without an agent re-reading every ticket. During the pilot these are conventions: `Review failed (<cause>): ...` notes, and a bug ticket with label `escape` and a note naming its source ticket. Decide from the first two retros whether they need structured fields, then add one small read-only report: first-pass yield, failures by cause, escapes, retries per ticket.

No new store: the data comes from task files, and `archive = "delete"` repositories need a stated answer, since deleting removes History.

## History

- 2026-11-03T10:27:48Z lively-panda → backlog
