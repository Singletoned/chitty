---
title: Echo agent output to stderr and an optional log in `_run_agent`
status: todo
parent: TASK-275
created: 2026-11-11
---

## Description

In print mode an agent prints only its final message, and `chitty run` captures agent output only to put it into an error, so when a session goes wrong nobody can see what it did (circuitry 2026-11-14 and echonomicon 2026-11-19: tickets went to `error` as `was unchanged` after agents that exited 0 in about two seconds). This ticket changes only how `_run_agent` (`src/chitty/run.py`) reads agent output: it echoes it live to stderr and can copy it to a log. Creating a log per ticket run and printing its path is `TASK-467`; pruning is `TASK-465`; naming the log in error notes is `TASK-466`.

Decisions (2026-11-19; an earlier implementation on branch `task-276` was deleted, start from `main`):

- `_run_agent(command, *, cwd, env, timeout, log)` gains a required keyword argument `log: TextIO | None` (no default value). Every caller in this ticket passes `log=None`: `_run_session` and the four direct calls in `tests/test_run_timeout.py` (that is the only change to that file).
- Agent stdout and stderr stay merged into one pipe (`stderr=subprocess.STDOUT`), so arrival order needs no extra work.
- One daemon reader thread is the only reader of `process.stdout`; remove both `process.communicate()` calls (normal path and after a timeout kill). The reader reads bytes line by line, keeps every byte for the returned `CompletedProcess.stdout` exactly as today, and for each line, decoded with `errors="replace"`, writes it to `sys.stderr` and, when `log` is not `None`, to `log`, flushing both. An unterminated final fragment at EOF is handled the same way. Decoding cannot fail with `errors="replace"`, and writes to `log` happen only under a lock while it is attached. If a write to `sys.stderr` or `log` raises (`OSError` or `ValueError`), the reader stores the first such exception, stops writing to that stream, and keeps reading so the pipe drains and the agent never blocks; after waiting, `_run_agent` raises `ChittyError("cannot write agent output: <error>")` from it, so the failure is plain and not mistaken for a timeout. The reader itself never raises.
- Waiting for exit is `process.wait(timeout=timeout or None)` (so `0` still means no limit); `subprocess.TimeoutExpired` leads to today's process-tree kill. After the agent exits, or after the timeout kill, `_run_agent` waits for the reader until one deadline, the module constant `AGENT_OUTPUT_GRACE_SECONDS = 2` beside `AGENT_KILL_GRACE_SECONDS`, so a descendant that keeps the pipe open cannot keep the run alive. The returned `stdout` holds the bytes read by then. In a `finally` (so also on timeout and `KeyboardInterrupt`), it detaches `log` under the lock, so the reader never writes to it again; later output goes to stderr only. `_run_agent` never closes `log`; its caller owns it.
- Keep the timeout handling, the process-tree kill and the `stderr=b"timed out"` sentinel. Keep the agent in the runner's process group and session; no `start_new_session` (`docs/plan/next-action-and-runner.md`).
- So `chitty run`'s stdout keeps only its status lines, and notes keep the agent output read within `AGENT_OUTPUT_GRACE_SECONDS` (today they wait for every descendant to close the pipe).

Tests: no property. This is real process and pipe handling, and its parts (an agent, its descendants, a deadline) cannot be pulled into a pure function. New tests go in a new `tests/test_run_agent_output.py`, calling `_run_agent` directly with `sys.executable -c ...` agents as `tests/test_run_timeout.py` does, a log file the test opens itself, and `sys.stderr` captured with `contextlib.redirect_stderr` to an `io.StringIO`.

## Acceptance Criteria

- [ ] An agent printing `out-1` to `out-5` on stdout and `err-1` to `err-5` on stderr, each with `flush=True`, alternating, then writing `tail` with `sys.stdout.write` and no newline, exits 0: the log and the captured stderr each hold each of those eleven pieces exactly once and in that order, the returned `stdout` holds them all as bytes, and the returncode is 0. It fails today (nothing is echoed or logged).
- [ ] An agent that writes `b"\xff bad\n"`, then `é\n`, then ends with `b"\xe2\x82"` and no newline (raw bytes via `sys.stdout.buffer`, flushed) gives a log containing ` bad`, `é` and a final line, and no thread exception (`threading.excepthook` replaced to record calls records none). A log opened on a closed file object gives `ChittyError` starting `cannot write agent output`. It fails today.
- [ ] An agent that starts a descendant printing `LATE` after 4 seconds and then exits at once: the call returns in under 3.5 seconds; the test sleeps until 5 seconds have passed, then `LATE` is not in the log and no thread raised; the test kills the descendant in a `finally`. It fails today (the call waits about 4 seconds).
- [ ] With `timeout=2`, an agent that prints `TIMEOUT_MARKER` with `flush=True`, starts a descendant ignoring `SIGTERM` that prints `LATE2` after 5 seconds, and sleeps 60 seconds returns the `timed out` sentinel with `TIMEOUT_MARKER` in `stdout`; the log contains `TIMEOUT_MARKER` and, checked after 8 seconds, not `LATE2`. Today it fails because `_run_agent` takes no `log` argument. `tests/test_run_timeout.py` passes with only `log=None` added. `make check` passes.

## Notes

Planner, 2026-11-19: rewritten from scratch and split twice after cold reads. The earlier implementation on branch `task-276` (tip `e26f0cd5`) was deleted at the owner's request because it had gone stale and conflicted with `main`; ignore any `refs/cold-read/TASK-276/*` refs. Split out: the per-run log in `chitty run` (`TASK-467`), pruning (`TASK-465`), log paths in error notes (`TASK-466`).

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
