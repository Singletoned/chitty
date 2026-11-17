## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`.

- When you write a literal single `*` in Markdown, escape it or enclose the
  pattern in backticks, for example `files/*.jpg`.

- Backticks run commands inside double-quoted shell arguments, so pass such text
  in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
- Work on one ticket per session. Start with `chitty show <ID>`.
- Read and change only files inside the ticket's worktree, and create your
  own files, including scratch files, only there; do not touch the main
  checkout, other worktrees or files elsewhere on the machine. Temporary
  directories the repository's tests create for themselves are fine. Reading
  other branches through Git or `chitty` is fine, such as `git diff main...`.
- Before writing code, write your approach with `chitty edit <ID> --plan`.
  Wait for approval if the human asked for it.
- With `autocommit = true`, Chitty commits ticket-file edits only. It does not
  commit code, tests, or other implementation files. Commit those in small
  logical commits ending with a `Task: <ID>` trailer; `chitty edit -s review`
  refuses branch commits without one.
- Record anything surprising with `--note`. When implementation is ready, run
  `chitty fix`, format and check, then commit your changes: `chitty edit -s
  review` refuses while the worktree has uncommitted files. Write `--summary`
  with handoff, verification, and follow-ups, then set `-s review`.
- When a ticket asks for a regression test, see it fail without the fix, by
  running it before you write the fix or with the fix reverted, and say so in
  a note. If it passes without the fix, it proves nothing: change the test
  until it fails without the fix.
- For missing or contradictory requirements, an unresolved design decision, a
  wrong claim about the code, files or other tickets, a criterion that cannot be
  verified as written or would pass with nothing built, or a ticket too large to
  finish in one session, always set `-s planning`. First finish reading the
  ticket and the code it touches, and list every such problem in one note
  explaining what was discovered, why the current ticket cannot guide the work, and what
  decision is needed. Do not work around the problem or weaken the tests.
  Preserve the existing branch and worktree; commit intended partial work and
  explain unfinished verification. On return, ownership is cleared and the run
  stops without starting another worker. The planner resumes in that worktree
  and follows normal planning and cold-read readiness before returning the
  ticket to `todo`.
- For a cheap-to-reverse default, choose it, note the choice and why for the
  reviewer, and comment the code where it applies. This applies only to choices
  the ticket leaves open; ticket defects go to planning instead.
- Use `blocked` for external obstacles requiring help. When blocked, note the
  problem, who can resolve it, and what is needed; then
  set `-s blocked`. Do not work blocked tickets. Leave `human` tickets in
  `todo`; never pick them up or block them.
- Found unrelated work on this ticket's branch? Use plain `chitty add`, which
  files it as `BACKLOG` for the planning session. A person planning should do
  this from the main checkout to get normal numbers. Use `-c human` if a person
  must act, or `chitty suggest PROJECT` for another project. Do not do it in
  this session.
