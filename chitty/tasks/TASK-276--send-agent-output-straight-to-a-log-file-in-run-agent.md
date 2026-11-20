---
title: Send agent output straight to a log file in `_run_agent`
status: review
parent: TASK-275
created: 2026-11-11
---

## Description

When a `chitty run` agent session goes wrong nobody can see what it did: `_run_agent` (`src/chitty/run.py`) reads agent output through a pipe only to put it into an error note (circuitry 2026-11-14 and echonomicon 2026-11-19: tickets went to `error` as `was unchanged` after agents that exited 0 in about two seconds). A descendant that keeps the pipe open also holds the run until it exits, because `process.communicate` waits for end of file. This ticket makes `_run_agent` write agent output to a file it is given. Creating a log per ticket run and printing its path is `TASK-467`; pruning is `TASK-465`; naming the log in error notes is `TASK-466`.

Decisions (owner, 2026-11-20):

- Agent output never goes to the terminal. (An earlier version of this ticket echoed it to stderr through a reader thread; three reviews each found a race between that thread and an output deadline. Both are dropped.)
- `_run_agent(command, *, cwd, env, timeout, log)` gains a required keyword argument `log: BinaryIO` (no default): an open file the caller owns, readable and writable, with a real file descriptor. `_run_agent` never closes it. An in-memory object such as `io.BytesIO` is not supported: its `fileno()` raises `io.UnsupportedOperation`, which surfaces as is; add no check for it.
- No pipe: `subprocess.Popen(..., stdout=log, stderr=subprocess.STDOUT)`, so the operating system writes the agent output, merged in arrival order, straight to the file. Before starting the agent, flush `log`, seek to its end (`log.seek(0, os.SEEK_END)`, so the agent appends rather than overwriting) and record that offset. When `process.wait` returns, take the file size then (`os.fstat(log.fileno()).st_size`) and read from the offset up to that size, so bytes a descendant writes during the read are not included (no test can provoke that race reliably; the reviewer checks the code). On the timeout path, do the same after the post-kill `process.wait()` returns. Those bytes are the returned `CompletedProcess.stdout`, so error notes still hold the output of this call only, as today.
- Waiting is `process.wait(timeout=timeout or None)` (`0` still means no limit). `subprocess.TimeoutExpired` leads to the existing process-tree kill, then `process.wait()` replaces the second `process.communicate()`. Keep the `stderr=b"timed out"` sentinel and the kill grace. Do not change the process group or session (`_run_agent` sets neither today; `docs/plan/next-action-and-runner.md`). `KeyboardInterrupt` handling is unchanged: it propagates to `_run_session` as today.
- A descendant that outlives the agent no longer delays the return. Whatever it writes later lands in the file after the call returns and is not in the returned `stdout`.
- Until `TASK-467` lands, `_run_session` opens a `tempfile.TemporaryFile()` (binary, read and write) in a `with` block around its `_run_agent` call and passes it as `log`.
- The implementation on branch `task-276` follows the dropped design. In one commit, return `src/chitty/run.py` and `tests/test_run_timeout.py` to their `main` versions and delete `tests/test_run_agent_output.py`, then build this design.
- Out of scope: where logs live, their names, pruning and naming them in notes (`TASK-465` to `TASK-467`), and any change to what `chitty run` prints.

Tests: no property; this is real process and file handling. New tests go in a new `tests/test_run_agent_output.py`, calling `_run_agent` directly with `sys.executable -c ...` agents as `tests/test_run_timeout.py` does, and a log the test opens itself with `tempfile.TemporaryFile()`.

## Acceptance Criteria

- [ ] The test writes `earlier\n` to one log without flushing and seeks it back to its start, then makes three calls on it: an agent that prints `out-1`, `err-1`, `out-2`, `err-2`, `out-3`, `err-3` in that order (the `out` lines on stdout, the `err` lines on stderr, each with `flush=True`) and then writes raw `b"\xff\n"` and `tail` (no newline) through `sys.stdout.buffer`; an agent that prints nothing; and an agent that writes raw `b"\xe2\x82"` with no newline. Each exits 0 and each returned `stdout` equals exactly its own agent bytes (empty for the second); reading the whole log from the start gives `earlier\n` followed by the three outputs in order. Write the checks as a helper that takes the function under test. Commit two wrong versions of `_run_agent` in the test file, one that returns the whole log and one that does not seek to the end before starting the agent, and a test asserting the helper fails for each (`assertRaises(AssertionError)`, one `subTest` each).
- [ ] The test writes `earlier\n` to its log, then runs an agent that starts a descendant (which sleeps 4 seconds, prints `LATE` with `flush=True`, and exits), writes the descendant PID to a file in a temporary directory the test creates, and exits 0 at once. The call returns in under 3 seconds, and the returned `stdout` contains neither `LATE` nor `earlier`. The test then polls for at most 10 seconds until `ps -o stat= -p <pid>` prints nothing or a state starting with `Z` (as `tests/test_run_timeout.py` does), kills the descendant in a `finally` if it is still running, and asserts the log now contains `LATE`. As in criterion 1, commit a wrong version that also waits for every descendant of the agent to exit before returning, and a test asserting the checks fail for it.
- [ ] With `timeout=2`, an agent that prints `TIMEOUT_MARKER` with `flush=True` and sleeps 60 seconds returns the `timed out` sentinel with `TIMEOUT_MARKER` in `stdout` and in the log. As in criterion 1, commit a wrong version that returns empty `stdout` on the timeout path, and a test asserting the checks fail for it. `tests/test_run_timeout.py` changes only by passing `log=` a `tempfile.TemporaryFile()` to its four `_run_agent` calls, and passes, including `test_run_timeout_records_usage_and_exits_one`, which reaches `_run_agent` through `_run_session`. `git grep -n "communicate" -- src/chitty/run.py` finds nothing. `make check` passes.

## Plan

Restore src/chitty/run.py and tests/test_run_timeout.py to main, and delete the stale tests/test_run_agent_output.py in one commit. Then implement direct binary-file output in _run_agent: flush and seek the caller-owned log to EOF, pass it as stdout with stderr merged, wait with the existing timeout/process-tree termination behavior, and return only the bytes written between the starting offset and the size observed after wait. Open a TemporaryFile around _run_agent in _run_session. Update timeout tests to supply binary temporary logs. Add fresh direct-call tests for byte-exact append behavior, prompt return despite a lingering descendant, and timeout output preservation, including the specified wrong-implementation checks. Run focused tests and make check, then commit implementation and tests with Task: TASK-276.

## Notes

Planner, 2026-11-19: rewritten from scratch and split twice after cold reads. The earlier implementation on branch `task-276` (tip `e26f0cd5`) was deleted at the owner's request because it had gone stale and conflicted with `main`; ignore any `refs/cold-read/TASK-276/*` refs. Split out: the per-run log in `chitty run` (`TASK-467`), pruning (`TASK-465`), log paths in error notes (`TASK-466`).

Review failed (tests): Add coverage for the lingering-pipe fragment and thread exceptions, and preserve bytes available before the grace deadline. These findings are new; there are no earlier review notes.
1: pass - `make check` ran 791 tests and printed OK; the ordering test passes. Running the new tests with the `main` implementation substituted produced TypeError for the missing `log` argument.
2: pass - `make check` printed OK for the invalid-byte and closed-log test; substitution of the `main` implementation produced TypeError for the missing `log` argument.
3: fail - The descendant test does not replace `threading.excepthook` or assert that no thread raised, and its cleanup does not cover the earlier return-code and duration assertions. Put cleanup around the entire run and check the hook after the late output. Also, a direct `_run_agent` invocation with an agent that flushes `partial` without a newline and spawns a descendant holding stdout open for 4 seconds printed `elapsed: 2.0 stdout: b'\` and only echoed `partial` later: `readline` withholds bytes until EOF, so output already in the pipe is lost from the result and log at the deadline. Retain those bytes within the deadline and add a regression test.
4: pass - `make check` printed OK, including the timeout marker test and existing timeout tests; substituting the `main` implementation made the new timeout test error with the missing `log` argument.

Addressed the lingering-pipe finding with chunked reads and an incremental UTF-8 decoder: bytes are retained immediately, including unterminated fragments, while decoding remains correct across chunk boundaries. Expanded the descendant regression to assert retained/logged partial output and no reader thread exception, with cleanup around all assertions. make check passes (791 tests); focused tests pass. Implementation commit: 75e101cc.

Review failed (tests): Preserve and log incomplete UTF-8 output at the grace deadline, and add a regression test. The prior review reported lost unterminated output; its ASCII example is fixed, but this newly discovered multibyte variant remains unresolved.
1: pass - make check printed OK (792 tests); the prior review recorded that the new test errors against main without the log argument.
2: pass - make check printed OK for invalid bytes and closed log; the prior review recorded failure against main without the log argument.
3: fail - A direct _run_agent invocation started a descendant sleeping 3 seconds and flushed raw bytes b"\xe2\x82" without a newline. It printed stdout: b"\xe2\x82" and an empty log, which remained empty after EOF: the incremental decoder retains the fragment until EOF, after the log has detached. Flush pending decoder bytes with replacement at the deadline without losing later stderr output. The existing descendant regression does not cover this case. The previous review recorded that the test fails against main.
4: pass - make check printed OK, including timeout tests; the previous review recorded failure against main without the log argument.

Regression test first failed against the unfixed code: the incomplete UTF-8 fragment was absent from the log at the grace deadline. After the fix, focused output tests and make check pass. Decoder access is serialized with the reader, and its pending fragment is finalized and written before the log detaches; later reader output continues to stderr.

Review failed (work): A newly discovered race loses output already read before the grace deadline when stderr writes are slow. Synchronize delivery and detachment so retained output is not silently omitted from the log; add a regression. The previously reported incomplete UTF-8 case now passes.
1: pass - make check printed OK for 793 tests, including ordering; the first review recorded that the test fails against main.
2: pass - make check printed OK for invalid bytes and closed log; the first review recorded that the test fails against main.
3: fail - A direct _run_agent invocation with a StringIO stderr whose write sleeps 3 seconds, an in-memory log, and an agent printing BEFORE showed `returned: b'BEFORE\n' log: ''` after the 2-second grace; after the reader finished it printed `after reader: '' stderr: 'BEFORE\n'`. The reader decodes before acquiring the log lock, so the deadline detaches the log while an earlier stderr write is in progress. Output read within the deadline is lost from the log. The earlier ASCII and incomplete UTF-8 regressions pass in make check; their original failures are documented in the prior review notes.
4: pass - make check printed OK, including timeout and existing timeout tests; the first review recorded failure against main.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Owner decision 2026-11-20: do not echo agent output to the terminal; that was a mistake. Agent output goes to the log only. Planner proposal (not yet agreed): drop the reader thread, lock and `AGENT_OUTPUT_GRACE_SECONDS`; `_run_agent` passes an open binary log file as the agent stdout (stderr merged) and waits with `process.wait`, so a descendant holding the output open no longer delays the run, and returns as `stdout` the bytes the file gained during the call. This removes the three races found in review (lost unterminated output, lost partial UTF-8 character, log detached during a slow stderr write). The earlier implementation on this branch follows the old design.

Blocked by a worktree/ticket ownership mismatch: this task worktree rejects edits because the authoritative latest committed TASK-276 version is on main and instructs Chitty edits to run from the main checkout. The user restricted work to this ticket worktree, so I cannot write the required plan or safely proceed with implementation here. A maintainer should reconcile the authoritative ticket state with the task-276 worktree (or authorize task metadata edits from main); then retry.

Planner 2026-11-20: the block above was caused by the planner, not the ticket. Copying the rewritten ticket to `main` (`58041b1a`) made `main` hold the newest commit, so Chitty treated `main` as authoritative and refused edits in this worktree. Fixed by merging `main` into `task-276` (`de0790b9`, taking the ticket text from `main`); the ticket is back in `todo` and its edits belong in this worktree again. The old threaded code is still on the branch, to be reverted as the Description says.

Planner 2026-11-20 (owner direction: move checks from agents to automation where safe): the wrong versions in all three criteria are now committed tests, not hand runs recorded in notes.

Blocked: Chitty considers the latest committed TASK-276 to be on main and refuses to update its status from this ticket worktree. A maintainer must reconcile the ticket authority/branch metadata or authorize editing from main.

Planner 2026-11-20: blocked again for the same reason (claim on `main` while branch `task-276` already existed). Merged `main` into `task-276` again and set `doing` from this worktree, so the next run continues here without a new claim on `main`. No code work had started.

## Summary

Implemented direct binary log output in _run_agent, bounded returned bytes to the file range written during the call, retained timeout process-tree handling, and supplied a temporary binary log from _run_session. Added byte-exact append, lingering-descendant, and timeout regressions, including committed faulty implementations. Verification: make check passed (793 tests); focused output and timeout tests passed. Follow-up: none.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:45Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:51Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:41:47Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:41:55Z vivid-yellowhammer: changed dependencies
- 2026-11-11T13:41:55Z vivid-yellowhammer cold-read → planning
- 2026-11-11T13:44:12Z vivid-yellowhammer planning → cold-read
- 2026-11-11T13:51:57Z vivid-yellowhammer: changed description, notes
- 2026-11-11T13:51:57Z vivid-yellowhammer cold-read → todo
- 2026-11-12T21:35:00Z kind-yellow-vole: changed description
- 2026-11-14T09:20:55Z jolly-silver-falcon: changed dependencies, notes
- 2026-11-19T21:12:12Z sunny-white-dormouse: changed notes
- 2026-11-19T21:12:12Z sunny-white-dormouse todo → planning
- 2026-11-19T21:12:26Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:12:39Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:18:33Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:18:33Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:18:51Z sunny-white-dormouse: replaced notes
- 2026-11-19T21:19:17Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:20:46Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:22:01Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:22:01Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:22:08Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:23:23Z sunny-white-dormouse: replaced notes; changed title, description, acceptance criteria
- 2026-11-19T21:23:23Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:23:53Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:24:55Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:24:55Z sunny-white-dormouse cold-read → todo
- 2026-11-19T21:25:08Z sunny-white-dormouse: changed acceptance criteria
- 2026-11-20T00:14:05Z vivid-amber-toad todo → doing
- 2026-11-20T00:16:53Z vivid-amber-toad: wrote the plan
- 2026-11-20T00:23:21Z vivid-amber-toad: changed summary
- 2026-11-20T00:23:21Z vivid-amber-toad doing → review
- 2026-11-20T00:28:24Z golden-indigo-gannet: changed acceptance criteria, notes
- 2026-11-20T00:28:24Z golden-indigo-gannet review → doing
- 2026-11-20T00:40:34Z able-zinc-falcon: changed notes, summary; ticked acceptance criteria
- 2026-11-20T00:40:34Z able-zinc-falcon doing → review
- 2026-11-20T00:46:51Z honest-amber-stoat: changed acceptance criteria, notes
- 2026-11-20T00:46:51Z honest-amber-stoat review → doing
- 2026-11-20T00:55:50Z zesty-ebony-gannet: wrote the plan
- 2026-11-20T00:59:41Z zesty-ebony-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-20T00:59:41Z zesty-ebony-gannet doing → review
- 2026-11-20T01:05:09Z able-navy-quail: changed owner, acceptance criteria, notes
- 2026-11-20T01:05:09Z able-navy-quail review → blocked
- 2026-11-20T08:39:11Z lively-bronze-crane: changed owner, notes
- 2026-11-20T08:39:11Z lively-bronze-crane blocked → planning
- 2026-11-20T08:41:43Z lively-bronze-crane: changed title, description; wrote the plan
- 2026-11-20T08:41:58Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:42:30Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:42:33Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:43:30Z lively-bronze-crane cold-read → planning
- 2026-11-20T08:43:32Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T08:43:35Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:44:58Z lively-bronze-crane cold-read → planning
- 2026-11-20T08:45:01Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:45:05Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:45:25Z lively-bronze-crane cold-read → planning
- 2026-11-20T08:45:28Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T08:45:33Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:47:12Z lively-bronze-crane cold-read → planning
- 2026-11-20T08:47:15Z lively-bronze-crane: changed description, summary
- 2026-11-20T08:47:26Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:47:30Z lively-bronze-crane planning → todo
- 2026-11-20T09:13:42Z intrepid-violet-otter todo → doing
- 2026-11-20T09:15:39Z intrepid-violet-otter: changed notes
- 2026-11-20T09:15:39Z intrepid-violet-otter doing → blocked
- 2026-11-20T09:31:53Z lively-bronze-crane: changed owner
- 2026-11-20T09:31:53Z lively-bronze-crane blocked → todo
- 2026-11-20T09:32:15Z lively-bronze-crane: changed notes
- 2026-11-20T09:44:01Z lively-bronze-crane todo → planning
- 2026-11-20T09:44:03Z lively-bronze-crane: changed acceptance criteria, notes
- 2026-11-20T09:44:08Z lively-bronze-crane planning → todo
- 2026-11-20T09:53:50Z upbeat-indigo-urchin todo → doing
- 2026-11-20T09:55:57Z human: changed notes
- 2026-11-20T09:55:57Z human doing → blocked
- 2026-11-20T10:06:41Z lively-bronze-crane: changed owner, notes
- 2026-11-20T10:06:41Z lively-bronze-crane blocked → doing
- 2026-11-20T11:52:33Z vivid-hazel-stoat: wrote the plan
- 2026-11-20T11:57:01Z vivid-hazel-stoat: changed summary
- 2026-11-20T11:57:01Z vivid-hazel-stoat doing → review
