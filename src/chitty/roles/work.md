## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`,
or run `chitty init`.

- Pass text containing backticks or apostrophes through a `-file` option, using
  `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Work on one ticket per session. Start with `chitty show <ID>`.
- Read and change only files inside the ticket's worktree (temp dirs for tests
  and reading other branches via Git or `chitty` are fine).
- Keep the design simple. Validate at boundaries so unexpected input fails
  loudly and early; do not add speculative defensive code for edge cases that
  are easy to handle later.
- Before writing code, write your approach with `chitty edit <ID> --plan`. Wait
  for approval if the human asked for it.
- Commit code and tests in small logical commits (`autocommit = true` commits
  ticket edits only). Chitty adds a `Task: <ID>` trailer on landing.
- For a bug-fix test, confirm it fails without the fix and note the result.
- Format and commit your changes, write a concise handoff in `--summary`, and
  move to `chitty edit -s review` (which runs the configured check and refuses
  if it fails or the worktree is dirty). Record surprises with `--note`.
- **Make decisions loudly:** if the ticket leaves a small detail open, has a
  minor typo or miscount, or has one sensible default with no obvious competing
  alternative, choose it, note `Decided: <case> -> <choice>, because <reason>`,
  add a focused test where useful, and keep moving. Let review push back if it
  disagrees.
- **Return to `-s planning` only for real blockers:** a genuine contradiction,
  a false claim about the codebase, an unverifiable criterion, a consequential
  choice with competing alternatives where guessing risks failing review, or a
  ticket clearly too large for one session (propose a split).
  - Finish reading the ticket and checking the rest of the relevant code before
    bouncing.
  - Write one clear note giving the evidence and the decision needed, commit
    intended partial work, and set `-s planning`.
- **External obstacles (`-s blocked`):** write a short, plain-English
  `--summary` for a human (what the ticket is for, why it stopped, and what
  action or decision is needed), then set `-s blocked`. Never block for time,
  token, or context budget.
- Leave `human` tickets in `todo`. File unrelated work with `chitty add` (or
  `-c human`, or `chitty suggest PROJECT`) rather than doing it here.
