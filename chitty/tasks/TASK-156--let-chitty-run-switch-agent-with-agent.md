---
title: Let `chitty run` switch agent with `--agent`
status: backlog
priority: high
depends_on:
  - TASK-137
  - TASK-142
parent: TASK-106
created: 2026-11-04
---

## Description

The human decided on 2026-11-04: Pi stays the default because it is the most token efficient, and it must be easy to switch to `claude` when tokens run out. Today that would mean editing and committing `agent_command` on `main` and later reverting it.

Add a table of other commands beside `agent_command`, which stays the default:

```toml
[agent_commands]
claude = "claude -p {prompt} --model sonnet --dangerously-skip-permissions --disallowedTools 'Bash(git push *)'"
```

`chitty run --agent claude` uses that entry for this run only. Declare it as a Click option on `run`, as `TASK-138` does with `--ticket`, so it is not forwarded to the agent. The chosen command gets all the validation `agent_command` gets. A name not in the table is an error listing the names there, before anything changes.

This repository sets the entry above, with the same `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync` prefix as its `agent_command`.

Out of scope: switching automatically when tokens run out.

## Acceptance Criteria

- [ ] Tests with fake agents show `--agent` starting that command for one run, not forwarding the option, and the default used without it
- [ ] Tests show an unknown name failing with the available names, and an invalid entry failing like `agent_command`, with no claim and no worktree
- [ ] `README.md` and `PLAN.md` describe the table, this repository sets the `claude` entry, and `__version__` is bumped above `main`'s

## History

- 2026-11-04T17:58:11Z mellow-newt → backlog
