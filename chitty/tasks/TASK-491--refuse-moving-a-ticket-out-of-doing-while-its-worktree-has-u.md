---
title: Refuse moving a ticket out of doing while its worktree has uncommitted changes
status: doing
labels:
  - bug
created: 2026-11-21
---

## Description

Seen 2026-11-20 on `TASK-347`. On 2026-11-17 a worker moved it `doing` to `planning` with about 70 lines of `src/chitty/cli.py` changes left uncommitted in `.worktrees/task-347`. Three days later the branch was 1324 commits behind `main`, the diff no longer applied, and nothing had reported the stale dirty worktree; it blocked `TASK-348` silently. Recovered by committing the work, tagging it `task-347-partial`, and removing the worktree and branch.

Today `Repo._edit_stored` (`src/chitty/store.py`) refuses only a move into `review`, or from `review` to `done`, while the checkout has uncommitted changes (`require_clean`, since `80ce143`, 0.1.47); since then no worker has reached `review` with uncommitted work. A move out of `doing` to any other status is not checked. Probed on `main` at `2301445a` (2026-11-24): in a `task-1` worktree with an untracked `left.py`, `chitty edit TASK-1 -s <status> --note reason` from `doing` succeeds for each of `backlog`, `planning`, `cold-read`, `todo`, `blocked` and `error`, and leaves `left.py` uncommitted.

Change: in `Repo._edit_stored`, after the existing `setting status done requires -s review first` check and before the review check (`entering_review`), refuse an edit that moves a ticket out of `doing` while the checkout has uncommitted changes, when all of these hold:

- the ticket's status before the edit is `doing`, and `edit.status` is not `None`, `doing` or `review` (`review` keeps its own check);
- `edit.skip_current_version` is false (the runner's own edits set it, as the review check already relies on);
- the checkout is a Git repository on the ticket's own branch: `self._current_branch() == str(task_id).lower()`. Edits from the main checkout or any other branch are unaffected, so a person with unrelated changes in the main checkout can still move a ticket.

The refusal uses `git.uncommitted_paths(self.root)` and the same message as `require_clean`: `cannot move <ID> to <status>; the worktree has uncommitted changes: <paths>. Commit or resolve them before changing status`, with each path in backticks joined by `, `. Nothing is written or committed. Decided: refuse, not warn, to match the review refusal, because a worker who leaves `doing` with uncommitted work loses it (the person, 2026-11-24: leaving things uncommitted is a bug); `src/chitty/roles/work.md` already tells workers to commit intended partial work before setting `planning`, and is unchanged.

Out of scope: paths Git quotes in `git status --porcelain` (listed as Git prints them, as `require_clean` does); `done` from `doing`, which the earlier check already refuses; the guides; `review` and `done` (unchanged); `chitty run` (its edits set `skip_current_version`).

Tests: CLI examples in a new `tests/test_leave_doing_clean.py`, class inheriting `CliTestCase` from `tests/test_cli.py`. Fixture, fresh for each case: `CliTestCase` already writes `chitty.toml` from `CONFIG` (`tests/support.py`); keep it and replace `autocommit = false` with `autocommit = true`, then run `git init -b main` with user name and email in `self.root` and commit everything; `chitty add One -d x -s todo`, then `chitty edit TASK-1 -s doing`; `git worktree add -b task-1 .worktrees/task-1 main`. Run commands with the working directory set to the named checkout. No property: the rule depends on a small fixed set of cases, each listed and tested:

1. For each status in `STATUSES` other than `doing`, `review` and `done`, as a `subTest` with its own fixture: write an untracked `left.py` in the worktree and run `chitty edit TASK-1 -s <status> --note reason` there. It exits non-zero, the output names `` `left.py` `` and `uncommitted changes`, the worktree `HEAD` is unchanged, and `chitty show TASK-1` still says `doing` and does not contain `reason`. Each fails today.
2. Guards, each passing today:
   - clean worktree: `-s todo --note reason` in the worktree succeeds (wrong version W1: always refusing);
   - note-only edit: with `left.py` present, `chitty edit TASK-1 --note progress` in the worktree succeeds (W2: refusing any edit of a `doing` ticket);
   - not leaving `doing`: after moving the ticket to `todo` with the worktree clean, write `left.py` and run `-s planning --note reason` in the worktree; it succeeds (W3: ignoring the previous status);
   - main checkout: with an untracked `scratch.txt` in `self.root`, `chitty edit TASK-1 -s planning --note reason` run from `self.root` succeeds (W4: refusing on any branch);
   - runner edit: with `left.py` present, `Repo.open(worktree).edit(TASK-1, Edit(status="error", note="runner", skip_verdicts=True, skip_current_version=True))` succeeds (W5: ignoring `skip_current_version`).

Probed while planning with this recipe: every case in 1 fails on `main` and passes with the change; the guards pass on both. Run each guard once against its wrong version as an uncommitted edit, restore the tree, and record the results in a note.

## Acceptance Criteria

- [ ] The cases in 1 pass and fail on `main`; each guard in 2 passes and fails against its wrong version; a note records the runs
- [ ] `make check` passes

## Plan

Read the existing clean-worktree guard and CLI test fixtures. Add the specified regression cases, first verify they fail against current behavior and each guard fails against its stated wrong version, then implement the status/branch/runner-gated refusal. Run make check and commit implementation changes in small logical commits.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:53Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:54Z nimble-umber-gannet: changed notes
- 2026-11-24T12:24:27Z kind-navy-toad: changed title, labels, description, acceptance criteria
- 2026-11-24T12:24:27Z kind-navy-toad backlog → planning
- 2026-11-24T12:24:30Z kind-navy-toad planning → cold-read
- 2026-11-24T12:25:59Z kind-navy-toad: changed description
- 2026-11-24T12:25:59Z kind-navy-toad cold-read → todo
- 2026-11-24T12:30:33Z nimble-zinc-vole todo → doing
- 2026-11-24T12:33:00Z nimble-zinc-vole: wrote the plan
