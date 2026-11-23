---
title: "`chitty edit -s review` runs the check silently and looks hung"
status: doing
created: 2026-11-22
---

## Description

`chitty edit <ID> -s review` runs the configured `check` on entering review
(`Repo._edit_stored`, `src/chitty/store.py` around lines 993-997) with all output in
`.chitty/check.log` and nothing on the terminal, so a 3-minute check looks
hung (the owner, 2026-11-22, on `TASK-540`). TASK-575 skips the check when
there is nothing to check; this ticket covers the cases where it still runs.

Change: in that block, just before `commands.run_logged("check", ...)`,
print to stderr

    running check <command> before review (output in .chitty/check.log)

(exactly this text, with the configured command substituted and no backticks)

and after it returns (pass or fail, not on exceptions) print

    check finished in <N>s

where `<N>` is whole seconds rounded down (`int(...)`) from
`time.monotonic()` (add `import time` to `store.py`). Use `click.echo(...,
err=True)` or `print(..., file=sys.stderr)`, whichever `store.py` already
uses for stderr messages (`grep -n "file=sys.stderr\|err=True" src/chitty/store.py`). When the check is skipped (`skipped check: HEAD is already on main`), neither new line is printed.

Tests, in `tests/test_review_check.py`, reusing `prepare()`:

- Passing check (`self.script("")`): `chitty edit 1 -s review` through
  `run_cli`; `result.stderr` contains "running check", then the check command text after it, and "check finished in" after the command text (compare `str.index`), and `re.search(r"check finished in \d+s\n", result.stderr)` matches.
- Failing check (`self.script("raise SystemExit(3)\n")`, `exit_code=1`):
  the same `re.search` matches.

If TASK-575 has landed, `prepare()` already makes a commit on `task-1`; if
not, the check runs anyway. Record that both tests fail before the change.

## Acceptance Criteria

- [ ] Entering review with a configured check prints `running check <command> before review (output in .chitty/check.log)` and then `check finished in <N>s` with whole seconds, on stderr, for passing and failing checks; shown by the two new tests, which fail before the change.
- [ ] `make check` passes.

## Plan

Add passing and failing review-check regression tests, verify they fail, then report start and elapsed time around the logged command. Run formatting and checks before handoff.

## Notes

Suggestion origin: chitty

Cold read: failing-check test, ordering, rounding and line number added.

The specified first line is `running check `<command>` before review ...`, but the passing-test instructions require the command text before `running check`, and acceptance criterion 1 also says the command comes before `running check`. These orders conflict, so the requested test cannot verify the specified output. Please decide the intended order and correct the line, test instructions, and criterion consistently.

`src/chitty/store.py` calls `commands.run_logged` inside the review transition and already uses `print(..., file=sys.stderr)`; `tests/test_review_check.py` provides `prepare()` and the requested passing and failing scripts. The existing check skips when HEAD is already on main, and `prepare()` makes an empty work commit. No implementation or regression tests were written or run because the output requirement is contradictory; timing and pass/fail behavior remain unverified.

Planner, 2026-11-23: the order now matches the specified line: `running check`, then the command, then `check finished in`.

Planner, 2026-11-23, after a cold read: the line is now exact text with no backticks; the tests check the whole-seconds format with a regex; the code location is corrected; and nothing is printed when the check is skipped. The criterion no longer claims timing that stderr cannot show.

## History

- 2026-11-22T13:16:27Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:27Z friendly-jade-stoat: changed notes
- 2026-11-22T13:18:38Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T13:18:38Z friendly-jade-stoat backlog → planning
- 2026-11-22T13:21:11Z friendly-jade-stoat: changed description, acceptance criteria, notes
- 2026-11-22T13:21:11Z friendly-jade-stoat planning → todo
- 2026-11-22T15:59:02Z sunny-amber-dormouse todo → doing
- 2026-11-22T16:02:09Z sunny-amber-dormouse: changed owner, notes
- 2026-11-22T16:02:09Z sunny-amber-dormouse doing → planning
- 2026-11-23T12:25:13Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:25:13Z witty-russet-gannet planning → cold-read
- 2026-11-23T12:26:19Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:26:19Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:40:28Z daring-indigo-toad todo → doing
- 2026-11-23T12:43:34Z daring-indigo-toad: wrote the plan
