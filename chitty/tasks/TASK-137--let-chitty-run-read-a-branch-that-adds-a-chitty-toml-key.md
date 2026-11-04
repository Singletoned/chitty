---
title: Let `chitty run` read a branch that adds a `chitty.toml` key
status: backlog
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

`chitty run` reads the ticket's worktree with `main`'s code, through `Repo.open(worktree)`. If the branch adds a key to `chitty.toml`, that fails with `<key>: Extra inputs are not permitted`, so the branch cannot be reviewed, and a session cannot be reported when it ends. `TASK-136` hit this with `agent_command`, and `TASK-150` will with `check`. A person running a global `chitty show` in that worktree hits it too.

In `load_repo_config`, for both `chitty.toml` and `[tool.chitty]`, when the file's `chitty_version` is newer than the running code, remove top-level keys not in `RepoConfig.model_fields` before validating, and warn on stderr naming them and saying to upgrade Chitty. `Repo.open` loads the file several times in a run, so warn once per process for a given file. Otherwise keep refusing, so a typo still fails loudly, and every other validation error still refuses, including unknown keys in `[contexts.*]`, which no ticket has needed. A branch adding a key is expected to bump the version; one that does not gets today's loud refusal.

Move `_version_key` from `src/chitty/store.py` to `src/chitty/config.py`, because `store` imports `config`, and compare with it. A malformed version keeps its existing error. Also use it in `_warn_setup_version` in `src/chitty/cli.py`, which compares versions as strings, so `0.1.100` sorts below `0.1.27`.

`chitty init` must not lose the new key's protection: `init_repo` rewrites `chitty_version` to the running version, so older code would now downgrade a newer file. Have it refuse a newer file with the same message as `_check_setup_version`.

Other writes need nothing new: `_check_setup_version` already refuses them when the file is newer than the code, with a message naming the version, and that stays. So does the claim `chitty run` makes on a `todo` ticket, which is fine, because a new branch from `main` is never newer than `main`'s code, and a resumed `doing` ticket has no claim to make.

Agents are not this ticket's concern. This repository's `agent_command` already starts them through `uv run`, so their `chitty` is the worktree's own (commit `b58cac8`).

Out of scope: `chitty run` checking which `chitty` an agent will find, and upgrading anyone's installs.

## Acceptance Criteria

- [ ] Tests show an unknown top-level key in either config file loading with one stderr warning naming it when `chitty_version` is newer than the code, leaving `chitty show --json` output valid, and refusing when the version is equal, older or absent, or the key is in `[contexts.*]`
- [ ] A test shows `chitty run` reviewing a ticket whose branch adds a key and bumps the version, and reporting the status change
- [ ] Tests show `chitty init` refusing a newer file, leaving it unchanged, and `0.1.100` compared as newer than `0.1.27` by the version warning

## Notes

Hit again 2026-11-04 on `TASK-136`: `chitty run` picked `review TASK-136`, ran `setup` in the worktree, then failed at `Repo.open(worktree)` with `agent_command: Extra inputs are not permitted`, before any claim or session. The worktree's own `.venv/bin/chitty run` cannot get round it, because `run` reads `agent_command` from the main checkout, which does not have it until the branch lands. Preferred option: warn about an unknown key when the file's `chitty_version` is newer than the running code, and keep refusing otherwise, so a typo still fails loudly. A branch adding a key already has to bump the version. `TASK-150` adds `check`, so it will hit this next.

Rewritten 2026-11-04: the human chose this fix. My earlier note was incomplete: warning alone does not let an agent write, because `_check_setup_version` refuses writes when the file is newer than the code. So agents get the branch's `chitty` from configuration instead, in commit `b58cac8`. That commit also answers the same error from a `TASK-141` session, where only `~/.envs/default/bin/chitty` of the three installs fails: it is 0.1.25, editable from `.worktrees/pi-token-analysis`. Why that session found it was not established.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: where `_version_key` goes, given the import direction; both config sources; dropping keys before validating, because catching the error and retrying could also drop keys in `[contexts.*]`; repeated warnings; stderr and valid JSON; and a title that promised more than this delivers. Found while checking the report, not by it: `init_repo` rewrites `chitty_version`, so ignoring the key would let older code downgrade a newer file, and `_warn_setup_version` compares strings. Rejected: work mode's claim being refused, because a fresh branch cannot be newer than `main`'s code; `inbox.py` callers, which gain a harmless warning on another project's newer file; enforcing the version bump, because a missing one refuses loudly; a version bump here, because nothing changes for `chitty init` to deliver except a refusal, and existing repositories need no refresh.

## History

- 2026-11-04T09:46:24Z lively-panda → backlog
- 2026-11-04T17:03:09Z mellow-newt: changed notes
- 2026-11-04T17:32:41Z mellow-newt: changed priority, description, acceptance criteria, notes
- 2026-11-04T17:34:51Z mellow-newt: changed title, description, acceptance criteria, notes
