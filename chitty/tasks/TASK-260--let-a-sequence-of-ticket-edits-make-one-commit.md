---
title: Let a sequence of ticket edits make one commit
status: backlog
labels:
  - needs-discussion
created: 2026-11-11
---

## Description

- Backlog triage on 2026-11-11 cleared `parent: TASK-106` on about 60 tickets with one `chitty edit` each. Autocommit made one commit per edit, about 60 commits for one logical change.
- `chitty edit` takes one ID, so a loop is the only way to apply one change to many tickets.
- Possible fixes: a bulk command, for example `chitty edit` taking several IDs or a filter; or a way to turn autocommit off for a sequence of commands and commit once at the end.
- Related: TASK-245 (edits slow while cold reads run); fewer commits may help there too.

## History

- 2026-11-11T10:37:05Z vivid-yellowhammer → backlog
