---
title: Edit existing tickets in planning worktrees
status: done
parent: TASK-376
created: 2026-11-21
---

## Description

Let planners revise existing tickets from separate Git worktrees on local branches with nonempty names under `plan/`. Scope the exception to `chitty edit ID` (without `--human`) and `chitty show ID`, plain and JSON. Read the target from the planning checkout, by ID using the existing working-tree parser and errors; a local draft is also what a cold reader sees when it runs `show` from that worktree. Never use a competing ref as the target of a planning edit. Preserve existing `show` output and normal `edit` validation, History and autocommit. If no local copy exists, planning `edit` refuses with a path/context diagnostic; `show` can use its normal source fallback. Do not change runner discovery, normal authoritative source selection outside these entry points, other writes or `--human` routing. Landing is ordinary Git integration, not a new command.

Before the planning edit can prepare or write files, examine locally visible branch tips (`git.branch_tips`): local and remote-tracking branches other than this branch and its same-named remote counterparts; exclude symbolic remote HEAD aliases. Include configured main, sibling plans, ticket and feature branches. A competing ref conflicts if its tree differs from its merge base with the planning HEAD for this ticket ID. Use matching ticket paths in the merge-base and competing trees, across active/archive contexts, so renames, moves and deletions count even if they do not affect the draft filename. No conflict just for a branch existing, being an ancestor, or editing something else. Skip refs with unrelated histories (no merge base); propagate actual Git command failures. If any conflict is found, report the ID and a conflicting ref and refuse the edit. This is a guard against visible committed changes, not a lock; ordinary Git integration must still handle concurrent commits.

Independently, if `locks.holder` reports a live runner lock for the target ID, an otherwise allowed edit warns on stderr that work or review is in progress and to coordinate. Do not warn merely because a branch exists. Use a narrow store/CLI boundary so warning output stays in the CLI. No new options, commands or locks.

Create `tests/test_planning_worktrees.py` with `CliTestCase`, real Git/worktrees, current committed setup with autocommit on and a local Git author. The following are fixed integration cases because each checks a distinct Git placement or real lock lifecycle, not a new pure policy. Run new tests before the change: draft editing and the warning must fail for the stated behavior, not setup errors. For conflict regressions, a targeted test variant bypassing the new conflict guard must make the conflict assertions fail (commit the negative control with the other new tests, using a test-local patch in that file; do not add a production bypass); the old code already rejects these edits for a different reason. Then run `make check`.

Isolation: commit `TASK-1` and `TASK-2` on main, create `plan/one` in a linked worktree and edit `TASK-1`'s title there. Run plain and JSON `show` in that worktree (the cold reader uses plain show). Assert the title and new path match the draft, the planning HEAD advanced by one commit, and main HEAD, bytes and JSON title are unchanged. Confirm main `Repo.lookup` reads the main copy. In a separate ordinary `feature` worktree confirm `edit` does not gain the exception.

Conflict matrix: use fresh repos or reset refs between cases. Start with the same two tickets, branch `plan/one` before the competing commit and invoke `edit TASK-1` there. Separately change `TASK-1`'s body on main; rename its filename and title on `plan/two`; delete it on `task-1`; and change its body on a feature branch visible only as `refs/remotes/origin/feature`. A positive control creates `plan/two` with only a `TASK-2` change and an idle `task-1` at the old tip. Snapshot HEAD, index, and ticket bytes after arranging each refusing fixture, and assert they do not change.

Lock: in the positive control perform three distinct notes on `TASK-1`, first with just the idle `task-1`, second inside `locks.run_lock(main_root, "TASK-1", actor="other-worker", mode="work")`, third after releasing it. Assert each note is committed and only the middle command warns. Do not spawn a worker or reviewer.

## Acceptance Criteria

- [ ] In the isolation fixture, `edit` commits on the planning branch, plain and JSON `show` there report its draft, and main still reports its original bytes and title. Main discovery does not see the draft as a competing source.
- [ ] In each conflict fixture, `edit` exits 1 naming the competing ref and ticket ID and preserves planning HEAD, index, and ticket bytes; an unchanged sibling and a sibling changing another ID allow the edit.
- [ ] The runner-lock fixture permits each edit. Only the edit while the real lock is held produces a coordinate-before-editing warning on stderr; an existing idle ticket branch and a released lock do not warn.

## Plan

Prove planning worktree isolation, conflicts and lock warnings with real Git; add narrow planning-only CLI and store paths; verify the tests and hand off for review.

## Notes

Blocked: the execution harness is repeatedly limiting this session to an analysis budget insufficient to implement and verify the requested integration work. The person operating the harness needs to start a session with sufficient budget; no implementation or verification has been completed.

Reviewed: make check passed (1008 tests, Ruff and Pyright). Worker reports initial regressions failed on unchanged CLI; the committed guard-bypass negative control passes by observing the conflict assertion fail.
1: pass - test_isolated_edit_and_show verifies draft show, commit, main bytes and lookup; worker reports original CLI refused the edit.
2: pass - conflict matrix and guard-bypass negative control pass in make check; the bypass causes the expected exit-code assertion failure.
3: pass - test_idle_branch_and_live_runner_lock passes in make check; worker reports the warning regression failed before implementation.

## Summary

Implemented planning-worktree edits and draft display without changing source selection for the runner or other checkouts. Competing local and remote changes to the same ticket refuse the edit before mutations. A real runner lock warns without blocking; an idle ticket branch does not warn.

The six initial regressions failed on the unchanged CLI (latest-version refusal or missing conflict diagnostic). The committed negative control confirms the conflict assertions fail when the guard is bypassed. The seven new tests and `make check` pass (1,008 tests, Ruff and Pyright). Implementation commit: `914c45c9`.

## History

- 2026-11-21T22:26:20Z eager-ginger-adder → backlog
- 2026-11-21T22:26:38Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T22:26:38Z eager-ginger-adder backlog → planning
- 2026-11-21T22:28:54Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T22:28:54Z eager-ginger-adder planning → cold-read
- 2026-11-21T22:29:54Z eager-ginger-adder: changed description
- 2026-11-21T22:29:54Z eager-ginger-adder cold-read → planning
- 2026-11-21T22:29:57Z eager-ginger-adder planning → todo
- 2026-11-21T22:30:50Z honest-umber-falcon todo → doing
- 2026-11-21T22:33:20Z honest-umber-falcon: changed notes
- 2026-11-21T22:33:20Z honest-umber-falcon doing → blocked
- 2026-11-21T22:45:22Z eager-ginger-adder: changed owner; wrote the plan
- 2026-11-21T22:45:22Z eager-ginger-adder blocked → doing
- 2026-11-21T22:50:16Z eager-ginger-adder: changed summary
- 2026-11-21T22:50:16Z eager-ginger-adder doing → review
- 2026-11-21T22:53:22Z tidy-bronze-vole: changed notes
- 2026-11-21T22:53:22Z tidy-bronze-vole review → done
