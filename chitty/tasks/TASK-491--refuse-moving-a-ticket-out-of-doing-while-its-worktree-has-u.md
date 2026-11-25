---
title: Refuse moving a ticket out of doing while its worktree has uncommitted changes
status: cold-read
labels:
  - bug
created: 2026-11-21
---

## Description

Seen 2026-11-20 on `TASK-347`: a worker moved it from `doing` to `planning` with about 70 lines of `src/chitty/cli.py` left uncommitted in its worktree. Three days later the diff no longer applied, and nothing had reported it. Leaving work uncommitted is a bug (the person, 2026-11-24).

Today `Repo._edit_stored` (`src/chitty/store.py`) refuses a move into `review`, or from `review` to `done`, while the checkout has uncommitted changes (`require_clean`). A move out of `doing` to any other status is not checked.

Change: in `Repo._edit_stored`, refuse an edit that moves a ticket out of `doing` while the checkout has uncommitted changes (`git.uncommitted_paths`), when all of these hold:

- the status before the edit is `doing`, and `edit.status` is not `None`, `doing` or `review` (`review` keeps its own check);
- `edit.skip_current_version` is false (the runner's own edits set it);
- the checkout is on the ticket's own branch: `self._current_branch() == str(task_id).lower()`, so edits from the main checkout or other branches are unaffected.

Use the same message as `require_clean`: `cannot move <ID> to <status>; the worktree has uncommitted changes: <paths>. Commit or resolve them before changing status`. Nothing is written or committed. Refuse rather than warn, to match the review refusal.

This is already implemented on branch `task-491` (commit `5eb3db64`); check it against the above and keep it. With it, `make check` fails only `test_run_forwards_arguments_and_uses_a_fresh_actor_per_invocation` in `tests/test_next.py`: its fake agent writes probe files (`pi-arguments`, `run-actor`, `child-actor`, `pi-session-id`) into the worktree and then moves the ticket to `blocked`. That is the behaviour this ticket refuses, so fix the fixture, not the rule: after the setup commit, append those four names to `.git/info/exclude` in `self.root` (worktrees share it). A trial (2026-11-25) showed this makes the test pass.

Out of scope: guides, `review` and `done`, `chitty run`, and how Git quotes unusual paths.

Tests: CLI examples in a new `tests/test_leave_doing_clean.py`, class inheriting `CliTestCase` from `tests/test_cli.py`. Fixture per case: set `autocommit = true` in the `chitty.toml` the class writes, `git init -b main` with user name and email, commit, `chitty add One -d x -s todo`, `chitty edit TASK-1 -s doing`, then `git worktree add -b task-1 .worktrees/task-1 main`. No property: the rule covers a small fixed set of statuses and cases, each listed and tested.

- Refused: for each status in `STATUSES` other than `doing`, `review` and `done` (a `subTest` each, own fixture), with an untracked `left.py` in the worktree, `chitty edit TASK-1 -s <status> --note reason` run there exits non-zero, names `` `left.py` `` and `uncommitted changes`, leaves the worktree `HEAD` unchanged, and `chitty show TASK-1` still says `doing` without `reason`.
- Allowed (regression tests): a clean worktree moving to `todo`; a note-only edit with `left.py` present; with the ticket already `todo`, `left.py` present, a move to `planning`; from the main checkout with an untracked `scratch.txt` there, a move to `planning`; `Repo.open(worktree).edit(TASK-1, Edit(status="error", note="runner", skip_verdicts=True, skip_current_version=True))` with `left.py` present.

## Acceptance Criteria

- [ ] The refused cases in `tests/test_leave_doing_clean.py` pass, and fail with the `store.py` change reverted
- [ ] Regression tests: the allowed cases, and `test_run_forwards_arguments_and_uses_a_fresh_actor_per_invocation` with its fixture fix, pass; `make check` passes

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
- 2026-11-24T12:46:04Z nimble-zinc-vole: changed owner, notes
- 2026-11-24T12:46:04Z nimble-zinc-vole doing → planning
- 2026-11-25T21:21:15Z daring-ebony-wren: replaced notes; changed owner, description, acceptance criteria; wrote the plan
- 2026-11-25T21:21:15Z daring-ebony-wren planning → cold-read
