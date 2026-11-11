---
title: Remove the hidden `claude-usage-hook`
status: backlog
depends_on:
  - TASK-277
parent: TASK-275
created: 2026-11-11
---

## Description

- After TASK-277 nothing sets `CHITTY_USAGE_FILE`, so `claude-usage-hook` (`src/chitty/cli.py`) and `src/chitty/integrations/claude/usage.py` never write. Delete them and `tests/test_claude_usage.py`, and any doc that mentions them.

## Acceptance Criteria

- [ ] `chitty claude-usage-hook` no longer exists, and `grep -rn CHITTY_USAGE_FILE src tests` finds only the Pi extension, which TASK-279 removes.

## History

- 2026-11-11T13:43:46Z vivid-yellowhammer → backlog
