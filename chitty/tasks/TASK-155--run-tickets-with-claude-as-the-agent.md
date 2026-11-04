---
title: Run tickets with `claude` as the agent
status: backlog
priority: high
depends_on:
  - TASK-142
  - TASK-154
parent: TASK-106
created: 2026-11-04
---

## Description

Requested by the human on 2026-11-04: use `claude` instead of `pi` to work on tickets, with a weaker model. Token efficiency is why agents may change, and `agent_command` from `TASK-136` and `{prompt}` from `TASK-142` should make this mostly configuration. This ticket proves it and fixes what that proof finds.

```toml
agent_command = "claude -p --model sonnet --permission-mode <mode> {prompt}"
```

Use `-p`: an interactive session stays open after the agent finishes, and `chitty run` waits for it to exit. `sonnet` is the CLI's alias, so it follows the current Sonnet. Open: which permission mode, because a `-p` session cannot ask a person. `--dangerously-skip-permissions` lets an agent do anything on this machine; the human decides before this ticket goes to `todo`.

`claude` reads `CLAUDE.md`, a symlink to `AGENTS.md`, so it gets the repository's instructions. Unlike Pi, nothing continues a stopped session: if it stops without changing the ticket, `chitty run` exits non-zero, and running it again resumes in a fresh session. See how often this happens before building anything, so `TASK-89`'s loop may not be needed. `requireLinkedWorktree` is only in the Pi extension, so it does not apply here, but `chitty run` has already chosen the worktree.

Try it on a small real ticket, for both work and review, in this repository. Record what the session did, what it cost if shown, and anything that needed fixing. Say in `README.md` how to use it. Whether this repository then stays on `claude` is for the human.

Out of scope: writing `CHITTY_USAGE_FILE` from `claude`, so the usage log shows `models` null for these sessions; `chitty init` installing anything for Claude Code; and `TASK-89`'s `/chitty` command.

## Acceptance Criteria

- [ ] A real ticket is worked and then reviewed through `chitty run` with `claude` on Sonnet, and a note records the commands, the outcome and anything fixed
- [ ] `README.md` shows the `agent_command` for `claude`, including the permission mode and why

## History

- 2026-11-04T15:38:29Z mellow-newt → backlog
