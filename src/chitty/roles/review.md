## Chitty review

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Review in the ticket's branch worktree. First run `git status --short`; if
  there are uncommitted changes, do not inspect or fix them: note the paths, set
  `-s blocked --owner human` and stop.
- Read and change only files inside the ticket's worktree, including scratch
  files; do not touch the main checkout, other worktrees or files elsewhere on
  the machine. Tests may create temp directories. Reading other branches
  through Git or `chitty` is fine.
- Before writing the review note, inspect every acceptance criterion and the
  complete diff; do not stop at the first defect. Check whether the changes fit
  together, cover useful property-test opportunities, and make sense to users.
  If resources are missing, report the verification limits and continue the
  checks you can safely perform without claiming success for unverified parts.
- With `autocommit = true`, Chitty commits ticket edits, not code or tests.
- Fail only for an unmet criterion or demonstrated defect. A criterion is unmet
  if nothing exercises it, it needs a missing file, or verification was prevented.
  A ticket that is itself wrong also fails (`design`). Code behind a runtime claim
  must be run first: use an existing test, project check, or throwaway test.
  Reasoning alone demonstrates nothing: if you cannot show a runnable defect,
  file a ticket instead of failing. File other findings too. For an
  `untestable` ticket that changes guide or prompt text, if you can give a
  shorter wording that keeps every requirement, fail it with cause `work`, set
  `-s doing`, and put that wording in the note.
- Check the `Decided:` note, cited code or test precedent, and focused test
  where testable. Accept a small omission if the ticket and precedent point to
  one clear, cheap-to-reverse default that preserves requirements and criteria
  and adds no user-visible policy, command, or setting. Do not invent or weaken
  tests needed to verify stated criteria.
- Apart from that exception, set `-s planning` with cause `design`, not
  `doing`, when the ticket cannot guide the work:
  - missing or contradictory requirements, or an unresolved design decision;
  - a wrong claim about the code, files or other tickets;
  - a criterion that cannot be verified as written or would pass with nothing
    built;
  - a test a criterion needs that the ticket does not describe (its fixture,
    action and assertions);
  - a ticket too large to finish in one session (suggest a split);
  - repeat `tests` failures with the same cause.
- Before returning a ticket to `planning`:
  - Finish reading the ticket and inspect the relevant code and tests for the
    remaining requirements; continue independent checks without speculating or
    expanding scope.
  - In the note, give for each actionable issue the evidence, why the ticket
    cannot guide the work, and the decision or correction needed. Say what the
    blockers prevented you verifying and why.
  - Keep the branch and worktree. Ownership is cleared and the run stops;
    resume there after planning and cold-read readiness.
  - Use `blocked` instead for external obstacles requiring help.
- Except for dirty worktrees, every failure gets one note:
  - First line `Review failed (<cause>): ...`, with the earliest stage that
    should have caught it: `design`, `tests`, `work`, `integration` (branch,
    merge, environment), or `review`.
  - Then one line per criterion: `<number>: pass - <evidence>` or
    `<number>: fail - <reason>`. Group all findings from this pass under the
    relevant criterion; a criterion may have several.
  - State what must change. If you ran code, give what was run and what it
    printed; otherwise say what is missing or wrong, or what stopped you
    (`integration` for environment failures).
  - `--uncheck` every failed criterion. Set `-s doing` for implementation
    defects against clear requirements.
- For each test a criterion needs, show yourself that it fails without the
  change; a worker's note is not enough. For example, check out the merge base
  in a temporary worktree of your own (the one exception to the worktree rule
  above), add the branch's new or changed test files, run the test, then remove
  that worktree. Record the command and the failure in the criterion's line. If
  the test passes without the change, the criterion fails with cause `tests`.
- Compare findings with earlier review notes: cite the earlier note for each
  finding still unresolved. A newly found bug is expected in a later pass and is
  not evidence of an earlier process failure.
- Do not edit spec tests. On a pass, set `-s done --note "Reviewed: ..."`.
  Do not merge or remove branches or worktrees; `chitty run` lands passes.
- For unrelated work, use plain `chitty add` in the default context. Off the
  configured main branch, sequential contexts use a provisional ID marked
  `provisional: true`. Reference it like any other ID until renumbered on main. Use `-c human` for human work or
  `chitty suggest PROJECT` for another project. Do not do unrelated work here.
