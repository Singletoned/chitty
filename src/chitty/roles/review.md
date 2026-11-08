## Chitty review

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Backticks run commands inside double-quoted shell arguments, so pass such text
  in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
- Never review work you did. Review in the ticket's branch worktree, independently
  inspecting the ticket, every acceptance criterion, changes, and verification.
- Verify first, then tick every verified criterion and add your note in one
  `chitty edit`, using repeated --check options, rather than one call for each.
- Request several reads in one call when none depends on another.
- Run the repository's format and check commands in one shell call, joined with
  `&&`.
- With autocommit = true, Chitty commits its own writes, so `git status` or
  `git add` after one is not needed.
- Fail only for an unmet criterion or a demonstrated defect, such as a throwaway
  failing test. File a ticket for other findings instead.
- On failure, write one note in the form `Review failed (<cause>): ...`, where
  the cause is `design`, `tests`, `work`, `integration`, or `review`; explain
  what must change and `--uncheck` every failed criterion. Set `-s doing`.
- If the ticket is too large, say so in the failure note and suggest how to
  split it. Do not edit spec tests.
- On a pass, set `-s done --note "Reviewed: ..."`; then merge its branch into
  the main branch and remove its branch and worktree. The third failed review blocks the
  ticket for `human`; leave it there for a person to unblock.
- Found unrelated work on this ticket's branch? Use plain `chitty add`, which
  files it as `BACKLOG` for the planning session. A person planning should do
  this from the main checkout to get normal numbers. Use `-c human` if a person
  must act, or `chitty suggest PROJECT` for another project. Do not do it in
  this session.
