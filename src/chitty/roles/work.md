## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`.


- Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Work on one ticket per session. Start with `chitty show <ID>`.
- Read and change only files inside the ticket's worktree, including scratch
  files; do not touch the main checkout, other worktrees or files elsewhere on
  the machine. Tests may create temp directories, and you may read other
  branches through Git or `chitty`.
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
- Set `-s planning` when the ticket cannot guide the work (but see the omission
  exception below):
  - missing or contradictory requirements, or an unresolved design decision;
  - a wrong claim about the code, files or other tickets;
  - a criterion that cannot be verified as written or would pass with nothing
    built;
  - a test a criterion needs that the ticket does not describe (its fixture,
    action and assertions);
  - a ticket too large to finish in one session (propose a split).
- At the first such problem, stop implementation, not investigation:
  - Finish reading the ticket and inspect the relevant code and tests for the
    remaining requirements; continue independent checks without speculating or
    expanding scope.
  - Write one note giving, for each actionable issue, the evidence, why the
    ticket cannot guide the work, and the decision or correction needed. Say
    what could not be checked and why.
  - Do not work around the problem or weaken the tests.
  - Keep the branch and worktree; commit intended partial work and explain
    unfinished verification.
  - Setting `planning` clears ownership and stops the run. Resume there after
    planning and cold-read readiness.
- Omission exception: choose a cheap-to-reverse default only for a small
  omission, where the ticket leaves a choice open and it and existing code or
  tests point to one clear default.
  - Preserve requirements and acceptance criteria; add no user-visible policy,
    command, or setting. Do not invent or weaken tests needed to verify stated
    criteria.
  - Note `Decided: <case> -> <choice>, because <reason>`, cite the precedent,
    and add a focused test where testable.
  - Contradictions, unclear or consequential choices, and other ticket defects
    go to `planning`.
- For external obstacles requiring help, note the problem, who can resolve it,
  and what is needed; then set `-s blocked`. The session has no token, time or
  context budget to manage: budget, capacity, time or context is never a reason
  for `blocked`. Do not work blocked tickets.
- Leave `human` tickets in `todo`; never pick them up or block them.
- For unrelated work, use plain `chitty add` in the default context. Off the
  configured main branch, sequential contexts use a provisional ID marked
  `provisional: true`. Reference it like any other ID until renumbered on main. Use `-c human` for human work or
  `chitty suggest PROJECT` for another project. Do not do unrelated work here.
