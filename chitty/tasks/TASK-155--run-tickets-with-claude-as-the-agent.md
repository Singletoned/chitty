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
agent_command = "claude -p {prompt} --model sonnet --dangerously-skip-permissions --disallowedTools 'Bash(git push *)'"
```

Use `-p`: an interactive session stays open after the agent finishes, and `chitty run` waits for it to exit. `sonnet` is the CLI's alias, so it follows the current Sonnet. `{prompt}` comes first because `--disallowedTools` takes several values and would otherwise swallow it. A `-p` session cannot ask a person. The human decided on 2026-11-04 to be permissive: an agent with write access and `Bash(make *)` can already do anything, so an allow-list would give no real containment, and a container is the answer if that is ever needed. `git push` stays denied as a guard against accidents, not a boundary, because pushing needs a person's request; the trial checks that the denial still applies alongside `--dangerously-skip-permissions`, and drops it if not, recording that. This repository also starts the agent through `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync`, as its current `agent_command` does, so `chitty` is the branch's own; the trial uses that prefix, and `README.md` shows the command without it.

`claude` reads `CLAUDE.md`, a symlink to `AGENTS.md`, so it gets the repository's instructions. Unlike Pi, nothing continues a stopped session: if it stops without changing the ticket, `chitty run` exits non-zero, and running it again resumes in a fresh session. See how often this happens before building anything, so `TASK-89`'s loop may not be needed. `requireLinkedWorktree` is only in the Pi extension, so it does not apply here, but `chitty run` has already chosen the worktree.

Try it on a small real ticket, for both work and review, in this repository, from an ordinary shell. Also check, and record: whether `claude` refuses to start or behaves differently inside a Claude Code session, since `run` removes `CLAUDE_CODE_SESSION_ID` but not `CLAUDECODE`; whether `-p` with an inherited stdin that is not a terminal blocks; and that the session really used Sonnet. Record what the session did, what it cost if shown, and anything that needed fixing. Say in `README.md` how to use it. Whether this repository then stays on `claude` is for the human.

Out of scope: writing `CHITTY_USAGE_FILE` from `claude`, so the usage log shows `models` null for these sessions; `chitty init` installing anything for Claude Code; and `TASK-89`'s `/chitty` command.

## Acceptance Criteria

- [ ] A real ticket is worked and then reviewed through `chitty run` with `claude` on Sonnet, and a note records the commands, the outcome and anything fixed
- [ ] `README.md` shows the `agent_command` for `claude`, including the permission mode and why

## Notes

Same cold read as `TASK-154`. Fixed: the allow-list as a third option, which my text missed; `{prompt}` before `--allowedTools`, which takes several values, found while checking `claude --help`; `git push` denied; and the trial now covers a nested session, inherited stdin and the model. Rejected: a criterion for an early stop exiting non-zero, because the code does it and existing tests cover it. Which ticket to try, which is the trial's choice. Stays in `backlog` until the human decides on permissions.

The human decided permissions on 2026-11-04: permissive, replacing the allow-list, because write access plus `Bash(make *)` already allows anything; a container if that ever matters.

## History

- 2026-11-04T15:38:29Z mellow-newt → backlog
- 2026-11-04T15:40:08Z mellow-newt: changed description, notes
- 2026-11-04T17:32:42Z mellow-newt: changed description, notes
