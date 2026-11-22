---
title: "`chitty edit -s review` runs the check silently and looks hung"
status: planning
created: 2026-11-22
---

## Description

`chitty edit <ID> -s review` runs the configured `check` on entering review
(`Repo.edit`, `src/chitty/store.py` around line 986) with all output in
`.chitty/check.log` and nothing on the terminal, so a 3-minute check looks
hung (the owner, 2026-11-22, on `TASK-540`). TASK-575 skips the check when
there is nothing to check; this ticket covers the cases where it still runs.

Change: in that block, just before `commands.run_logged("check", ...)`,
print to stderr

    running check `<command>` before review (output in .chitty/check.log)...

and after it returns (pass or fail, not on exceptions) print

    check finished in <N>s

where `<N>` is whole seconds from `time.monotonic()`. Use `click.echo(...,
err=True)` or `print(..., file=sys.stderr)`, whichever `store.py` already
uses for stderr messages (`grep -n "file=sys.stderr\|err=True"
src/chitty/store.py`).

Test, in `tests/test_review_check.py`, reusing `prepare()` with a passing
check script (`self.script("")`): run `chitty edit 1 -s review` through
`run_cli` and assert `result.stderr` contains
"running check" and "check finished in". If TASK-575 has landed, `prepare()`
already makes a commit on `task-1`; if not, the check runs anyway. Record
that the test fails before the change.

## Acceptance Criteria

- [ ] Entering review with a configured check prints `running check` before it and `check finished in <N>s` after it on stderr; shown by the new test, which fails before the change.
- [ ] `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T13:16:27Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:27Z friendly-jade-stoat: changed notes
- 2026-11-22T13:18:38Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T13:18:38Z friendly-jade-stoat backlog → planning
