---
title: Read tickets with any prefix from every directory under `chitty/`
status: cold-read
parent: TASK-262
created: 2026-11-11
---

## Description

- Today Chitty finds tickets only in configured contexts. Read every directory under `chitty/` (and its `archive/`), whatever the prefix, so `HUMAN-` and `BACKLOG-` tickets keep working once contexts are removed.
- References, `depends_on` and `chitty show` work with any prefix.

## Acceptance Criteria

- [ ] A test writes `chitty/other/OTHER-1--x.md` and `chitty/other/archive/OTHER-2--y.md`, with no `other` context in `chitty.toml`. `chitty show OTHER-1` and `chitty show OTHER-2` work, and `chitty list` includes `OTHER-1`. It fails today.
- [ ] A ticket can name `OTHER-1` in `depends_on`, and `chitty check` reports no problem.

## History

- 2026-11-11T11:35:15Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:48Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:54Z vivid-yellowhammer backlog → cold-read
