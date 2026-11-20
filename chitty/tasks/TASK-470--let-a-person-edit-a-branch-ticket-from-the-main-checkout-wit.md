---
title: Let a person edit a branch ticket from the main checkout with `chitty edit --human`
status: doing
priority: high
created: 2026-11-19
---

## Description

A person reviewing from the main checkout cannot edit a ticket whose latest copy is on its branch. `chitty edit TASK-420 -s done --note '...'` refuses with `TASK-420's latest committed version is on branch task-420; run Chitty in worktree <path>` (`Repo._require_current_version` in `src/chitty/store.py`), so on 2026-11-19 the owner had to type `cd .worktrees/task-463 && ../../.venv/bin/chitty edit TASK-463 ...` for each review. Commands a person runs inside an agent session (Claude Code's `!`) also get that session's actor name (`actor()` in `src/chitty/actor.py` derives it from the harness identity), so the review-independence rule treats the person as the agent that moved the ticket to `review`: the owner's `chitty edit TASK-404 -s done` was refused that way. The owner wants the convenience behind an explicit flag, so agents do not edit tickets in other worktrees by accident.

Decisions:

- New flag `--human` on `chitty edit` only (`src/chitty/cli.py`). It does two things for that one command, and nothing without it changes:
  1. The actor is `human`: the CLI sets `CHITTY_ACTOR=human` in its own process environment, runs the write, and restores the previous value (or removes the variable if it was unset) in a `try`/`finally`, so the override never outlives the command (`actor()` in `src/chitty/actor.py` already prefers `CHITTY_ACTOR`, and the store reads it during the write). History lines then read `human`, and review independence treats the edit as the person's.
  2. When the ticket's latest copy is on a branch other than the current one and a local worktree has that branch (the case where `_require_current_version` today says `run Chitty in worktree <path>`), the edit is made in that worktree: add `Repo.for_human_edit(task_id: TaskId) -> Repo` in `src/chitty/store.py`, which looks up the branch with `self.find(task_id).branch` and returns `Repo.open(<worktree>)` in that case and `self` otherwise, and have the CLI resolve the ID first (as `edit` in `src/chitty/cli.py` already does with `repo.resolve`), call `for_human_edit` with that `TaskId`, then call `edit` on the returned repo. Use `git.worktree_for_branch` as `_require_current_version` does. In every other case (ticket on the current branch, or its branch has no worktree) the write behaves as without the flag, including today's refusals.
- The output names the file written, as `chitty edit` already prints (`updated <ID> <path> actor <actor>`), so the path shows the worktree.
- In the worktree the edit behaves exactly as `chitty edit` run there, including its refusals (for example uncommitted changes); `--human` adds no new handling.
- Docs: in `README.md`, add an example line after `chitty edit 1 -s done --note ...` in the command examples (near line 59), such as `chitty edit 1 -s done --note "Reviewed: ok." --human  # a person, from the main checkout`, and the option's `--help` text: for people editing from the main checkout, for example to approve a review. Do not mention it in the agent guides (`src/chitty/guide.md`, `src/chitty/roles/`).
- `TASK-385` will replace `_require_current_version` with `_require_writable` and its `edit it in worktree <path>` message. `for_human_edit` only uses the worktree lookup, so it is unaffected; whichever lands second keeps both working.

Tests, new file `tests/test_edit_human.py`, inheriting `CliTestCase` from `tests/test_cli.py` (its `setUp` sets `CHITTY_ACTOR=test-agent` and changes into `self.root`). Fixture: `git init -b main`, user name and email set, `autocommit = true` in `chitty.toml`, `.worktrees/` written to `.gitignore` (as `tests/test_landing.py` does, so the main checkout stays clean), `add` tickets `TASK-1`, `TASK-2` and `TASK-3`, each with no criteria (so moving `review → done` needs only a note starting `Reviewed:`), commit everything, then `git worktree add -b task-1 .worktrees/task-1`. Inside the worktree (`os.chdir`, then back to `self.root`), `edit TASK-1 -s doing` and `edit TASK-1 -s review`, each committed by autocommit on `task-1` as actor `test-agent`.

- `test_human_edit_writes_in_the_worktree`: from `self.root`, `run_cli("edit", "TASK-1", "-s", "done", "--note", "Reviewed: ok", "--human")` exits 0 and its output contains `.worktrees/task-1`. Then `git show task-1:<path>`, where `<path>` is the file matching `chitty/tasks/TASK-1--*.md` (found with a glob, as `tests/test_landing.py` does), contains `status: done` and a history line containing `human review → done`; `git rev-parse main` is unchanged from before the command; `git status --porcelain` is empty in both checkouts; `os.environ["CHITTY_ACTOR"]` is still `test-agent` after the command (restore it, since `CliRunner` runs in this process). Without the change it fails: the option does not exist. Because `test-agent` moved the ticket to `review`, an implementation that writes in the worktree but leaves the actor alone is refused by review independence, so this test also covers the actor override.
- `test_edit_without_human_still_refuses`: the same command without `--human` exits 1 with `latest committed version is on branch task-1`.
- `test_human_edit_without_a_worktree_keeps_the_refusal`: on `main`, `git switch -c task-3`, `edit TASK-3 --note x` (committed on `task-3`), `git switch main`; no worktree has `task-3`. `edit TASK-3 --note y --human` exits 1 with `run \`git switch task-3\` first`, `git rev-parse task-3` and `main` are unchanged, and `os.environ.get("CHITTY_ACTOR")` is still `test-agent` (the restore also runs on refusal). Then delete `CHITTY_ACTOR` from `os.environ`, repeat the command, and assert the variable is absent afterwards (restore it for the other tests).
- `test_human_edit_of_a_ticket_on_main_uses_main`: `TASK-2` exists only on `main`; `edit TASK-2 --note x --human` from `self.root` writes on `main` and its history line contains `human`.

No property: a fixed set of three placements (ticket on the current branch, on a branch with a worktree, on a branch without one), each listed and tested. Without the change the first test fails only because the option is unknown (exit 2); that is the expected evidence, and the actor override is covered by review independence as above.

Out of scope: the remote-only refusal (`run \`git switch --track ...\` first`), which keeps its message untested here; the same flag on other commands (`archive`, `move`), the MCP front end, and `TASK-385`'s refusals.

## Acceptance Criteria

- [x] `test_human_edit_writes_in_the_worktree` passes with every assertion in the Description; a note records its failure against two mutants of the change: the worktree redirect disabled (`for_human_edit` returns `self`), and the actor override disabled (the edit is then refused by review independence, `moved the task to review`)
- [x] `test_edit_without_human_still_refuses`, `test_human_edit_without_a_worktree_keeps_the_refusal` and `test_human_edit_of_a_ticket_on_main_uses_main` pass
- [x] `chitty edit --help` and `README.md` describe `--human`; `git grep -n -- --human src/chitty/guide.md src/chitty/roles/` finds nothing; `make check` passes

## Plan

Add Repo.for_human_edit using the existing branch/worktree lookup, and add an explicit --human option to chitty edit. Resolve the task before selecting the target repo; scope CHITTY_ACTOR=human to the write and restore it in finally. Add the requested fixture-based regression tests in tests/test_edit_human.py, documenting the baseline and both mutants. Update README and option help, run focused tests and make check, record criterion evidence, then commit implementation changes with Task: TASK-470.

## Notes

Focused evidence: tests.test_edit_human passed all four tests. Mutation check ran test_human_edit_writes_in_the_worktree with Repo.for_human_edit replaced by self and with store.actor forced to test-agent; each mutant produced one failure. The clean baseline was not run before implementation; the ticket predicts the new option fails as unknown.

## Summary

Implemented explicit chitty edit --human with target-worktree selection and scoped actor restoration. Added four regression tests and README/help documentation. Verified by make check (787 tests), focused tests, CLI help, and no --human mentions in agent guides. Both required mutants fail the primary regression test. Follow-up: none.

## History

- 2026-11-19T22:04:44Z daring-amber-kestrel → planning
- 2026-11-19T22:04:56Z daring-amber-kestrel planning → cold-read
- 2026-11-19T22:05:53Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T22:05:53Z daring-amber-kestrel cold-read → planning
- 2026-11-19T22:06:02Z daring-amber-kestrel planning → cold-read
- 2026-11-19T22:07:06Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T22:07:06Z daring-amber-kestrel cold-read → planning
- 2026-11-19T22:07:10Z daring-amber-kestrel planning → cold-read
- 2026-11-19T22:08:26Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T22:08:26Z daring-amber-kestrel cold-read → planning
- 2026-11-19T22:08:30Z daring-amber-kestrel planning → todo
- 2026-11-20T00:06:05Z witty-ochre-kestrel todo → doing
- 2026-11-20T00:09:02Z witty-ochre-kestrel: wrote the plan
- 2026-11-20T00:12:43Z witty-ochre-kestrel: changed notes, summary; ticked acceptance criteria
