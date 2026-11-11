---
title: Make the order of `chitty run` jobs configurable
status: doing
parent: TASK-259
created: 2026-11-11
---

## Description

- Today `src/chitty/selection.py` picks `review`, then `doing`, then `todo` (`STATUSES`). Add a top-level `job_order` setting in `chitty.toml`: a list of those statuses, in pick order. Unset means today's order.
- `chitty next`, `chitty run` and the MCP `next` tool use it, all through `next_action` in `src/chitty/store.py`. `--mode` narrows it further: `job_order = ["review"]` with `--mode work` picks nothing. `chitty run --ticket` and the `chitty list` markers are unchanged.
- An entry that is not one of those statuses, an empty list, or a repeated status is a config error naming the problem. A status left out of the list is never picked.
- Docs: `PLAN.md` "Config" (as a commented optional setting in the example) and "Next action and runner", and `README.md` where it describes the pick order.
- TASK-272 adds `cold-read` to the allowed statuses and puts it first in the default, because cold reads hold up planning. Until then `cold-read` in `job_order` is an error.

## Acceptance Criteria

- [ ] With `job_order = ["todo", "review"]` and one ticket in each, `chitty next` picks the `todo` ticket; without the setting it picks the `review` ticket, as today.
- [ ] With `job_order = ["todo"]` and only a `review` ticket, `chitty next` prints `no next ticket`; `job_order = ["typo"]` fails with an error naming `typo`.
- [ ] The property tests in `tests/test_property_next.py` also draw a random `job_order` and check `choose` against it.

## Plan

Add strict optional job_order validation to RepoConfig, defaulting selection to the existing STATUSES. Pass the configured order through next_action into choose while keeping mode filters and list markers unchanged. Add focused config/selection integration tests and extend the property test to generate status orders; update the Config, Next action and runner, and README pick-order docs. Verify with make format and make check, then commit implementation and update ticket.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-270/1`. Check it against the current criteria; do not trust it. It lacks the random-order property test and the docs.

Check failed before this session: check exited with status 2:
```text
....TASK-1: doing → review
.............no next ticket for --mode work
.......landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_configured_job_order_and_omitted_status (tests.test_next.TestNext.test_configured_job_order_and_omitted_status)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-270/tests/test_next.py", line 104, in test_configured_job_order_and_omitted_status
    with self.assertRaisesRegex(ChittyError, "no next ticket"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ChittyError not raised

----------------------------------------------------------------------
Ran 490 tests in 40.408s

FAILED (failures=1)
make: *** [check] Error 1
```

Check failed before this session: check exited with status 2:
```text
...TASK-1: doing → review
.............no next ticket for --mode work
.......landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_configured_job_order_and_omitted_status (tests.test_next.TestNext.test_configured_job_order_and_omitted_status)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-270/tests/test_next.py", line 104, in test_configured_job_order_and_omitted_status
    with self.assertRaisesRegex(ChittyError, "no next ticket"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ChittyError not raised

----------------------------------------------------------------------
Ran 490 tests in 31.161s

FAILED (failures=1)
make: *** [check] Error 1
```

## History

- 2026-11-11T13:21:06Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:43Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:50Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:43:01Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:43:01Z vivid-yellowhammer cold-read → todo
- 2026-11-11T14:55:45Z golden-crane todo → doing
- 2026-11-11T14:56:04Z golden-crane: wrote the plan
- 2026-11-11T18:47:42Z able-ibis: changed notes
- 2026-11-11T18:55:22Z sunny-marten: changed notes
