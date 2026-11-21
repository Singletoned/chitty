---
title: Test archiving a referenced ticket and reading an archive from an older worktree
status: doing
labels:
  - bug
  - escape
priority: high
depends_on:
  - TASK-378
created: 2026-11-17
---

## Description

Two archive failures, both reproduced on `main` on 2026-11-21 (chitty at `b0c849b2`):

1. In a repository with no other branch and `autocommit = true`: add `TASK-1`, add `TASK-2 --parent TASK-1`, set `TASK-1` to `done`, then `chitty archive TASK-1` fails with `TASK-1 is used by more than one file: <active path>, <archive path>`. Nothing is committed and `git status` is clean, but the ticket cannot be archived. The failure is in the check that `_commit` runs (`check.fix` → `check.check` → `Repo.lookup`, `src/chitty/store.py`): `lookup` takes candidates from `_tasks_in_location`, which still sees `main`'s committed active copy beside the moved file. So any ticket that another ticket names as `parent` or in `depends_on` cannot be archived.
2. In a ticket worktree made before `main` archived `TASK-2`, `chitty edit TASK-1 --depends-on TASK-2` and `chitty show TASK-2` fail the same way, naming the worktree active file and `main`'s archived one.

`TASK-378` fixes both: it reads each ticket from one source (this checkout's working tree on `main` or on the ticket's own branch, otherwise `main`'s tip), so a ticket has one copy. This ticket adds no code. It adds regression tests that fail today and pass once `TASK-378` has landed, so the two cases cannot come back. It replaces the earlier plan for this ticket, a version-choosing function, which `TASK-378` makes unnecessary.

Decisions:

- New `tests/test_archive_referenced_tickets.py`, a class inheriting `CliTestCase` from `tests/test_cli.py`. `setUp` follows `tests/test_run_claims_on_branch.py`: replace `autocommit = false` with `autocommit = true` in `chitty.toml`, `git init --quiet -b main`, set `user.email` and `user.name`, then `run_cli("init")` and commit it. A helper sets a ticket to `done` with `run_cli("edit", <ID>, "-s", "review")` then `run_cli("edit", <ID>, "-s", "done", "--human", "--override-review-independence", "--note", "Reviewed: ok")`.
- `test_archive_ticket_named_as_parent`: add `One`, add `Two` with `--parent TASK-1`, set `TASK-1` done, `run_cli("archive", "TASK-1")` exits 0. Then `git status --short` is empty, `git ls-files chitty/tasks` lists `chitty/tasks/archive/TASK-1--one.md` and not `chitty/tasks/TASK-1--one.md`, the last commit subject starts with `chitty: archive TASK-1`, and `json("show", "TASK-1")["archived"]` is `True`.
- `test_archive_ticket_named_in_depends_on`: the same as `test_archive_ticket_named_as_parent`, but `Two` is added with `--depends-on TASK-1` instead of `--parent`.
- `test_archive_all_done_when_one_is_a_parent`: the same tickets, then `run_cli("archive")` with no ID exits 0, `git status --short` is empty, `TASK-1` is archived and `TASK-2` (not done) is still active.
- `test_older_worktree_sees_ticket_archived_on_main`: add `One` and `Two`, set `TASK-2` done, `git worktree add --quiet .worktrees/task-1 -b task-1`, then `run_cli("archive", "TASK-2")` in the main checkout. In the worktree (`os.chdir(worktree)` with `self.addCleanup(os.chdir, self.root)`, as `tests/test_cli.py` near line 384 does; `run_cli` runs in-process and uses the current directory), `edit TASK-1 --depends-on TASK-2` exits 0 and `show TASK-2 --json` reports `archived` `True`.
- No property: three fixed placements with real Git; `TASK-393` owns the generated property over placements.
- If, once `TASK-378` has landed, any of these tests still fails, return this ticket to `planning` naming the read that fails, rather than changing store code here.
- Out of scope: archiving a ticket from inside its own ticket worktree, and listings (`TASK-480`).

## Acceptance Criteria

- [ ] The four tests in `tests/test_archive_referenced_tickets.py` pass with `TASK-378` landed; a note records that each fails, with `is used by more than one file`, when run in a temporary worktree at the parent of `TASK-378`'s first landed commit, `$(git log --reverse --format=%H --grep "Task: TASK-378" main | head -1)^`
- [ ] `make check` passes, and `git diff --name-only main...HEAD` lists only paths under `tests/` and `chitty/` (the revert of `0c9354ac` cancels its `src/` changes)

## Plan

Revert the superseded selector work, merge the landed dependency, add the four specified real-Git regression tests, verify each against the pre-TASK-378 revision, and run the required checks.

## Notes

Also seen 2026-11-17: in the `task-364` worktree, which branched before `TASK-356` was archived on `main`, `chitty edit TASK-364 --note ...` failed with `TASK-356 is used by more than one file` (the local active file and `main`'s archived one), after writing the note to the ticket file and without committing it, despite `TASK-355`. So every worktree created before an archive on `main` cannot edit any ticket until it merges `main`.

Escape: introduced by `TASK-356`, whose cross-branch `lookup` in `check` made archiving a referenced ticket fail. Cold read by a Haiku subagent, 2026-11-17. Fixed: neither real-Git test failed before the change as first written (a plain archive and a plain edit both work), so the tests now use the reproduction, found by the planner; `autocommit = true` for the clean-status check; tie-breaking and detached HEAD; how a `Version` maps back to a ticket and which historical versions are candidates; the outcome when another branch edits an archived ticket (accepted, stated). Not adopted: a repository-level property over `tasks`; the unit properties and two real tests cover it.

Planning return: the selector rule and older-version property conflict when the input contains only a clean local version. The rule says a historical version from another branch wins over a clean local version; adding any historical candidate therefore changes the result, even if it is older than every existing candidate (the local candidate has no committed_at). The property requires adding such an older historical version never to change the choice. Please decide whether that property applies only when at least one historical candidate already exists, or revise the selection rule for local-versus-historical comparison. Also, make check currently fails the existing TestRenumber duplicate-file diagnostic assertion after the selector change; determine the expected diagnostic path while refining the design. Partial implementation is committed as 0c9354ac; property tests and the first real-Git reproduction pass, but the full check and second regression evidence are incomplete.

Same-checkout case still exists: Reproduced 2026-11-18 in `.worktrees/task-359` (branch `task-359`, clean worktree, ticket committed there and also present on `main`): `chitty edit TASK-359 --note ...` succeeded, then `chitty archive TASK-359` failed with `TASK-359 is used by more than one file: .../chitty/tasks/TASK-359--....md, .../chitty/tasks/archive/TASK-359--....md`, leaving the active file deleted and the archive file untracked, uncommitted. The same command on `main` for `TASK-366` (also on branch `task-366`) succeeded. Undone by hand with `git restore` and `rm`.

Planning 2026-11-20: superseded by `TASK-378` (single-ticket reads from one authoritative source) and `TASK-480` (listings), which replace the history-based version choice this ticket would change. Its two real-Git scenarios (archiving `TASK-1` while `TASK-2` has `parent: TASK-1` with autocommit; editing in a worktree made before `main` archived a ticket) are recorded on `TASK-480` as regression tests. Archive this once `TASK-480` lands.

Planner, 2026-11-21: re-planned as regression tests only, depending on `TASK-378`. Both cases reproduced on `main` today. Branch `task-367` holds a partial implementation of the superseded design (`0c9354ac`): revert it first (`git revert --no-edit 0c9354ac`, with a `Task: TASK-367` trailer) so the branch changes no store code. The scenarios previously recorded on `TASK-480` live here now.

Cold read 2026-11-21 outcomes: net diff against `main` for the path check; `os.chdir` pattern named; a `depends_on` variant; archive-all keeps the non-done ticket active; the command that finds the commit before `TASK-378`. Stays behind `TASK-378` through `depends_on`; the runner will not start it before then.

Check failed before this session: check exited with status 2; output in `.chitty/check.log`

Planning return: the specified regression evidence contradicts the prescribed fixture. All four tests pass on the merged main with TASK-378, but running the exact tests at the parent of the first TASK-378 commit (cae058f9) fails during the done helper: the historical CLI does not have --human, so each reports "No such option --human" before reaching archive or the older-worktree read, not "is used by more than one file". Decide how to adapt the historical fixture or revise the evidence requirement without changing what is tested. The four tests and the revert of the superseded selector are committed; make check passes (909 tests). Regression evidence and the acceptance criteria remain unfinished.

## History

- 2026-11-17T19:53:05Z kind-umber-toad → todo
- 2026-11-17T19:59:48Z kind-umber-toad: changed priority, notes
- 2026-11-17T20:00:40Z kind-umber-toad: changed title, description, acceptance criteria
- 2026-11-17T20:00:40Z kind-umber-toad todo → planning
- 2026-11-17T20:00:42Z kind-umber-toad: changed owner
- 2026-11-17T20:00:42Z kind-umber-toad planning → cold-read
- 2026-11-17T20:05:01Z kind-umber-toad: changed labels, description, acceptance criteria, notes
- 2026-11-17T20:05:01Z kind-umber-toad cold-read → planning
- 2026-11-17T20:22:20Z kind-umber-toad: changed owner
- 2026-11-17T20:22:20Z kind-umber-toad planning → todo
- 2026-11-17T22:03:54Z witty-ochre-yellowhammer todo → doing
- 2026-11-17T22:04:06Z witty-ochre-yellowhammer: wrote the plan
- 2026-11-17T22:10:39Z witty-ochre-yellowhammer: changed owner, notes
- 2026-11-17T22:10:39Z witty-ochre-yellowhammer doing → planning
- 2026-11-18T16:25:59Z lively-quartz-crane: changed notes
- 2026-11-20T23:20:45Z quick-pearl-lapwing: changed notes
- 2026-11-20T23:20:45Z quick-pearl-lapwing planning → backlog
- 2026-11-21T08:04:54Z nimble-umber-gannet: changed title, dependencies, description, acceptance criteria, notes; wrote the plan
- 2026-11-21T08:04:54Z nimble-umber-gannet backlog → cold-read
- 2026-11-21T08:08:45Z nimble-umber-gannet: changed description, acceptance criteria, notes
- 2026-11-21T08:08:45Z nimble-umber-gannet cold-read → todo
- 2026-11-21T12:31:41Z quick-ginger-jay todo → doing
- 2026-11-21T12:32:19Z quick-ginger-jay: changed notes
- 2026-11-21T12:32:51Z quick-ginger-jay: wrote the plan
- 2026-11-21T12:35:56Z quick-ginger-jay: changed notes
