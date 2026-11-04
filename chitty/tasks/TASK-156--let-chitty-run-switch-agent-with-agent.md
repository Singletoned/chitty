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

`chitty run --agent claude` uses that entry for this run only. Declare it as a Click option on `run`, so it is not forwarded to the agent while other arguments still are; `TASK-138` adds `--ticket` the same way, and whichever lands second rebases. Check it where `agent_command` is checked today, in `_agent_command`, after the inbox pull and setup refresh and before the claim. The chosen command gets the same validation at that point, with messages naming the setting, such as `agent_commands.claude`. A name not in the table, or any name when there is no table, is an error listing the names there. With `--agent`, `agent_command` may be unset, because only the chosen command is needed.

`[agent_commands]` must follow every top-level key in `chitty.toml`, because a table takes the keys after it. This repository sets the entry above, with the same `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync` prefix as its `agent_command`.

Out of scope: switching automatically when tokens run out.

## Acceptance Criteria

- [ ] Tests show an unknown name failing with the available names, and an invalid entry failing like `agent_command`, with no claim and no worktree
- [ ] `README.md` and `PLAN.md` describe the table, this repository sets the `claude` entry, and `__version__` is bumped above `main`'s
- [ ] Tests with fake agents show `--agent` starting that command for one run, with other arguments forwarded and the option not, and the default used without it

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: "before anything changes", which is false because validation follows the pull and refresh, so it now says where; `--agent` with `agent_command` unset; no table; messages naming the entry; and where the table goes in the file. Rejected: depending on `TASK-138`, because one ticket is in work at a time and the second rebases; an `agent` field in the usage log, because `models` already shows provider and model, and can be added if the comparison needs it; validating names, because any TOML key works and an unknown one fails.

## History

- 2026-11-04T17:58:11Z mellow-newt → backlog
- 2026-11-04T18:01:13Z mellow-newt: changed description, acceptance criteria, notes
