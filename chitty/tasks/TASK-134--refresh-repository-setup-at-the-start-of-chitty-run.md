---
title: Refresh repository setup at the start of `chitty run`
status: todo
priority: high
parent: TASK-106
created: 2026-11-03
---

## Description

A landed version bump or extension change only takes effect when someone runs `chitty init` in the main checkout, and nobody is prompted except by a warning. So `chitty run` can start an agent with an old extension, or one left by a leak like the one that stopped `TASK-126`. Have every `chitty run` bring setup up to date before it selects a ticket, as suggested by the human on 2026-11-03.

Add `Repo.refresh_setup()` in `src/chitty/store.py`, and call it first in `run` in `src/chitty/run.py`. It shares its code with `_prepare_write`: refuse if the recorded version is newer than the running code, call `init_repo(self.root, False)`, commit any repository files with `chitty: upgrade repository setup`, and reload the config. Print each changed path on stderr, so the update is visible.

Always call `init_repo`, not only when `chitty_version` differs. It is idempotent and writes nothing if nothing changed, and an extension can differ without a version change, for example after a leak or two tickets bumping to the same version. Decided by the author, cheap to change.

A failure stops the run before any agent starts: for example a locally edited extension, which `validate_pi_extension` refuses, with the existing message. Do not catch it.

The process is new at each `chitty run`, so it already holds the latest code, and no subprocess is needed. This also replaces the step in `TASK-131` that ran `chitty init` after landing: the next run does it, and until then no agent needs the new extension.

With `autocommit` off, leave the changed files uncommitted, as `chitty init` does. `TASK-126` then refuses that repository in its preflight.

Run from inside a linked worktree, `TASK-129` already skips the Pi install. After `TASK-126` lands, `run` works from the main checkout in every case, so that ticket must call this on its main repository object, after its preflight.

Out of scope: running init from `chitty next` or any other command.

## Acceptance Criteria

- [ ] A test runs `chitty run` with a fake `pi` in a repository with a stale `chitty_version`: setup is upgraded and committed before `pi` starts, and the fake `pi` sees the current version
- [ ] A test with a temporary `PI_CODING_AGENT_DIR` and an up-to-date `chitty_version` shows a differing installed extension replaced before `pi` starts
- [ ] A test shows that when nothing is out of date, a run makes no commit and prints nothing about setup
- [ ] A test shows a failing refresh, such as a recorded version newer than the code or a locally edited extension, exits non-zero without starting `pi`
- [ ] `PLAN.md` and `README.md` say `chitty run` refreshes setup

## History

- 2026-11-03T21:21:52Z lively-panda → todo
