---
title: Accept an optional `due` date in ticket frontmatter
status: backlog
parent: TASK-619
created: 2026-11-23
---

## Description

Add an optional `due` key to ticket frontmatter (`Frontmatter` in `src/chitty/model.py`): an ISO 8601 date, written unquoted like `created`. `chitty check` accepts a valid date and reports a malformed one with a clear message naming the file and the value. A ticket with `due` round-trips through the pinned prettier and mdformat formatter tests unchanged. Existing tickets without `due` are unaffected.

## History

- 2026-11-23T10:39:46Z witty-russet-gannet → backlog
