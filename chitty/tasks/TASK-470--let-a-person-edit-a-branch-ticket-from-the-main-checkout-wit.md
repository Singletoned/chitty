---
title: Let a person edit a branch ticket from the main checkout with `chitty edit --human`
status: planning
priority: high
created: 2026-11-19
---

## Description

A person reviewing from the main checkout cannot edit a ticket whose latest copy is on its branch. `chitty edit TASK-420 -s done --note '...'` refuses with `TASK-420's latest committed version is on branch task-420; run Chitty in worktree <path>` (`Repo._require_current_version` in `src/chitty/store.py`), so on 2026-11-19 the owner had to type `cd .worktrees/task-463 && ../../.venv/bin/chitty edit TASK-463 ...` for each review. Commands a person runs inside an agent session (Claude Code's `!`) also get that session's actor name (`actor()` in `src/chitty/actor.py` derives it from the harness identity), so the review-independence rule treats the person as the agent that moved the ticket to `review`: the owner's `chitty edit TASK-404 -s done` was refused that way. The owner wants the convenience behind an explicit flag, so agents do not edit tickets in other worktrees by accident.

Decisions:

- New flag `--human` on `chitty edit` only (`src/chitty/cli.py`). It does two things for that one command, and nothing without it changes:
  1. The actor is `human`: the CLI sets `CHITTY_ACTOR=human` in its own process environment before the write, overriding any existing value (`actor()` already prefers `CHITTY_ACTOR`). History lines then read `human`, and review independence treats the edit as the person's.
  2. When the ticket's latest copy is on a branch other than the current one and a local worktree has that branch (the case where `_require_current_version` today says `run Chitty in worktree <path>`), the edit is made in that worktree: add `Repo.for_human_edit(task_id: TaskId) -> Repo` in `src/chitty/store.py`, which returns `Repo.open(<worktree>)` in that case and `self` otherwise, and have the CLI call it before `edit`. Use `git.worktree_for_branch` as `_require_current_version` does. In every other case (ticket on the current branch, or its branch has no worktree) the write behaves as without the flag, including today's refusals.
- The output names the file written, as `chitty edit` already prints (`updated <ID> <path> actor <actor>`), so the path shows the worktree.
- In the worktree the edit behaves exactly as `chitty edit` run there, including its refusals (for example uncommitted changes); `--human` adds no new handling.
- Docs: in `README.md`, add an example line after `chitty edit 1 -s done --note ...` in the command examples (near line 59), such as `chitty edit 1 -s done --note "Reviewed: ok." --human  # a person, from the main checkout`, and the option's `--help` text: for people editing from the main checkout, for example to approve a review. Do not mention it in the agent guides (`src/chitty/guide.md`, `src/chitty/roles/`).
- `TASK-385` will replace `_require_current_version` with `_require_writable` and its `edit it in worktree <path>` message. `for_human_edit` only uses the worktree lookup, so it is unaffected; whichever lands second keeps both working.

Tests, new file `tests/test_edit_human.py`, inheriting `CliTestCase` from `tests/test_cli.py` (its `setUp` sets `CHITTY_ACTOR=test-agent` and changes into `self.root`). Fixture: `git init -b main`, user name and email set, `autocommit = true` in `chitty.toml`, `.worktrees/` written to `.gitignore` (as `tests/test_landing.py` does, so the main checkout stays clean), `add` ticket `TASK-1` with no criteria (so moving `review → done` needs only a note starting `Reviewed:`), commit everything, then `git worktree add -b task-1 .worktrees/task-1`. Inside the worktree (`os.chdir`, then back to `self.root`), `edit TASK-1 -s doing` and `edit TASK-1 -s review`, each committed by autocommit on `task-1` as actor `test-agent`.

- `test_human_edit_writes_in_the_worktree`: from `self.root`, `run_cli("edit", "TASK-1", "-s", "done", "--note", "Reviewed: ok", "--human")` exits 0 and its output contains `.worktrees/task-1`. Then `git show task-1:<path>` contains `status: done` and a history line containing `human review → done`; `git rev-parse main` is unchanged from before the command; `git status --porcelain` is empty in both checkouts; `os.environ["CHITTY_ACTOR"]` is still `test-agent` after the command (restore it, since `CliRunner` runs in this process). Without the change it fails: the option does not exist. Because `test-agent` moved the ticket to `review`, an implementation that writes in the worktree but leaves the actor alone is refused by review independence, so this test also covers the actor override.
- `test_edit_without_human_still_refuses`: the same command without `--human` exits 1 with `latest committed version is on branch task-1`.
- `test_human_edit_of_a_ticket_on_main_uses_main`: with a second ticket `TASK-2` that exists only on `main`, `edit TASK-2 --note x --human` from `self.root` writes on `main` and its history line contains `human`.

No property: a fixed set of three placements (ticket on the current branch, on a branch with a worktree, and the refusals for the rest, which are unchanged), each listed and tested.

Out of scope: the same flag on other commands (`archive`, `move`), the MCP front end, and `TASK-385`'s refusals.

## Acceptance Criteria

- [ ] `test_human_edit_writes_in_the_worktree` passes with every assertion in the Description; a note records the command run against the code without the change and its failing output
- [ ] `test_edit_without_human_still_refuses` and `test_human_edit_of_a_ticket_on_main_uses_main` pass
- [ ] `chitty edit --help` and `README.md` describe `--human`; `git grep -n -- --human src/chitty/guide.md src/chitty/roles/` finds nothing; `make check` passes

## History

- 2026-11-19T22:04:44Z daring-amber-kestrel → planning
- 2026-11-19T22:04:56Z daring-amber-kestrel planning → cold-read
- 2026-11-19T22:05:53Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T22:05:53Z daring-amber-kestrel cold-read → planning
