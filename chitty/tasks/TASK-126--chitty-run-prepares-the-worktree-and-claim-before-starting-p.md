---
title: "`chitty run` prepares the worktree and claim before starting Pi"
status: blocked
priority: high
depends_on:
  - TASK-124
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
- The main checkout has no branch `main`.

### Then, in order

1. Run the equivalent of `chitty inbox --pull` from the main checkout, if the repository has a `project`. A failure stops the run. This only adds `backlog` tickets, so it cannot change the selection.
2. Select the ticket. If its file has uncommitted changes in the main checkout, stop with a loud error, as a new branch would not contain them.
3. Find the worktree by branch name, `<id in lower case>` (for example `task-124`). Do not use `StoredTask.branch`: it reports `main` when run from a worktree, and can be a remote ref.
    - Branch exists and has a linked worktree: use it, wherever it is, per `git worktree list`.
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
- [ ] Tests cover `setup` unset and `setup` failing: each exits non-zero with a message and does not start `pi`
- [ ] Tests show arguments after `--` reach `pi`, and that the claim and a write from the fake `pi` record one actor, different from the actor of a second run
- [ ] Node tests show the prompts no longer mention creating worktrees, setup or claiming, and that startup refuses outside a linked worktree
- [ ] `PLAN.md`, `README.md` and the `chitty.toml` template document `setup`; `chitty init` handles existing repositories; `__version__` is bumped
- [ ] Tests cover the preflight refusals: `autocommit` off, `pi` missing and the main checkout without `main`, each leaving no worktree, branch or claim
- [ ] Tests cover running from inside another worktree, a ticket whose newest copy is on `main` (it must not try to add a `main` worktree), a branch checked out in the main checkout, and uncommitted changes to the ticket in the main checkout
- [ ] Tests show the order: `inbox --pull` happens and is skipped with no `project`; `setup` runs in the worktree on every run, before the claim, parsed without a shell; a failed `setup` leaves the ticket unclaimed; `review` mode changes no status
- [ ] A test shows a fake `pi` that does nothing on a `todo` ticket makes `chitty run` exit non-zero, with the ticket left in `doing`, and that the next run resumes it
- [ ] A test shows that with `CHITTY_ACTOR` and `CLAUDE_CODE_SESSION_ID` set, two runs still record different actors
- [ ] Run by hand in a scratch repository: `chitty run` starts Pi in the new worktree and the ticket is claimed on its branch. The note records whether Pi interrupted with any prompt; if it does, say so rather than work around it

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. Biggest finds: `StoredTask.branch` reports `main` from a worktree, so step 2 as written would have tried to add a `main` worktree (branch lookup is now by name); and a claim counted as progress, which would have defeated the loop stopping on dead sessions (the baseline is now taken after the claim). Also adopted: preflight checks, config read from the main checkout, actor variables cleared, and the guard on `/chitty` too. The "no trust prompt" criterion is now an observation, as Chitty may not control it.

Blocked: current cross-branch write protection refuses both the required `--plan` and `todo` to `doing` claim from the new `task-126` worktree because this ticket’s newest committed copy is on `main`. Completing the requested pre-implementation branch claim requires a bootstrap route that writes the claim on its new branch (the behavior this ticket is intended to add), or human authorization to make the ticket-state write on `main`. A human must choose one of those options; no implementation has started.

## History

- 2026-11-03T16:30:14Z lively-panda → todo
- 2026-11-03T16:30:15Z lively-panda: changed acceptance criteria
- 2026-11-03T16:48:59Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T19:22:46Z nimble-crane: changed notes
- 2026-11-03T19:22:46Z nimble-crane todo → blocked
