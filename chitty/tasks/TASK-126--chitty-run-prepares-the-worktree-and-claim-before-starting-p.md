---
title: "`chitty run` prepares the worktree and claim before starting Pi"
status: doing
priority: high
depends_on:
  - TASK-124
  - TASK-128
parent: TASK-106
created: 2026-11-03
---

## Description

Make `chitty run` do the mechanical setup before starting Pi, so the agent starts in the right place with nothing to get wrong. These steps are currently prompt instructions, and they have failed: the `TASK-107` worker committed its claim on `main`, then ran `git reset --hard` in the main checkout (`TASK-121`). A script does them more reliably and for no tokens, and the prompts get shorter.

This supersedes two parts of `TASK-124`: Pi's working directory becomes the worktree, not the repository root, so rewrite that test; and `chitty run -- --model sonnet` replaces the advice to call `pi` directly.

### Before anything changes

`chitty run` works the same from the main checkout or any worktree: find the main checkout with `git rev-parse --git-common-dir` and read config from there, so old branches with no `setup` key still work. Exit non-zero with a message, changing nothing, if:

- `autocommit` is off, because a claim and status changes must be committed to be visible.
- `pi` is not on `PATH`, so a missing `pi` cannot leave a claimed ticket.
- `setup` is unset. It has no default, since a wrong guess would look like a working environment. `chitty init` adds a commented example; set `setup = "make install"` in this repository.
- The main checkout is not on branch `main`. `inbox --pull` commits there and `TASK-120` lands there, so both must be on the right branch.

### Then, in order

1. Run the equivalent of `chitty inbox --pull` from the main checkout, if the repository has a `project`. A failure stops the run. This only adds `backlog` tickets, so it cannot change the selection.
2. Select the ticket. If its file has uncommitted changes in the main checkout, stop with a loud error, as a new branch would not contain them.
3. Find the worktree by branch name, `<id in lower case>` (for example `task-124`). Do not use `StoredTask.branch`: it can name another branch holding the same version, or a remote ref. A branch that exists only on a remote is not considered; the `TASK-105` guard then refuses the claim loudly.
    - Branch exists and has a linked worktree: use it, wherever it is, per `git worktree list`. Uncommitted files there are left alone: a `doing` ticket is resuming, and `TASK-120` deals with them before a review.
    - Branch exists with no worktree: add one at `.worktrees/<branch>` in the main checkout.
    - Branch does not exist: in mode `work`, create it from local `main` at `.worktrees/<branch>`. In mode `review`, this is a loud error, as there is nothing to review.
    - Branch checked out in the main checkout: loud error, and never switch the main checkout.
    - Anything else Git refuses, such as a stale directory, is a loud error with Git's message.
4. Run `setup` in the worktree, every time, because dependencies may have changed since the last session. It is parsed without a shell, like `autoformat`, with output inherited and stdin closed. A failure stops the run, leaving the worktree in place and the ticket unclaimed. The next run reuses the worktree and runs `setup` again.
5. In mode `work`, if the ticket is `todo`, set it to `doing` in the worktree through `Repo.edit`, so the claim is committed on the branch.
6. Read the ticket's status. This is the `TASK-124` baseline for "did the status change", so a claim alone never counts as progress and a dead session stops a loop on its first run. The accepted extra session in `TASK-124`'s notes no longer applies.
7. Start `pi --chitty-<mode> <ID>` with the worktree as its working directory, passing through any arguments given after `--`.

Ctrl-C during `inbox --pull` or `setup` exits 130 with one line and no traceback.

### Actor

The claim and the Pi session must be one actor, different from every other run. Generate a UUID for each `chitty run`, and set `CHITTY_PI_SESSION_ID` to it in `chitty run`'s own environment, overwriting any inherited value, before the claim. The extension leaves it alone and subagents inherit it. Also remove `CHITTY_ACTOR` and `CLAUDE_CODE_SESSION_ID` from the environment for the run, as `actor()` checks them first and they would make runs share an actor.

### Extension

The extension stops telling agents to do any of this. `--chitty-work`, `--chitty-review` and `/chitty` all refuse to start, with a message pointing at `chitty run`, unless the working directory is a linked Git worktree (`git rev-parse --git-dir` differs from `--git-common-dir`). That also guards the main checkout for Pi (`TASK-121`).

Out of scope: merging, gates and removing worktrees (`TASK-120`); non-Pi harnesses; `src/chitty/guide.md`, which still describes the manual steps for other agents; a second `chitty run` on the same ticket while one is running.

## Acceptance Criteria

- [ ] Tests with a fake `pi` and a real Git repository cover a `todo` ticket with no branch, a ticket with a branch and no worktree, a ticket with a worktree, and `review` with no branch: each checks the working directory `pi` receives and the branch holding the claim
- [ ] Tests show the main checkout has no new commits on its branch from the claim, that a second `chitty run` reuses the worktree, and that a `doing` ticket is not claimed again
- [x] Tests cover `setup` unset and `setup` failing: each exits non-zero with a message and does not start `pi`
- [ ] Tests show arguments after `--` reach `pi`, and that the claim and a write from the fake `pi` record one actor, different from the actor of a second run
- [x] Node tests show the prompts no longer mention creating worktrees, setup or claiming, and that startup refuses outside a linked worktree
- [x] `PLAN.md`, `README.md` and the `chitty.toml` template document `setup`; `chitty init` handles existing repositories; `__version__` is bumped
- [x] Tests cover the preflight refusals: `autocommit` off, `pi` missing and the main checkout without `main`, each leaving no worktree, branch or claim
- [ ] Tests cover running from inside another worktree, a ticket whose newest copy is on `main` (it must not try to add a `main` worktree), a branch checked out in the main checkout, and uncommitted changes to the ticket in the main checkout
- [ ] Tests show the order: `inbox --pull` happens and is skipped with no `project`; `setup` runs in the worktree on every run, before the claim, parsed without a shell; a failed `setup` leaves the ticket unclaimed; `review` mode changes no status
- [ ] A test shows a fake `pi` that does nothing on a `todo` ticket makes `chitty run` exit non-zero, with the ticket left in `doing`, and that the next run resumes it
- [ ] A test shows that with `CHITTY_ACTOR` and `CLAUDE_CODE_SESSION_ID` set, two runs still record different actors
- [x] Run by hand in a scratch repository: `chitty run` starts Pi in the new worktree and the ticket is claimed on its branch. The note records whether Pi interrupted with any prompt; if it does, say so rather than work around it
- [ ] A test shows `chitty run` leaves the main checkout's `HEAD`, branch and `git status` unchanged apart from any inbox commit, and refuses when it is on another branch
- [ ] This repository sets `setup = "make install"`, a test shows `chitty init` adds `setup` to an existing repository only as a commented example, and `README.md` no longer advises calling `pi` directly
- [ ] Outside a linked worktree, Pi shows a one-line message and exits, with no stack trace and no session left open; a Node test covers this
- [ ] A Node test shows the worktree check refusing in a subdirectory of the main checkout

## Plan

1. Add black-box CLI tests using real Git repositories and a fake `pi` to define every preflight, worktree, setup, claim, actor and progress path.
2. Move run orchestration into `run.py`: resolve the main checkout, validate preconditions before mutation, pull the inbox, select and prepare the ticket worktree, run parsed setup, claim `todo`, then launch Pi from that worktree.
3. Extend config/init, Pi extension startup guards, documentation and release metadata for the required setup contract.
4. Run targeted tests, then `make check`; exercise `chitty run` manually in a scratch repository; tick criteria only from that evidence.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. Biggest finds: `StoredTask.branch` reports `main` from a worktree, so step 2 as written would have tried to add a `main` worktree (branch lookup is now by name); and a claim counted as progress, which would have defeated the loop stopping on dead sessions (the baseline is now taken after the claim). Also adopted: preflight checks, config read from the main checkout, actor variables cleared, and the guard on `/chitty` too. The "no trust prompt" criterion is now an observation, as Chitty may not control it.

Blocked: current cross-branch write protection refuses both the required `--plan` and `todo` to `doing` claim from the new `task-126` worktree because this ticket’s newest committed copy is on `main`. Completing the requested pre-implementation branch claim requires a bootstrap route that writes the claim on its new branch (the behavior this ticket is intended to add), or human authorization to make the ticket-state write on `main`. A human must choose one of those options; no implementation has started.

Unblocked by the author, 2026-11-03: the block was a bug in the `TASK-105` guard, not a decision for the human, and is now `TASK-128`, on which this depends. The worker was right to stop. Its worktree and branch had no commits and were removed. When this is picked up, branch from `main` after `TASK-128` lands.

Every finding from the cold read now has an outcome. Fixed in the ticket on the second pass: the main checkout must be on `main` (I had let a wrong branch through), a test that it is left untouched (the old criterion only checked commits), resuming with uncommitted files, this repository's `setup`, the `init` migration, and the `README.md` advice. The `StoredTask.branch` wording is corrected now `TASK-128` has landed. Rejected: a test that prompts get shorter, because the goal is removing the steps, which is tested. Worktree `.gitignore` handling, because `_add_worktrees_to_gitignore` in `init` already does it. An extra setup-upgrade commit on a stale branch, because it is existing behaviour, an identical `chitty.toml` change rebases cleanly, and a different one fails loudly. A conflict with `TASK-124` criterion 5, because `run` re-reads through a new `Repo`. Two concurrent runs, because a single worker is the stated assumption. `formatter.run` not being reusable, because a worker sees that on reading it. `setup` breaking existing repositories, because only `chitty run` needs it and it fails with a clear message.

Manual scratch-repository check: `chitty run` created `.worktrees/task-1`, claimed on branch `task-1`, and started the fake Pi there; it reported `TASK-1: doing → blocked`. Pi did not interrupt with any prompt.

The globally installed `chitty` was still pre-TASK-126 and rejected `setup`; verification and ticket writes used this worktree’s `.venv/bin/chitty`.

Verified criterion 5 with `npm test -- --test src/chitty/integrations/pi/tests/chitty.test.ts`: work prompts omit worktree, setup and claim instructions; the extension rejects a main-checkout Git directory with a `chitty run` message.

Verified criterion 6 with `tests.test_cli.TestInit` and `make check`: new templates and existing-repository upgrades keep `setup` as a commented example; project config sets `setup = "make install"`; version, README and PLAN were updated.

Verified criterion 7 with `TestNext.test_run_refuses_preflight_without_mutating` and `make check`: disabled autocommit, unset setup, missing Pi and a non-main checkout all fail before a worktree or claim is created.

Verified criterion 3 with `TestNext.test_run_refuses_preflight_without_mutating`, `TestNext.test_run_setup_failure_does_not_start_pi_or_claim_ticket`, and `make check`: missing setup and a failing parsed setup both fail without starting Pi; failed setup leaves the new worktree unclaimed.

Findings from a real run on 2026-11-03. The refusal raised a stack trace and left Pi open, so a criterion is added. The session ended at the continuation cap despite progress: see the new cap ticket. Running worktree code wrote the unfinished extension to `~/.pi/agent/extensions`, repaired with `chitty init` on `main`; do not run `chitty init` from this worktree again until the install ticket lands. This branch sets `chitty_version = "0.1.22"` and `setup`, which the global `chitty` cannot read, so use `.venv/bin/chitty` in this worktree, including for review.

From the `TASK-129` cold read: `requireLinkedWorktree` must compare `--git-dir` and `--git-common-dir` as resolved paths, not strings. As strings they differ in a subdirectory of the main checkout, so Pi started there would pass the guard. Add a Node test.

## History

- 2026-11-03T16:30:14Z lively-panda → todo
- 2026-11-03T16:30:15Z lively-panda: changed acceptance criteria
- 2026-11-03T16:48:59Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T19:22:46Z nimble-crane: changed notes
- 2026-11-03T19:22:46Z nimble-crane todo → blocked
- 2026-11-03T19:25:32Z lively-panda: changed dependencies, notes
- 2026-11-03T19:25:32Z lively-panda blocked → todo
- 2026-11-03T20:00:15Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T20:14:32Z eager-lynx: wrote the plan
- 2026-11-03T20:14:32Z eager-lynx todo → doing
- 2026-11-03T20:21:42Z eager-lynx: changed notes; ticked acceptance criteria
- 2026-11-03T20:23:00Z eager-lynx: changed notes
- 2026-11-03T20:24:44Z eager-lynx: changed notes; ticked acceptance criteria
- 2026-11-03T20:26:09Z eager-lynx: changed notes; ticked acceptance criteria
- 2026-11-03T20:28:00Z eager-lynx: changed notes; ticked acceptance criteria
- 2026-11-03T20:29:37Z eager-lynx: changed notes; ticked acceptance criteria
- 2026-11-03T20:41:14Z lively-panda: changed acceptance criteria, notes
- 2026-11-03T20:44:59Z lively-panda: changed acceptance criteria, notes
