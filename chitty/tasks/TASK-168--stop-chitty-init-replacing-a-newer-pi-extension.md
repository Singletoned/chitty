---
title: Stop `chitty init` replacing a newer Pi extension
status: backlog
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

The Pi extension is one file shared by every repository, but `install_pi_extension` in `src/chitty/actor.py` writes whatever the running Chitty ships, whichever repository it runs in. On 2026-11-04, a session in another repository ran `chitty init` with a stale `~/.envs/default/bin/chitty`, 0.1.25, and replaced the installed extension with that version, which lacks the `TASK-147` fix. Nothing warned, because the state file only records a hash to detect local edits, and it matched. Any older copy can do this, including a worktree's `.venv` running `chitty init`.

Record the version beside the hash in the state file, `_PI_EXTENSION_STATE`. When the installed extension is from a newer Chitty than the one running, leave it and print a warning to stderr naming both versions, and let `chitty init` finish, because the repository's own setup is still right to update. A state file holding only a hash is treated as an older version. Compare with `_version_key`, wherever it then lives.

## Acceptance Criteria

- [ ] Tests show an older Chitty leaving a newer extension in place with a warning naming both versions and finishing the rest of `init`, a newer or equal Chitty updating as now, and a hash-only state file being replaced
- [ ] A locally edited extension is still refused, shown by the existing test passing, and `__version__` is bumped above `main`'s

## History

- 2026-11-04T21:00:16Z mellow-newt → backlog
