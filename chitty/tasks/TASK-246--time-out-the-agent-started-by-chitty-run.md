---
title: Time out the agent started by chitty run
status: review
labels:
  - needs-minor
created: 2026-11-10
---

## Description

In echonomicon, a `chitty run --mode work` agent (Pi, `gpt-6-luna`) ran `while ps -p <pid of chitty run>; do sleep 5; done`, waiting on its own parent. `chitty run` waits for the agent (`subprocess.run` in `src/chitty/run.py`, around line 236), so both hung for about 20 hours with no warning.

Add an optional setting, `agent_timeout` in `chitty.toml`: a whole number of seconds. It defaults to 7200 (two hours, a module-level constant), decided with the human on 2026-11-10; `0` means no limit. A negative number or a value that is not a TOML integer (a string such as `"10"` included) is a configuration error naming the key. The default changes behaviour for every project, so this ticket carries `needs-minor`.

When the limit passes, `chitty run` stops the agent and everything it started. The configured agent command is usually a wrapper (`env ... uv run ... pi`), so killing only the direct child would leave Pi running. List the agent's descendants (for example from `ps -A -o pid= -o ppid=`), send each and the agent `SIGTERM`, then `SIGKILL` any still running after a short grace period (a module-level constant). Keep the agent in `chitty run`'s own process group and session: a cold read found that `process_group=0` stops an interactive agent reading the terminal, and `start_new_session=True` takes its controlling terminal away. Staying in the same group also leaves Ctrl-C working exactly as today. It then fails like any other agent failure: it prints `agent timed out after N seconds` and exits 1. The ticket is left as the agent left it, the usage log records the run as usual, and `--loop` stops, as it does for every agent failure (see "Next action and runner" in `PLAN.md`).

Out of scope: an idle or no-output limit (the agent writes straight to the terminal, so `chitty run` sees no output to time), moving on to the next ticket after a timeout, and a guide line telling agents not to wait on their parent. Update the "Next action and runner" section of `PLAN.md` and the configuration docs.

## Acceptance Criteria

- [x] With `agent_timeout = 2` and an agent command that starts a child process which sleeps for 60 seconds, `chitty run` exits 1 within 10 seconds, prints `agent timed out after 2 seconds`, neither process is still running afterwards, and the usage log has an entry for the run.
- [x] With `agent_timeout = 0`, an agent that sleeps for 3 seconds finishes normally; `agent_timeout = -5` or `"10"` fails with a configuration error naming `agent_timeout`; and with no `agent_timeout` set, the limit is the default constant, which is 7200, and a test that patches that constant to 2 sees `agent timed out after 2 seconds`.
- [x] The agent runs in the same process group as `chitty run` (the fake agent records `os.getpgid(0)`), so terminal input and Ctrl-C reach it as today.

## Plan

Fix timeout escalation so the configured grace period applies to surviving descendants even if the direct agent exits promptly. Add a regression test with a SIGTERM-handling child that delays then records cleanup; run it against current code first to confirm failure, then implement and run focused plus full checks.

## Notes

Suggestion origin: echonomicon

Haiku cold read 1 (`refs/cold-read/TASK-246/1`): implemented as written, all green; new tests failed first. Outcomes: (1) `process_group=0` breaks interactive terminal input, and `start_new_session` drops the controlling terminal: fixed, now kills the descendant tree and keeps the agent in the same group, which replaced the Ctrl-C criterion. (2) The "longer than any test limit" bound was untestable: fixed, now 3 seconds. (3) `"10"` needs strict integer parsing: fixed, the description says a string is an error. (4) Usage log after a timeout was untested: fixed, added to criterion 1. (5) Reader skipped the `PLAN.md` and docs updates: no change, the description already asks for them.

Approach recorded; implementing.

Verified end-to-end timeout with child cleanup and usage-log entry; verified zero disables timeout, strict invalid-value rejection, 7200 default and patched 2-second default; verified inherited process group. make format && make check passed (429 suites plus Node tests). chitty fix completed; tree is clean.

Review failed (tests): Descendants do not receive the specified grace period when the agent exits on SIGTERM: the runner waits only for the agent, then immediately SIGKILLs remaining descendants. Add a regression test with a descendant that handles SIGTERM and needs time to clean up, and wait the grace period for surviving descendants before escalation. A throwaway _run_agent test with a child whose SIGTERM handler sleeps 0.5 seconds then writes a marker printed `agent timed out after 2 seconds` and `elapsed: 2.84 child cleanup completed: False` (including a subsequent 0.8-second wait). `make format && make check` passed: 442 Python tests and Node tests.

1: fail - Descendant cleanup escalates without the specified grace period.
2: pass - Configuration and default timeout tests passed.
3: pass - Inherited process group test passed.

Check failed before this session: check exited with status 2:
```text
.....TASK-1: doing → review
.......no next ticket for --mode work
.......landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_run_overlaps_one_worker_and_one_reviewer (tests.test_next.TestNext.test_run_overlaps_one_worker_and_one_reviewer)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-246/tests/test_next.py", line 537, in test_run_overlaps_one_worker_and_one_reviewer
    self.assertNotEqual(worker_actors, review_actors)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'nimble-falcon'} == {'nimble-falcon'}

----------------------------------------------------------------------
Ran 442 tests in 42.253s

FAILED (failures=1)
make: *** [check] Error 1
```

Fixed escalation to wait through the grace period for any live descendant, even when the agent exits immediately on SIGTERM. Added a regression test that failed before the fix and passes after it. make format and make check passed (443 Python tests and Node tests); focused timeout tests passed.

## Summary

Implemented and verified timeout descendant grace-period escalation. Regression test demonstrated failure before the fix; focused tests, make format, and make check pass. Ready for review; no follow-ups.

## History

- 2026-11-10T16:53:45Z jolly-heron → backlog
- 2026-11-10T16:53:45Z jolly-heron: changed notes
- 2026-11-10T16:54:04Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T16:54:04Z jolly-heron backlog → todo
- 2026-11-10T16:54:11Z jolly-heron todo → backlog
- 2026-11-10T16:59:38Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T16:59:40Z jolly-heron: changed notes
- 2026-11-10T17:34:39Z jolly-heron: changed labels, description, acceptance criteria
- 2026-11-10T17:34:48Z jolly-heron: changed acceptance criteria
- 2026-11-10T17:34:48Z jolly-heron backlog → todo
- 2026-11-10T17:35:46Z brisk-yellowhammer todo → doing
- 2026-11-10T17:35:55Z brisk-yellowhammer: wrote the plan
- 2026-11-10T17:36:08Z brisk-yellowhammer: changed notes
- 2026-11-10T17:45:06Z brisk-yellowhammer: changed notes, summary; ticked acceptance criteria
- 2026-11-10T17:45:06Z brisk-yellowhammer doing → review
- 2026-11-10T18:11:52Z tidy-urchin: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-10T18:11:52Z tidy-urchin review → doing
- 2026-11-10T18:13:59Z youthful-otter: changed notes
- 2026-11-10T18:14:35Z youthful-otter: wrote the plan
- 2026-11-10T18:16:25Z youthful-otter: changed notes, summary; ticked acceptance criteria
- 2026-11-10T18:16:25Z youthful-otter doing → review
