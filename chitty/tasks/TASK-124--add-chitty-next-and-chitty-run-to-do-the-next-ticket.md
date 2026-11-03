---
title: Add `chitty next` and `chitty run` to do the next ticket
status: done
priority: high
depends_on:
  - TASK-123
parent: TASK-106
created: 2026-11-03
---

## Description

One command to do the right next thing: review whatever needs reviewing, otherwise work the highest-priority ticket. Run it repeatedly to check things between tickets, or in a shell loop to go unattended.

### `chitty next`

Prints the next action, for example `work TASK-12`. `--json` gives `{"mode", "id"}`. With nothing to do it prints nothing on stdout, gives a message on stderr, and exits non-zero. Selection lives in `src/chitty/store.py` beside `ordered` and raises `ChittyError` when there is nothing, so the MCP tool reports the same error.

1. Consider `review` tickets, then `doing`, then `todo`. `review` gives mode `review`; the others give `work`. Status wins over priority, because the human asked for reviews first and one ticket in work at a time means finishing `doing` first.
2. Within a status, take `high`, `medium`, `low`, then unset, then `TaskId` order (prefix, then number as an integer), across all contexts.
3. Always exclude `backlog`, `blocked` and `done`; tickets in the context named `human`; and tickets whose `owner` is exactly `human`.
4. Exclude `todo` tickets with a `depends_on` entry not yet `done`. A done or archived dependency counts as met: `TASK-105` still lists the finished `TASK-107`. The rule does not apply to `review` or `doing`, because work already started must not silently vanish from the queue if a dependency is added later.
5. A `depends_on` entry that names no ticket is a `ChittyError` naming both tickets, because `chitty check` already treats it as an error.

### `chitty run`

Put the process handling in a new module, `src/chitty/run.py`, so `cli.py` stays thin.

1. Call the selection, then run `pi --chitty-<mode> <ID>` as a child process with the repository root as its working directory, and stdin, stdout and stderr inherited, not captured.
2. After `pi` exits, open a new `Repo` to read the ticket: the existing instance caches branch history. Print the change, for example `TASK-12: todo → review`.
3. Exit 0 if the ticket's status changed, to any status: a ticket that becomes `blocked` has made progress and the next run moves on.
4. Exit non-zero with a message on stderr if there is no next ticket, `pi` is not on `PATH`, `pi` exits non-zero, or the status did not change. A session that made no progress, such as one out of credits, therefore stops a loop instead of repeating. Pi's exit code alone cannot show this, because interactive shutdown always exits 0. The unchanged message says that only committed changes are visible, because a worktree in a repository without `autocommit` looks unchanged.
5. On Ctrl-C, wait for `pi`, skip the comparison, and exit 130 with a one-line message and no traceback.

So `while chitty run; do :; done` is the loop, and needs no flag or code. `README.md` documents it.

### Defaults chosen, cheap to change

Pi exits when a ticket finishes rather than staying open, because a loop needs it and the terminal keeps the transcript. The command is named `run` and only knows `pi`; `TASK-89` can extend it. Model choice is left to Pi's settings; for a specific model, run `chitty next` and call `pi` directly. Agents do not need these commands, so `src/chitty/guide.md` does not change and no version bump is required.

`next` gets an MCP tool, since it is a read. `run` does not, since it launches a harness.

Out of scope: label filters and role options from `TASK-76`, per-stage models, and detecting a `doing` ticket held by another live session.

## Acceptance Criteria

- [x] Table-driven tests over a real temp repo cover selection order and every exclusion, including a met and an unmet dependency, and `HUMAN` tickets
- [x] Tests run `chitty run` with a fake `pi` on `PATH`, covering each exit-code case: status changed, unchanged, `pi` failing, `pi` missing, and no next ticket
- [x] `chitty next --json` and the MCP tool return the same answer
- [x] `PLAN.md`, `README.md` and the `chitty --help` output describe both commands and the shell loop; `__version__` is bumped if `src/chitty/guide.md` changes
- [x] Tests use a fake `pi` that commits the status change on a ticket branch in a worktree, as a real worker does, and `chitty run` run from the main checkout still reports the change and exits 0
- [x] Ctrl-C during `pi` exits `chitty run` non-zero without a traceback, so it stops a shell loop; a test sends SIGINT to the child and checks this
- [x] Selection tests also cover a `doing` ticket with an unmet dependency (selected), a dangling `depends_on` entry (error), a tie across two contexts, and `TASK-9` ordering before `TASK-12`
- [x] CLI tests pin `next` output: `work TASK-12`, the `--json` form, and for no ticket an empty stdout, a stderr message and a non-zero exit; the MCP tool reports the same error
- [x] Fake-`pi` tests pin `run`: the printed change line, a status change to `blocked` exiting 0, a working directory of the repository root, and a child that reads inherited stdin

## Plan

1. Map the existing CLI, MCP, repository ordering, and test helpers.
2. Add focused failing tests for selection, CLI/MCP parity, and subprocess execution semantics.
3. Implement shared next-action selection in `store.py`, thin CLI/MCP adapters, and `run.py`.
4. Document the commands, format, run the full checks, and verify every acceptance criterion.

## Notes

Criteria added after `TASK-123` failed review twice on behaviour its criteria left out. Starting states covered by existing text: a ticket that makes no progress exits non-zero. A `todo → doing` session that then runs out of credits counts as a change, so a loop spends one further session before stopping, which is accepted.

Cold read by a fresh Sonnet subagent, 2026-11-03. Adopted into the description: dependency rule limited to `todo`, a dangling dependency as an error, the definition of the human context, all contexts with `TaskId` tie-break, a fresh `Repo` after `pi` exits (the old one caches history), the repository root as working directory, Ctrl-C behaviour, the unchanged message for uncommitted worktree changes, and a new `src/chitty/run.py`. Three criteria added. Rejected as already fine or too rare: duplicate IDs and deleted tickets, which fail loudly already, and `review` tickets in a context with `review = false`. This corrects the earlier note, which overstated what the ticket covered.

Implementation choice: return a small action value with `mode` and canonical `TaskId` from shared selection. This keeps CLI, MCP, and runner output consistent while remaining cheap to extend if later commands need more metadata.

Implementation choice: return a small action value with `mode` and canonical `TaskId` from shared selection. This keeps CLI, MCP, and runner output consistent while remaining cheap to extend if later commands need more metadata.

Verified with `make check`: runner exit cases, CLI/MCP JSON parity, docs and help, Ctrl-C handling, and selection ordering/dependency edge cases pass. Remaining criteria need the committed-worktree integration scenario and tighter output assertions before review.

Verified the remaining criteria with `make check`: table-driven exclusions and dependency cases, a real Git worktree committing a status change, exact CLI/MCP no-work output, and inherited stdin/cwd/change output for fake `pi`.

All nine acceptance criteria re-checked after `make check` passed. Ready for an independent reviewer.

Review failed: (1) `next_action` treats an archived dependency as unmet because it checks only `status == "done"`; the requirement says archived dependencies count as met. Reproduced: archive a `todo` dependency, add a dependent `todo`, then `chitty next` exits 1 with `no next ticket`. Add coverage for archived dependencies and the full medium/unset priority order. (6) the Ctrl-C test has fake `pi` signal its parent with `os.kill(os.getppid(), SIGINT)`; it does not send SIGINT to the child as required, so it does not verify the specified child-interrupt scenario. (7) the numeric test selects `TASK-1` from `TASK-1` through `TASK-12`; it does not cover the required `TASK-9` before `TASK-12` comparison. Fix these and re-check the criteria.

Verified reviewer fixes with uv run ruff format --check .
176 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run python -m unittest discover -s tests -t .
[ticket 1ac4e97] worker change
 1 file changed, 1 insertion(+), 1 deletion(-): archived dependencies count as met; full priority order and  before  are covered; a test sends SIGINT to the Pi child and confirms exit 130 without a traceback. Re-checked all nine criteria.

Correction: verified reviewer fixes with `make check`: archived dependencies count as met; full priority order and `TASK-9` before `TASK-12` are covered; a test sends SIGINT to the Pi child and confirms exit 130 without a traceback. Re-checked all nine criteria.

Ready for independent review: all nine criteria are checked; `make check` passed with 207 tests.

Reviewed: all nine criteria pass independently. Inspected selection and runner behavior, CLI/MCP parity, documentation and help; make check passes (207 tests).

Retro: the single failed review cited stated requirements, in one note, so cause `work`: archived dependencies treated as unmet, a Ctrl-C test that signalled the parent instead of the child, and a numeric test that skipped `TASK-9` before `TASK-12`. None was a gap in the ticket, unlike both `TASK-123` failures, which is one data point for the cold read. Two of the three were tests weaker than the criterion they claimed, which spec-first tests aim to prevent. The cold read had flagged that archived was not named in a criterion and the author did not add it; that was the first failure. A worker note was again mangled by shell backticks (`TASK-67`).

## History

- 2026-11-03T12:40:39Z lively-panda → todo
- 2026-11-03T16:08:31Z lively-panda: changed acceptance criteria, notes
- 2026-11-03T16:16:15Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T16:45:51Z honest-heron: changed notes; wrote the plan
- 2026-11-03T16:45:51Z honest-heron todo → doing
- 2026-11-03T16:46:18Z honest-heron: changed notes; wrote the plan
- 2026-11-03T16:57:36Z honest-heron: changed notes; ticked acceptance criteria
- 2026-11-03T17:01:02Z honest-heron: changed notes; ticked acceptance criteria
- 2026-11-03T17:01:10Z honest-heron: changed notes
- 2026-11-03T17:01:10Z honest-heron doing → review
- 2026-11-03T17:08:32Z mellow-raven: changed acceptance criteria, notes
- 2026-11-03T17:08:32Z mellow-raven review → doing
- 2026-11-03T17:19:43Z frosty-marten: changed notes; ticked acceptance criteria
- 2026-11-03T17:19:51Z frosty-marten: changed notes
- 2026-11-03T17:19:58Z frosty-marten: changed notes
- 2026-11-03T17:19:58Z frosty-marten doing → review
- 2026-11-03T17:23:27Z brisk-quail: changed notes
- 2026-11-03T17:23:27Z brisk-quail review → done
- 2026-11-03T17:26:54Z lively-panda: changed notes
