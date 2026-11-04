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
agent_command = "claude -p {prompt} --model sonnet --permission-mode dontAsk --allowedTools 'Read Edit Write Bash(chitty *) Bash(git *) Bash(make *) Bash(npm *) Bash(uv *)' --disallowedTools 'Bash(git push *)'"
```

Use `-p`: an interactive session stays open after the agent finishes, and `chitty run` waits for it to exit. `sonnet` is the CLI's alias, so it follows the current Sonnet. `{prompt}` comes first because `--allowedTools` takes several values and would otherwise swallow it. A `-p` session cannot ask a person, so `dontAsk` denies whatever the list omits, and a denial should appear in the session rather than stalling it. Tune the list in the trial and record what changed. Not yet decided: the human chooses between this and `--dangerously-skip-permissions` before this ticket goes to `todo`.

`claude` reads `CLAUDE.md`, a symlink to `AGENTS.md`, so it gets the repository's instructions. Unlike Pi, nothing continues a stopped session: if it stops without changing the ticket, `chitty run` exits non-zero, and running it again resumes in a fresh session. See how often this happens before building anything, so `TASK-89`'s loop may not be needed. `requireLinkedWorktree` is only in the Pi extension, so it does not apply here, but `chitty run` has already chosen the worktree.

Try it on a small real ticket, for both work and review, in this repository, from an ordinary shell. Also check, and record: whether `claude` refuses to start or behaves differently inside a Claude Code session, since `run` removes `CLAUDE_CODE_SESSION_ID` but not `CLAUDECODE`; whether `-p` with an inherited stdin that is not a terminal blocks; and that the session really used Sonnet. Record what the session did, what it cost if shown, and anything that needed fixing. Say in `README.md` how to use it. Whether this repository then stays on `claude` is for the human.

Out of scope: writing `CHITTY_USAGE_FILE` from `claude`, so the usage log shows `models` null for these sessions; `chitty init` installing anything for Claude Code; and `TASK-89`'s `/chitty` command.

## Acceptance Criteria

- [ ] A real ticket is worked and then reviewed through `chitty run` with `claude` on Sonnet, and a note records the commands, the outcome and anything fixed
- [ ] `README.md` shows the `agent_command` for `claude`, including the permission mode and why

## Notes

Same cold read as `TASK-154`. Fixed: the allow-list as a third option, which my text missed; `{prompt}` before `--allowedTools`, which takes several values, found while checking `claude --help`; `git push` denied; and the trial now covers a nested session, inherited stdin and the model. Rejected: a criterion for an early stop exiting non-zero, because the code does it and existing tests cover it. Which ticket to try, which is the trial's choice. Stays in `backlog` until the human decides on permissions.

## History

- 2026-11-04T15:38:29Z mellow-newt → backlog
- 2026-11-04T15:40:08Z mellow-newt: changed description, notes
