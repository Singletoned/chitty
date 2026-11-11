---
title: Apply every `--replace-in-description`, not just the last
status: backlog
labels:
  - bug
parent: TASK-284
created: 2026-11-11
---

## Description

- `chitty edit` keeps only the last of several `--replace-in-description OLD NEW` options, silently (`src/chitty/cli.py:599`; `Edit.replace_in_description` in `src/chitty/store.py` holds one pair). The planner lost an edit this way on 2026-11-11.
- Make the option repeatable (`multiple=True`) and apply each pair in order, each to the result of the one before, with the existing checks (empty OLD, OLD not found, combined with `--description`) applied to every pair. The MCP `edit` tool (`src/chitty/mcp.py`) takes a list of pairs too.

## Acceptance Criteria

- [ ] A test: `chitty edit` with two `--replace-in-description` options changes both parts of the Description. It fails today.
- [ ] If any OLD does not occur exactly once in the Description as the earlier pairs leave it, the edit fails naming that OLD and changes nothing.

## History

- 2026-11-11T21:10:11Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:18Z vivid-yellow-raven: changed acceptance criteria
