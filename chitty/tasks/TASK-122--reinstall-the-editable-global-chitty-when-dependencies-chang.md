---
title: Reinstall the editable global `chitty` when dependencies change
status: todo
depends_on:
  - TASK-120
  - TASK-131
created: 2026-11-03
---

## Description

An editable `uv tool` install picks up code from `main` but not new dependencies, so landing a dependency change can give other repositories `ModuleNotFoundError` until the tool is reinstalled. `chitty run` lands tickets after `TASK-120`, so it can run this step; until then merging is only a prompt instruction.

1. Add an optional `after_land` command to `chitty.toml`, parsed without a shell like `autoformat`. `chitty run` runs it in the main checkout after each `git merge --ff-only`, before removing the worktree, so a failure leaves the ticket pending and the next run repeats it. Unset means nothing runs, since most repositories need nothing. A failure exits non-zero with a message; the ticket has already landed, so nothing is rolled back, and the message gives the command to run.
2. Add a `make refresh-global` target that reinstalls only if the hash of `pyproject.toml` and `uv.lock` differs from a stamp in an ignored file, `.global-deps`, writing the stamp only after success, using `uv tool install --reinstall --editable '.[mcp]'` from the main checkout. Keeping the dependency test in the Makefile keeps Chitty free of uv knowledge. Reinstalling only on change avoids disturbing running sessions. Set `after_land = "make refresh-global"` in this repository, which assumes one developer's machine; another clone can change it.
3. `README.md` currently says not to make a global editable install, while `TASK-118` made this machine's install editable on purpose. The unlanded `task-118` branch already changes `README.md` and `PLAN.md`, so check whether it has landed first. Keep the advice for users, and add a section for maintainers describing this setup and `after_land`.

Accepted limit: a plain `git merge` or `git pull` by hand skips this until the next landing, which catches up because the stamp differs, and the command is `make refresh-global`. See `TASK-118` for why it must never run from a worktree: it would repoint the global install at a directory that later gets removed.

Out of scope: detecting a broken install at startup, because the failure is an import error before any Chitty code can run.

## Acceptance Criteria

- [ ] Tests with a fake `pi` show `after_land` running in the main checkout after a landing, not running when unset, parsed without a shell, and a failure exiting non-zero with the ticket still landed
- [ ] Run by hand: `make refresh-global` makes no change when dependency files are unchanged. With a new dependency on a scratch branch landed, the receipt still shows editable from the main checkout with the `mcp` extra, and `chitty` works from another repository. Record this in a note
- [ ] `PLAN.md`, `README.md` and the `chitty.toml` template describe `after_land`; `__version__` is bumped
- [ ] A test shows `chitty init` does not set `after_land` in a new or existing repository; the `chitty.toml` template shows it only as a commented example; only this repository sets `after_land = "make refresh-global"`

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. It found this ticket left its central decision open, had no testable criterion, pointed at no code, and contradicted `README.md`. Rewritten on top of `TASK-120`, since there was no merge code to hook into. The author chose `after_land` and the Makefile check, cheap to change.

Decided with the human, 2026-11-03: set `after_land` in this repository, but never make it a default on new installs, so other people are unaffected.

Every finding from the cold read now has an outcome. Fixed on the second pass: I had made `ORIG_HEAD` decide when to reinstall, but `chitty run` retries after a failure, when the fast-forward is a no-op and `ORIG_HEAD` cannot be relied on, so a failed reinstall might never be repeated. A stamp file also catches up after a hand merge. Also verified: the receipt is editable with the `mcp` extra at `~/.local/share/uv/tools/chitty`, and `README.md` still disagrees because the `TASK-118` documentation commit never landed. Rejected: excluding the `dev` group, because an extra reinstall is harmless. A Git hook, because it is not shared by clones. Other machines and non-editable installs, because `after_land` is only set here. Running sessions, because reinstalls are rare. Overlap between `TASK-119` to `TASK-122`, because they touch different things.

Run `after_land` before the `chitty init` step added to `TASK-120`: a new dependency must be installed before the new code can run.

Landing moved from `TASK-120` to `TASK-131`, so read references to that step accordingly.

Archived 2026-11-04 unbuilt: the human decided the global `chitty` comes from PyPI (`TASK-160`), so there will be no editable global to reinstall.

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T18:19:34Z lively-panda: changed dependencies, description, acceptance criteria, notes
- 2026-11-03T19:23:01Z lively-panda: changed acceptance criteria, notes
- 2026-11-03T20:00:18Z lively-panda: changed description, notes
- 2026-11-03T20:44:56Z lively-panda: changed notes
- 2026-11-03T20:46:21Z lively-panda: changed dependencies, notes
- 2026-11-04T19:36:58Z mellow-newt: changed notes
