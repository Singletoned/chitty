## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`.


- Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Work on one ticket per session. Start with `chitty show <ID>`.
- Read and change only files inside the ticket's worktree, including scratch
  files; do not touch the main checkout, other worktrees or files elsewhere on
  the machine. Tests may create temp directories. Reading other branches
  through Git or `chitty` is fine.
- Before writing code, write your approach with `chitty edit <ID> --plan`.
  Wait for approval if the human asked for it.
- With `autocommit = true`, Chitty commits ticket-file edits only. Commit
  code, tests, or other implementation files in small logical commits. Chitty
  adds a `Task: <ID>` trailer to each commit when it lands the ticket.
- Record surprises with `--note`. Format and commit your changes:
  `chitty edit -s review` runs the configured check and refuses if it fails or
  the worktree has uncommitted files. Use `--summary` for handoff, verification, and follow-ups.
- For a requested regression test, see it fail without the fix and note the
  result. If it passes, change the test until it fails without the fix.
- For missing or contradictory requirements, an unresolved design decision, a
  wrong claim about the code, files or other tickets, a criterion that cannot be
  verified as written or would pass with nothing built, a test a criterion needs
  that the ticket does not describe (its fixture, action and assertions), or a
  ticket too large to finish in one session, set `-s planning` (see omission
  exception below). At the first blocker, stop implementation, not investigation.
  Before changing status, finish reading the ticket and inspect relevant code
  and tests for remaining requirements. Explain what could not be checked and
  why; continue independent checks without speculating or expanding scope.
  In one note, give evidence of what was discovered, why the current ticket
  cannot guide the work, and what decision is needed or what must be corrected
  for each actionable issue. Do not work around the problem or weaken the tests.
  Preserve the existing branch and worktree; commit intended partial work and
  explain unfinished verification. On return, ownership is cleared and the run
  stops. Resume there after planning and cold-read readiness.
- For a cheap-to-reverse default, choose it only for a small omission. This
  applies only to choices the ticket leaves open where it and existing code or
  tests point to one clear default. Preserve requirements and acceptance
  criteria; add no user-visible policy, command, or setting. Note
  `Decided: <case> -> <choice>, because <reason>`, cite precedent, and add a
  focused test where testable. Do not invent or weaken tests needed to verify
  stated criteria. Contradictions, unclear or consequential choices, and other
  ticket defects go to `planning`.
- For external obstacles requiring help, note the problem, who can resolve it,
  and what is needed; then set `-s blocked`. Do not work blocked tickets. Leave
  `human` tickets in `todo`; never pick them up or block them.
- For unrelated work, plain `chitty add` files `BACKLOG`; planners use the main
  checkout for normal numbers. Use `-c human` for human work or
  `chitty suggest PROJECT` for another project. Do not do unrelated work here.
