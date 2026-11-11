---
title: Accept ticket IDs with a lowercase alphanumeric suffix
status: backlog
parent: TASK-262
created: 2026-11-11
---

## Description

- `src/chitty/ids.py` accepts `PREFIX-N` (`TaskId.number` is an `int`). Also accept a lowercase alphanumeric suffix with at least one letter, for example `BACKLOG-k3f9x2ab`, in IDs, filenames, references and `chitty show`/`edit`.
- Sorting: numeric IDs sort as today; alphanumeric ones after them, by suffix.
- Nothing generates these yet.

## History

- 2026-11-11T11:35:12Z vivid-yellowhammer → backlog
