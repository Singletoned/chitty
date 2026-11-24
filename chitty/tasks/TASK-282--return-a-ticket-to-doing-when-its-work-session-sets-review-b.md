---
title: Return a ticket to doing when its work session sets review but leaves uncommitted changes
status: review
labels:
  - bug
created: 2026-11-11
---

## Description

`TASK-167` went to `review` three times with its changes verified but never committed. Each review start found the dirty worktree and blocked it for a human (`_block_dirty_review` in `src/chitty/run.py`), and the next work session repeated the mistake. Probed on `main` at `80f6f701` (2026-11-24) with the fake agent from `tests/test_run_continue.py`: a work session that sets the ticket to `review` and leaves an untracked `left.py`, or an uncommitted change to a tracked file, ends with the ticket in `review` and the files still uncommitted in its worktree.

Change: when a work session ends with its ticket in `review` and its worktree has uncommitted changes, `chitty run` moves the ticket back to `doing` with a note naming the files, so the next work session commits them instead of a review blocking it for a human.

- Add `_return_uncommitted_work(work_repo: Repo, worktree: Path, action: NextAction, old_status: str) -> RunResult | None` next to `_block_dirty_review`, shaped like it: return `None` when `git.uncommitted_paths(worktree)` is empty; otherwise edit the ticket to `doing` with `skip_verdicts=True` and `skip_current_version=True` and the note `Returned to doing (work): the session set review but left uncommitted changes: <paths>. Commit them, or delete any that are not part of the work, then set the ticket to review again.`, where `<paths>` lists each path in backticks joined by `, ` as `_block_dirty_review` does. Return `RunResult(action, old_status, change.task.task.frontmatter.status)`, where `change` is the edit's result: use the `old_status` parameter, not a status read from `work_repo`, so the run reports the ticket's status before the session, not `review`. The runner moves a `todo` ticket to `doing` before the agent starts, so this prints `<id>: doing → doing`.
- Call it in the function that runs the agent (the one containing `new_status = _agent_sessions(`), after the `if repairing:` blocks and before `status_outcome(old_status, new_status) == "land"`, only when `action.mode == "work"`, `not repairing` and `new_status == "review"`. Pass `Repo(worktree, main_repo.config)` as the repair-blocked branch does, and that function's `old_status` (read before `_agent_sessions`). When it returns a result, set `new_status` to the result's `new_status` (so `_record_usage` records it) and return that result as the run's result (use the existing `handoff` variable).
- The runner leaves the files themselves alone: it neither commits, stages nor deletes them.
- Decided: this return counts as a failed review. `store.py` `_escalate_repeated_failure` counts every `review → doing` transition since the last `blocked`, and turns the third (`REVIEW_FAILURE_LIMIT`) into `blocked` for `human` with an `Escalated to human review` note. That bounds a worker that keeps leaving files uncommitted (`TASK-167` looped three times), so keep it, and add no bypass. `tests/test_check_edit.py` covers the limit; this ticket adds no escalation test (a test of three runner returns in a row needs a review history the fake agent cannot easily build), so the helper must report the status the edit produced, never a hard-coded `doing`. A `ChittyError` from the edit is recorded as a ticket error, as other edits in that `try` block are.

Out of scope: paths Git quotes in `git status --porcelain` (listed as Git prints them, as `_block_dirty_review` does); repair sessions (`repairing`); review sessions (unchanged `_block_dirty_review`); a session ending in any status other than `review`. Known interaction, not changed here: when the next work session starts on the `doing` ticket, the pre-session check may fail on the uncommitted files and send the ticket to `error`; that is `TASK-369`.

Tests: add to class `TestRunContinue` in `tests/test_run_continue.py`, using its `write_fake` fake agent. Before the run, commit a tracked file `tracked.py` (`changed = False`) on `main`. The fake runs its `edit` snippet in the worktree, then stages only the ticket file and commits, so files the snippet writes stay uncommitted. Snippets: status, `text = text.replace('status: doing', 'status: review')` (or `'status: blocked'`); untracked, `Path('left.py').write_text('x = 1\n')`; modified, `Path('tracked.py').write_text('changed = True\n')`. `setUp` commits only the config, so commit `tracked.py` in the test body. Run `chitty run --ticket <id>`, then read the status with `chitty show`, the note, and `git status --porcelain` in `.worktrees/<id>`. No property: the behaviour depends on a small fixed set of cases, each listed and tested as a `subTest`:

| status the agent sets | worktree state left | expected ticket status | note |
| --- | --- | --- | --- |
| `review` | untracked `left.py` | `doing` | contains `Returned to doing (work)` and `` `left.py` `` |
| `review` | `tracked.py` modified, not staged | `doing` | contains `Returned to doing (work)` and `` `tracked.py` `` |
| `review` | clean | `review` | no `Returned to doing` note |
| `blocked` | untracked `left.py` | `blocked` | no `Returned to doing` note |

In the two `doing` rows the run's last output line is `<id>: doing → doing` and the fake was invoked exactly once (`len(self.invocations_seen()) == 1`). In every case `git status --porcelain` in the worktree is unchanged by the runner: `?? left.py`, ` M tracked.py`, or empty, as left. The first two rows fail today (the ticket stays `review`); the third and fourth pass today and guard wrong versions W1 (returning on any status, not only `review`, caught by the `blocked` row) and W2 (returning whenever the session ends, dirty or clean, caught by the clean row). Run the test once against W1 and W2 as uncommitted edits, without committing them, and record the results in a note.

## Notes

Dropped 2026-11-24 with the person: not needed. Since `80ce143` (2026-11-09 21:08, released in 0.1.47) `chitty edit -s review` refuses while the worktree has uncommitted changes (`Repo.edit` in `src/chitty/store.py`, `require_clean`), so a worker cannot reach `review` with uncommitted files. Every occurrence of `Review failed (work): the worktree has uncommitted changes` in chitty, echonomicon, chladnify and mullion (12, including `TASK-167`) is from 2026-11-06 to 2026-11-09, the last at 20:43 on 2026-11-09, before that release; none since. The planned test only reproduced it because its fake agent writes the ticket file by hand instead of through `chitty edit`. Criteria removed because nothing will be built.

## History

- 2026-11-11T15:57:40Z vivid-yellowhammer → backlog
- 2026-11-24T08:39:55Z kind-navy-toad: changed title, description, acceptance criteria
- 2026-11-24T08:39:55Z kind-navy-toad backlog → planning
- 2026-11-24T08:41:55Z kind-navy-toad planning → cold-read
- 2026-11-24T08:44:13Z kind-navy-toad: changed description
- 2026-11-24T08:44:13Z kind-navy-toad cold-read → planning
- 2026-11-24T08:44:59Z kind-navy-toad: changed description
- 2026-11-24T08:44:59Z kind-navy-toad planning → cold-read
- 2026-11-24T08:46:20Z kind-navy-toad: changed description
- 2026-11-24T08:46:20Z kind-navy-toad cold-read → planning
- 2026-11-24T08:46:33Z kind-navy-toad planning → cold-read
- 2026-11-24T08:49:32Z kind-navy-toad: changed description
- 2026-11-24T08:49:32Z kind-navy-toad cold-read → todo
- 2026-11-24T09:07:51Z kind-navy-toad: changed acceptance criteria, notes
- 2026-11-24T09:07:53Z kind-navy-toad todo → review
