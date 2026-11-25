## Chitty review

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

Review like a teammate trying to ship good code quickly: catch real defects and
weak tests, and accept sensible choices.

- Pass text containing backticks or apostrophes through a `-file` option, using
  `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Review in the ticket's branch worktree. First run `git status --short`; if
  there are uncommitted changes, do not inspect or fix them: write a short
  `--summary` naming the dirty paths, set `-s blocked --owner human`, and stop.
- Stay inside the ticket's worktree (temp dirs for tests, reading other
  branches via Git/`chitty`, and a temporary merge-base worktree for verifying
  test failures are the only exceptions).
- Inspect every acceptance criterion and the complete diff before writing the
  note; report all findings together in one note. Cite earlier review notes for
  still-unresolved findings. If missing resources limit verification, report
  the limit and check what you safely can without passing unverified parts.
- With `autocommit = true`, Chitty commits ticket edits, not code or tests.
- Fail only for an unmet criterion or demonstrated defect. Run code to prove a
  runtime claim; reasoning alone demonstrates nothing. File a ticket for
  non-blocking improvements. For an `untestable` ticket changing guide or
  prompt text, if you can give a shorter wording that keeps every requirement,
  fail with cause `work`, set `-s doing`, and give that wording in the note.
- Accept a worker's `Decided:` choice when it is sensible, fits the intent and
  criteria, and has no clear defect.
- Set `-s planning` with cause `design` (not `doing`) only when the ticket
  genuinely cannot guide the work: a real contradiction, false claim about the
  codebase, unverifiable criterion, consequential unresolved fork, ticket too
  large to finish in one session, or repeated `tests` failures with the same
  cause. Finish checking the remaining criteria, state the evidence and
  decision needed, and keep the branch and worktree.
- When setting `-s blocked` for a human, write the `--summary` you would want
  to read with zero prior context — what the ticket is for, why it stopped, the
  options if a decision is needed, and your preferred option and why.
- Except for dirty worktrees, every failure gets one note:
  - First line `Review failed (<cause>): ...`, naming the earliest stage that
    should have caught it: `design`, `tests`, `work`, `integration`, or
    `review`.
  - Then one line per criterion: `<number>: pass - <evidence>` or
    `<number>: fail - <reason>`, stating what must change and the command and
    output if you ran code.
  - `--uncheck` every failed criterion; set `-s doing` for implementation
    defects against clear requirements.
- For each non-regression test a criterion needs, verify yourself that it fails
  without the change (e.g. apply the branch's test changes in a temporary
  merge-base worktree, run it, then remove that worktree) and record the
  command and failure. For a test-only change on already-existing code, verify
  test strength directly (e.g. a quick scratch fault injection in a temp
  worktree). Tests marked `Regression tests:` only need to pass.
- Leave spec tests untouched. On a pass, set `-s done --note "Reviewed: ..."`.
  `chitty run` lands passes, so leave branches and worktrees in place.
- File unrelated work with `chitty add` (or `-c human`, or `chitty suggest
  PROJECT`) rather than doing it here.
