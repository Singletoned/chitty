---
title: Refresh repository setup at the start of `chitty run`
status: doing
priority: high
parent: TASK-106
created: 2026-11-03
---

## Description

A landed version bump or extension change only takes effect when someone runs `chitty init` in the main checkout, and nobody is prompted except by a warning. So `chitty run` can start an agent with an old extension, or one left by a leak like the one that stopped `TASK-126`. Have every `chitty run` bring setup up to date before it selects a ticket, as suggested by the human on 2026-11-03.

Add `Repo.refresh_setup()` in `src/chitty/store.py`, and call it first in `run` in `src/chitty/run.py`. In order: do nothing in a linked Git worktree (`git.is_linked_worktree`), because a commit there would land the upgrade on a ticket branch. Refuse if the recorded version is newer than the running code, sharing that check with `_prepare_write`. Refuse with a message if `chitty.toml`, `pyproject.toml`, `AGENTS.md` or `.gitignore` has uncommitted changes, because `git.commit` commits whole files and would sweep those edits into the upgrade. Call `init_repo(self.root, False)`, commit changed files inside the repository with `chitty: upgrade repository setup`, and reload the config. Print each path `init_repo` returns on stderr. Unlike `_prepare_write`, it neither returns early on an equal version nor raises when `autocommit` is off.

Always call `init_repo`, not only when `chitty_version` differs. It is idempotent and writes nothing if nothing changed, and an extension can differ without a version change, for example after a leak or two tickets bumping to the same version. Decided by the author, cheap to change.

A failure stops the run before any agent starts: for example a locally edited extension, which `validate_pi_extension` refuses, with the existing message. Do not catch it.

The process is new at each `chitty run`, so it already holds the latest code, and no subprocess is needed. This also replaces the step in `TASK-131` that ran `chitty init` after landing: the next run does it, and until then no agent needs the new extension.

With `autocommit` off, leave the changed files uncommitted, as `chitty init` does. After `TASK-126` lands its preflight refuses that repository first, so this only applies until then.

After `TASK-126` lands, `run` works from the main checkout in every case, so that ticket must call this on its main repository object, right after its preflight.

The warning in `_repo()` in `src/chitty/cli.py` fires before `run` starts, so a stale repository would be told to re-run `chitty init` just before it happens automatically. Do not show it for `run`.

No version bump: this does not change what `init` writes.

Test hints: `_pi_extension_files` returns nothing unless the Pi directory exists, so create `PI_CODING_AGENT_DIR`. A differing extension counts as a local edit unless the state hash matches it, so write that file too. `tests/test_cli.py:130` shows the setup.

Out of scope: running init from `chitty next` or any other command.

## Acceptance Criteria

- [ ] A test with a temporary `PI_CODING_AGENT_DIR` and an up-to-date `chitty_version` shows a differing installed extension replaced before `pi` starts
- [ ] A test shows a failing refresh, such as a recorded version newer than the code or a locally edited extension, exits non-zero without starting `pi`
- [ ] `PLAN.md` and `README.md` say `chitty run` refreshes setup
- [ ] A test runs `chitty run` with a fake `pi` in a repository with a stale `chitty_version`: before `pi` starts, the fake `pi` sees the current version, one `chitty: upgrade repository setup` commit holds only setup files, the changed paths are on stderr, and no warning to re-run `chitty init` appears
- [ ] Tests show that when nothing is out of date, and when run from a linked worktree, a run makes no commit and prints nothing about setup
- [ ] A test shows uncommitted changes to `AGENTS.md` make the run exit non-zero without starting `pi`, leaving those changes in place and uncommitted

## Plan

1. Add focused CLI integration tests covering refresh-before-`pi`, failures, no-op/worktree, and protected uncommitted setup edits. 2. Implement `Repo.refresh_setup()` using existing setup/version/Git helpers, then invoke it before ticket selection. 3. Document the behavior in `PLAN.md` and `README.md`; run checks and verify every criterion.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03, with an outcome for every finding. Fixed: user edits being swept into the upgrade commit; a linked worktree committing the upgrade to a ticket branch, and printing on every run; the contradiction between `call it first`, `after its preflight` and the `autocommit` sentence; the misleading warning; how this differs from `_prepare_write`; test hints; and stated output now covered by criteria. Fixed in `TASK-131`: landing in the same process would have started the next agent on old code. Rejected: testing the config reload directly, because the fake `pi` seeing the current version covers it. A concurrent `chitty run`, because a single worker is the stated assumption and `index.lock` fails loudly. The installed extension changing while Pi runs, because Pi loads it at startup, though I have not verified that. No rollback on partial failure, because the error is loud and the next run refuses the dirty files. `_default_project` failing in an oddly named directory, because that is rare and loud. A version bump, because `init` output does not change.

## History

- 2026-11-03T21:21:52Z lively-panda → todo
- 2026-11-03T21:24:17Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T08:35:23Z mellow-lynx: wrote the plan
- 2026-11-04T08:35:23Z mellow-lynx todo → doing
