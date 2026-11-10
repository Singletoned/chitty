## Chitty review

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- When you write a literal single `*` in Markdown, escape it or enclose the
  pattern in backticks, for example `files/*.jpg`.
- Backticks run commands inside double-quoted shell arguments, so pass such text
  in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
- Never review work you did. Review in the ticket's branch worktree, independently
  inspecting the ticket, every acceptance criterion, changes, and verification.
  First run `git status --short`. If the branch has uncommitted changes, do not
  inspect or fix them: record the paths and reason in a note, set `-s blocked`
  and `--owner human`, then stop. A review branch must be clean; a human decides
  how to resolve it and when to resume.
- Read and change only files inside the ticket's worktree, including scratch files; do not touch the main checkout, other worktrees or files elsewhere on the machine. Reading other branches through Git or `chitty` is fine, such as `git diff main...`.
- Verify first, then tick every verified criterion and add your note in one
  `chitty edit`, using repeated --check options, rather than one call for each.
- Request several reads in one call when none depends on another.
- Run the repository's format and check commands in one shell call, joined with
  `&&`.
- With `autocommit = true`, Chitty commits its own ticket-file edits, not code
  or tests. Do not assume this cleans the worktree.
- Fail only for an unmet criterion or a demonstrated defect. A criterion is unmet
  if nothing exercises it, if a file it needs is missing, or if the environment
  stopped you verifying it. A ticket that is itself wrong also fails, with the
  cause `design`. A claim about what code does when it runs must be run first,
  using an existing test, the project's check command or a throwaway test.
  Reasoning alone demonstrates nothing: if you can run the code but cannot show
  the defect, file a ticket instead of failing. File a ticket for other findings
  too.
- Except for uncommitted changes, on failure write one note in the form
  `Review failed (<cause>): ...`, where
  the cause is the earliest stage that should have caught it: `design`, `tests`,
  `work`, `integration` (branch, merge, environment), or `review`. Explain what
  must change and `--uncheck` every failed criterion. Set `-s doing`. If you ran
  code, the note gives what was run and what it printed. If there was nothing to
  run, it says what is missing or wrong. If the environment stopped you running
  the code, it says what stopped you, with the cause `integration`.
- If the ticket is too large, say so in the failure note and suggest how to
  split it. Do not edit spec tests.
- On a pass, set `-s done --note "Reviewed: ..."`. Do not merge or remove
  branches or worktrees; `chitty run` lands a passing review. The third failed
  review blocks the ticket for `human`; leave it there for a person to unblock.
- Found unrelated work on this ticket's branch? Use plain `chitty add`, which
  files it as `BACKLOG` for the planning session. A person planning should do
  this from the main checkout to get normal numbers. Use `-c human` if a person
  must act, or `chitty suggest PROJECT` for another project. Do not do it in
  this session.
