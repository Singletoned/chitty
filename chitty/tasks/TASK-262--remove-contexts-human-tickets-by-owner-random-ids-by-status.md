---
title: "Remove contexts: human tickets by owner, random IDs by status"
status: backlog
labels:
  - needs-discussion
  - needs-minor
created: 2026-11-11
---

## Description

- Contexts serve two narrow uses. The human chose to replace both on 2026-11-11, and to remove contexts entirely.
- `human`: scrap it. A ticket for the human is `owner: human`. It needs review like any other; the human reviews it or forces it.
- Tickets created off `main` get a random ID with prefix `BACKLOG` and a lowercase alphanumeric suffix, clearly unlike a number, for example `BACKLOG-k3f9x2ab`. Tickets created on `main` get sequential IDs, whatever their status.
- A `BACKLOG-` ticket gets a sequential ID when it leaves `backlog`, in the main checkout only, normally during triage.
- No migration. Chitty stops creating old-style tickets, and existing `HUMAN-` and `BACKLOG-` tickets keep their IDs until they are archived. Any prefix must keep working.
- Children, smallest first; each is planned on its own.

## History

- 2026-11-11T11:24:46Z vivid-yellowhammer → backlog
- 2026-11-11T11:35:11Z vivid-yellowhammer: changed description
