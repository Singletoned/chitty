---
title: Rebase the ticket branch onto `main` before every work session
status: planning
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-373
  - TASK-374
  - TASK-384
  - TASK-382
  - TASK-524
  - TASK-534
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model a ticket file changes only on its branch, so ticket files rebase like any other file; there is no ticket merge (`TASK-359` is archived). Any conflict goes to an agent.

A work session today runs on whatever the ticket branch last had: `_run_ticket` in `src/chitty/run.py` never brings in `main` in work mode, so workers build on code behind `main`, and `setup` and `check` test code that is not what would land.

Starts after `TASK-524` (`git.save_work`, `git.restore_work`) lands; `TASK-374`, `TASK-373`, `TASK-382` and `TASK-384` have landed. Out of scope: saved work that cannot be restored, an existing saved-work ref, and the prompt sentence naming it (`TASK-525`).

Decisions:

- In work mode, after `_worktree` and the claim (`TASK-384`) and before `setup`, rebase the worktree onto `main` for every ticket status.
- Uncommitted work is cheap to redo (decided with the owner 2026-11-18), so save it explicitly rather than with `--autostash`, which a cold read showed can report success with conflict markers left behind, hide edits during a stopped rebase, and break the next run. Decided 2026-11-21: never use the shared stash list; saved work goes under the per-ticket ref `refs/chitty/stash/<ID>` through `git.save_work` and `git.restore_work` (`TASK-524`). The per-ticket run lock in `src/chitty/run.py` already stops two runs of one ticket.
  1. `git.save_work(worktree, f"refs/chitty/stash/{id}", f"chitty {id} before rebase")`.
  2. Rebase with `git.rebase_onto` (`TASK-374`), which never uses `--autostash`.
  3. If the rebase completed and work was saved: `git.restore_work(worktree, ref)`, then carry on. Its `False` result, and `save_work`'s refusal when the ref already exists, are handled by `TASK-525`; in this ticket let `save_work`'s `ChittyError` propagate and ignore `restore_work`'s result.
  4. If the rebase stopped on a conflict (any file): leave it stopped and the ref in place, skip `setup` and `check`, and start the agent (the work agent, or the repair agent for an `error` ticket). Write nothing to the ticket while the rebase is stopped. The prompt sentence naming the ref is `TASK-525`.
- Prompt rendering (rechecked 2026-11-21 against `main`): `_agent_command` already takes `worktree` and passes it to `guide()` when that directory exists, and `guide()` already puts the body of `src/chitty/roles/rebase.md` after the `Work only on Chitty ticket <ID>.` line when a rebase is in progress there. `_run_ticket_with_log` renders the command twice: once before `_worktree` (keep it, so a bad `agent_command` still fails before anything is written) and once after the claim. Move that second rendering to after the rebase, so the prompt reflects a stopped rebase. No change to `_agent_command`'s signature.
- A `rebase_onto` error that is not a conflict is recorded as a ticket error on the branch (`_record_ticket_error(branch_repo, ...)`, phase `rebase`), whose note also says `Uncommitted changes from before the rebase are in refs/chitty/stash/<ID>.` when work was saved; no agent starts.
- A rebase still in progress at the start of a later run is refused by `_worktree`, as today, for a human.
- Ctrl-C during the rebase runs `git rebase --abort` and raises `RunInterrupted("rebase")` (exit 130); the ref stays; naming it in the interrupt message is `TASK-525`. No test: it needs a signal mid-rebase (accepted).
- Accepted edge case: a nested untracked Git repository in the worktree is added as a gitlink by `git add -A`, survives the reset, and may come back staged.
- Update the work-mode bullet under `## Before a review` in `docs/plan/next-action-and-runner.md`.

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_work_rebases.py`, in the style of `tests/test_review_merge.py`, with `git init -b main`. A non-conflict rebase failure is made by patching `chitty.git.rebase_onto` to raise `ChittyError`. The fake agent records what it saw when it started (`git status`, `git.rebase_in_progress`, `git stash list`, `git for-each-ref refs/chitty/stash`, its prompt) in a marker file. No property: real Git and runner processes over the fixed cases in the criteria.

## Acceptance Criteria

- [ ] A work run on a `doing` ticket whose branch exists, with a new non-conflicting commit on `main`: afterwards `main` is an ancestor of the branch and `git rev-list main..task-<n>` lists only the branch's own commits, and a fake `check` command records `main`'s new commit in `git log` before the agent starts; this fails before the change
- [ ] A work run whose rebase stops on a code conflict, once on a `doing` ticket and once on an `error` ticket, starts the work agent or the repair agent respectively with a rebase in progress and a prompt in which the body of `src/chitty/roles/rebase.md` directly follows the `Work only on Chitty ticket TASK-<n>.` line (both recorded by a fake agent whose command has `{prompt}`); a fake `setup` and `check` record that they did not run; this fails before the change
- [ ] After `main` gains a commit touching another file, an unstaged edit to a tracked file, a staged edit and an untracked file are all present with the same content when the agent starts, and the branch has been rebased. `refs/chitty/stash/TASK-<n>` no longer exists, and `git stash list` is the same as before the run, including one entry the test pushed beforehand from the main checkout; this fails before the change
- [ ] A `rebase_onto` failure that is not a conflict, with an uncommitted file present, records `Runner error (rebase)` on the branch naming `refs/chitty/stash/TASK-<n>`, and starts no agent; `make check` passes

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

Planning 2026-11-18: took over giving `_agent_command` a `directory` from `TASK-373`, whose third cold read showed the runner half could not be tested there, because `_worktree` refuses a leftover rebase.

Cold read 2026-11-18 (the `directory` bullet) outcomes: accepted a `doing` case alongside the `error` case in criterion 2, so both render paths are checked; the exact rebase text and its position; the fails-before clause; keyword-only `directory`.

Planning needed: the prescribed stash identification is not safe under the concurrency it explicitly allows. If another worktree pushes a stash between the before and after lists, their set difference contains multiple IDs, not one; if an entry is dropped or shifted between finding its stash@{n} and dropping it, the wrong stash can be removed. The per-ticket run lock in src/chitty/run.py does not serialize different tickets. The ticket needs a decision on a concurrency-safe identification and drop protocol, including interaction with other Git stash users, plus a deterministic real-Git test fixture, action and assertions that exercise the interleaving and prove the correct stash is preserved or dropped. The existing fixed-case tests do not specify that test. No implementation or verification was started.

Replanned 2026-11-21: the stash concurrency blocker is settled by not using the shared stash list at all. Saved work goes to the per-ticket ref `refs/chitty/stash/<ID>` (see the Description).

Split 2026-11-21 after a cold read found it too large: `TASK-524` (save and restore helpers, no runner change) and `TASK-525` (saved work that cannot be restored). Keep this ticket in planning until `TASK-524` lands; then compare with the landed helpers, cold-read and move to `todo`.

Also waits for `TASK-534` (`restore_work`), split from `TASK-524` on 2026-11-21.

## History

- 2026-11-18T09:13:39Z witty-ginger-falcon → planning
- 2026-11-18T09:22:43Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:25:16Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:25:17Z witty-ginger-falcon: changed dependencies, description, acceptance criteria
- 2026-11-18T09:25:21Z witty-ginger-falcon planning → todo
- 2026-11-18T09:28:17Z witty-ginger-falcon: changed description
- 2026-11-18T09:32:30Z witty-ginger-falcon todo → planning
- 2026-11-18T09:51:40Z witty-ginger-falcon: changed dependencies
- 2026-11-18T09:51:42Z witty-ginger-falcon: changed dependencies
- 2026-11-18T09:51:44Z witty-ginger-falcon: changed title, labels, priority, dependencies, description, acceptance criteria
- 2026-11-18T09:52:37Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:54:24Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:54:26Z witty-ginger-falcon: changed dependencies, description, acceptance criteria
- 2026-11-18T09:54:27Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:42Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:42Z witty-ginger-falcon todo → planning
- 2026-11-18T17:57:44Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:57:46Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:57:48Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:57:51Z lively-quartz-crane: changed dependencies
- 2026-11-18T17:58:13Z lively-quartz-crane: changed dependencies
- 2026-11-18T18:00:07Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:16:56Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T18:16:56Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:16:58Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T18:17:00Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:17:17Z lively-quartz-crane: changed description
- 2026-11-18T18:19:34Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:19:34Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:19:36Z lively-quartz-crane planning → todo
- 2026-11-18T20:44:39Z lively-quartz-crane: changed description, notes
- 2026-11-18T20:44:39Z lively-quartz-crane todo → planning
- 2026-11-18T20:44:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T20:46:32Z lively-quartz-crane: changed description, acceptance criteria, notes
- 2026-11-18T20:46:32Z lively-quartz-crane cold-read → planning
- 2026-11-18T20:46:37Z lively-quartz-crane planning → todo
- 2026-11-20T19:05:55Z daring-ebony-heron todo → doing
- 2026-11-20T19:07:26Z daring-ebony-heron: changed owner, notes
- 2026-11-20T19:07:26Z daring-ebony-heron doing → planning
- 2026-11-21T23:08:26Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-21T23:08:55Z lively-zinc-newt: changed description
- 2026-11-21T23:08:55Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:11:38Z lively-zinc-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-21T23:11:38Z lively-zinc-newt cold-read → planning
- 2026-11-22T00:06:48Z lively-zinc-newt: changed dependencies, notes
