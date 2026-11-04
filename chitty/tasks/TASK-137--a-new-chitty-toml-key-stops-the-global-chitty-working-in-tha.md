---
title: A new `chitty.toml` key stops the global `chitty` working in that branch's worktree
status: backlog
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

`chitty run` reads the ticket's worktree with `main`'s code, through `Repo.open(worktree)`. If the branch adds a key to `chitty.toml`, that fails with `<key>: Extra inputs are not permitted`, so the branch cannot be reviewed, and a session cannot be reported when it ends. `TASK-136` hit this with `agent_command`, and `TASK-150` will with `check`. A person running a global `chitty show` in that worktree hits it too.

In `load_repo_config`, when the file's `chitty_version` is newer than the running code, ignore top-level keys the code does not know, and warn on stderr naming each key and saying to upgrade Chitty. Otherwise keep refusing, so a typo still fails loudly. A branch adding a key must already bump the version, so this covers the real case. Unknown keys in `[contexts.*]` still refuse, because no ticket has needed that.

Writes need nothing new: `_check_setup_version` already refuses them when the file is newer than the code, with a message naming the version, and that stays.

Agents are not this ticket's concern. This repository's `agent_command` already starts them through `uv run`, so their `chitty` is the worktree's own (commit `b58cac8`).

Out of scope: `chitty run` checking which `chitty` an agent will find, and upgrading anyone's installs.

## Acceptance Criteria

- [ ] Tests show a `chitty.toml` with an unknown top-level key loading with a warning naming it when its `chitty_version` is newer than the code, and refusing when the version is equal, older or absent
- [ ] A test shows `chitty run` reviewing a ticket whose branch adds a key and bumps the version, and reporting the status change

## Notes

Hit again 2026-11-04 on `TASK-136`: `chitty run` picked `review TASK-136`, ran `setup` in the worktree, then failed at `Repo.open(worktree)` with `agent_command: Extra inputs are not permitted`, before any claim or session. The worktree's own `.venv/bin/chitty run` cannot get round it, because `run` reads `agent_command` from the main checkout, which does not have it until the branch lands. Preferred option: warn about an unknown key when the file's `chitty_version` is newer than the running code, and keep refusing otherwise, so a typo still fails loudly. A branch adding a key already has to bump the version. `TASK-150` adds `check`, so it will hit this next.

Rewritten 2026-11-04: the human chose this fix. My earlier note was incomplete: warning alone does not let an agent write, because `_check_setup_version` refuses writes when the file is newer than the code. So agents get the branch's `chitty` from configuration instead, in commit `b58cac8`. That commit also answers the same error from a `TASK-141` session, where only `~/.envs/default/bin/chitty` of the three installs fails: it is 0.1.25, editable from `.worktrees/pi-token-analysis`. Why that session found it was not established.

## History

- 2026-11-04T09:46:24Z lively-panda → backlog
- 2026-11-04T17:03:09Z mellow-newt: changed notes
- 2026-11-04T17:32:41Z mellow-newt: changed priority, description, acceptance criteria, notes
