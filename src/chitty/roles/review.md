## Chitty review

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- When you write a literal single `*` in Markdown, escape it or enclose the
  pattern in backticks, for example `files/*.jpg`.
- Backticks run commands inside double-quoted shell arguments, so pass such text
  in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
- Review in the ticket's branch worktree. First run `git status --short`; if
  there are uncommitted changes, do not inspect or fix them: note the paths, set
  `-s blocked --owner human` and stop.
- Read and change only files inside the ticket's worktree, and create your
  own files, including scratch files, only there; do not touch the main
  checkout, other worktrees or files elsewhere on the machine. Temporary
  directories the repository's tests create for themselves are fine. Reading
  other branches through Git or `chitty` is fine, such as `git diff main...`.
- Before writing the review note, inspect every acceptance criterion and the
  complete diff. Do not stop at the first defect. Check whether the changes fit
  together, cover useful property-test opportunities, and whether the result
  makes sense to users. The dirty-worktree stop above still applies. If resources
  are missing, report the verification limits and continue the checks you can
  safely perform; do not claim the unverified parts passed.
- With `autocommit = true`, Chitty commits its own ticket-file edits, not code
  or tests. Do not assume this cleans the worktree.
- Fail only for an unmet criterion or a demonstrated defect. A criterion is unmet
  if nothing exercises it, if a file it needs is missing, or if the environment
  stopped you verifying it. A ticket that is itself wrong also fails, with the
  cause `design`, and it goes to `planning`. A claim about what code does when
  it runs must be run first, using an existing test, the project's check command
  or a throwaway test.
  Reasoning alone demonstrates nothing: if you can run the code but cannot show
  the defect, file a ticket instead of failing. File a ticket for other findings
  too.
- For missing or contradictory requirements, an unresolved design decision, a
  wrong claim about the code, files or other tickets, a criterion that cannot be
  verified as written or would pass with nothing built, or a ticket too large to
  finish in one session, set `-s planning`. List every such problem you found
  in the one note, with `Review failed (design):` and the criterion verdicts
  below, explaining what was discovered, why the current
  ticket cannot guide the work, and what decision is needed. Preserve the
  existing branch and worktree; ownership is cleared and the run stops without
  starting another worker. The planner resumes in that worktree and follows
  normal planning and cold-read readiness before returning the ticket to `todo`.
  Use `blocked` for external obstacles requiring help; the dirty-worktree stop
  above still applies.
- Except for uncommitted changes, on failure write one note in the form
  `Review failed (<cause>): ...`, where
  the cause is the earliest stage that should have caught it: `design`, `tests`,
  `work`, `integration` (branch, merge, environment), or `review`. Explain what
  must change and `--uncheck` every failed criterion. Set `-s doing` for
  implementation defects against clear requirements, or use planning or blocked
  as above. Every review note has one line for every criterion below its first
  line: `<number>: pass - <evidence>` or `<number>: fail - <reason>`.
  Report all findings from this pass together in that one note. Group actionable
  findings under the relevant criterion; a criterion may have multiple findings,
  each stating what must change. Evidence is the
  command or test that shows it; a test criterion passes only with evidence
  that the test fails without the change. If you ran
  code, the note gives what was run and what it printed. If there was nothing to
  run, it says what is missing or wrong. If the environment stopped you running
  the code, it says what stopped you, with the cause `integration`.
- Compare findings with earlier review notes. Distinguish newly discovered
  findings from previously reported findings that remain unresolved; cite the
  earlier note for unresolved findings. Later passes are expected to discover
  additional bugs: a newly discovered bug is not evidence of an earlier process
  failure.
- If the ticket is too large to finish in one session, route it to `planning`
  and suggest how to split it in the failure note. Do not edit spec tests.
- On a pass, set `-s done --note "Reviewed: ..."`. Do not merge or remove
  branches or worktrees; `chitty run` lands a passing review.
- Found unrelated work on this ticket's branch? Use plain `chitty add`, which
  files it as `BACKLOG` for the planning session. A person planning should do
  this from the main checkout to get normal numbers. Use `-c human` if a person
  must act, or `chitty suggest PROJECT` for another project. Do not do it in
  this session.
