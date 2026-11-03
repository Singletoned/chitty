---
title: Reinstall the editable global `chitty` when dependencies change
status: todo
depends_on:
  - TASK-120
created: 2026-11-03
---

## Description

An editable `uv tool` install picks up code from `main` but not new dependencies, so landing a dependency change can give other repositories `ModuleNotFoundError` until the tool is reinstalled. `chitty run` lands tickets after `TASK-120`, so it can run this step; until then merging is only a prompt instruction.

1. Add an optional `after_land` command to `chitty.toml`, parsed without a shell like `autoformat`. `chitty run` runs it in the main checkout after each `git merge --ff-only`, before removing the worktree. Unset means nothing runs, since most repositories need nothing. A failure exits non-zero with a message; the ticket has already landed, so nothing is rolled back, and the message gives the command to run.
2. Add a `make refresh-global` target that reinstalls only if `git diff --quiet ORIG_HEAD HEAD -- pyproject.toml uv.lock` reports a change, using `uv tool install --reinstall --editable '.[mcp]'` from the main checkout. Keeping the dependency test in the Makefile keeps Chitty free of uv knowledge. Reinstalling only on change avoids disturbing running sessions. Set `after_land = "make refresh-global"` in this repository, which assumes one developer's machine; another clone can change it.
3. `README.md` currently says not to make a global editable install, while `TASK-118` made this machine's install editable on purpose. Keep the advice for users, and add a section for maintainers describing this setup and `after_land`.

Accepted limit: a plain `git merge` or `git pull` by hand skips this, and the command is `make refresh-global`. See `TASK-118` for why it must never run from a worktree: it would repoint the global install at a directory that later gets removed.

Out of scope: detecting a broken install at startup, because the failure is an import error before any Chitty code can run.

## Acceptance Criteria

- [ ] Tests with a fake `pi` show `after_land` running in the main checkout after a landing, not running when unset, parsed without a shell, and a failure exiting non-zero with the ticket still landed
- [ ] Run by hand: `make refresh-global` makes no change when dependency files are unchanged. With a new dependency on a scratch branch landed, the receipt still shows editable from the main checkout with the `mcp` extra, and `chitty` works from another repository. Record this in a note
- [ ] `PLAN.md`, `README.md` and the `chitty.toml` template describe `after_land`; `__version__` is bumped
- [ ] A test shows `chitty init` does not set `after_land` in a new or existing repository; the `chitty.toml` template shows it only as a commented example; only this repository sets `after_land = "make refresh-global"`

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. It found this ticket left its central decision open, had no testable criterion, pointed at no code, and contradicted `README.md`. Rewritten on top of `TASK-120`, since there was no merge code to hook into. The author chose `after_land` and the Makefile check, cheap to change.

Decided with the human, 2026-11-03: set `after_land` in this repository, but never make it a default on new installs, so other people are unaffected.

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T18:19:34Z lively-panda: changed dependencies, description, acceptance criteria, notes
- 2026-11-03T19:23:01Z lively-panda: changed acceptance criteria, notes
