---
title: Let `chitty run` switch agent with `--agent`
status: doing
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
claude = "claude -p {prompt} --model sonnet --permission-mode dontAsk --allowedTools 'Read Edit Write Bash(chitty *) Bash(git *) Bash(make *) Bash(uv run *) Bash(python *) Bash(npm test*) Bash(rg *) Bash(head *) Bash(grep *) Bash(find *) Bash(sort *) Bash(tail *) Bash(sed *) Bash(nl *) Bash(awk *) Bash(cat *) Bash(ls *) Bash(wc *)' --disallowedTools 'Bash(git push *)'"
```

`chitty run --agent claude` uses that entry for this run only. Declare it as a Click option on `run`, so it is not forwarded to the agent while other arguments still are; `TASK-138` adds `--ticket` the same way, and whichever lands second rebases. Check it where `agent_command` is checked today, in `_agent_command`, after the inbox pull and setup refresh and before the claim. The chosen command gets the same validation at that point, with messages naming the setting, such as `agent_commands.claude`. A name not in the table, or any name when there is no table, is an error listing the names there. With `--agent`, `agent_command` may be unset, because only the chosen command is needed.

`[agent_commands]` must follow every top-level key in `chitty.toml`, because a table takes the keys after it. This repository sets the entry above, with the same `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync` prefix as its `agent_command`.

Out of scope: switching automatically when tokens run out.

## Acceptance Criteria

- [x] Tests show an unknown name failing with the available names, and an invalid entry failing like `agent_command`, with no claim and no worktree
- [x] `README.md` and `PLAN.md` describe the table, this repository sets the `claude` entry, and `__version__` is bumped above `main`'s
- [ ] Tests with fake agents show `--agent` starting that command for one run, with other arguments forwarded and the option not, and the default used without it

## Plan

1. Extend configuration parsing and init templates with an optional [agent_commands] table, preserving agent_command as the default.
2. Add run --agent as a Click-only option and select/validate the chosen command after setup refresh and inbox pull, before claiming; preserve forwarding of all other arguments.
3. Add focused fake-agent tests for selection, forwarding, defaults, and validation/no side effects; update README.md, PLAN.md, repository config, and version.
4. Run the regression test first where practical, then make format/check, tick verified criteria, run chitty fix, record summary, and set review.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: "before anything changes", which is false because validation follows the pull and refresh, so it now says where; `--agent` with `agent_command` unset; no table; messages naming the entry; and where the table goes in the file. Rejected: depending on `TASK-138`, because one ticket is in work at a time and the second rebases; an `agent` field in the usage log, because `models` already shows provider and model, and can be added if the comparison needs it; validating names, because any TOML key works and an unknown one fails.

Changed 2026-11-04: the human chose an allow-list built from the command table on `TASK-155`, in place of `--dangerously-skip-permissions`.

## History

- 2026-11-04T17:58:11Z mellow-newt → backlog
- 2026-11-04T18:01:13Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T18:01:13Z mellow-newt backlog → todo
- 2026-11-04T20:32:38Z mellow-newt: changed description, notes
- 2026-11-05T10:07:34Z mellow-newt: changed description
- 2026-11-05T10:23:45Z mellow-newt: changed description
- 2026-11-05T17:00:07Z open-eel todo → doing
- 2026-11-05T17:00:24Z open-eel: wrote the plan
- 2026-11-05T17:12:59Z open-eel: ticked acceptance criteria
- 2026-11-05T17:13:00Z open-eel: ticked acceptance criteria
