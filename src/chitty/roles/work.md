## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`,
or run `chitty init`.

Optimise for less human work first, then cost-effective simplicity (automation
> agent > human).

- Pass text containing backticks or apostrophes through a `-file` option, using
  `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Work on one ticket per session. Start with `chitty show <ID>`.
- Stay inside the ticket's worktree (temp dirs for tests and reading other
  branches via Git or `chitty` are fine).
- Keep the design simple and ship a clean working version. Prefer boundary
  validation to defensive error handling — loud early failures are cheap to fix
  later, while defensive branches add complexity to maintain.
- Before writing code, write your approach with `chitty edit <ID> --plan`. Wait
  for approval if the human asked for it.
- Commit code and tests in small logical commits (`autocommit = true` commits
  ticket edits only). Chitty adds a `Task: <ID>` trailer on landing.
- For a bug-fix test, confirm it fails without the fix and note the result.
- Format and commit your changes, write a concise handoff in `--summary`, and
  move to `chitty edit -s review` (which runs the configured check and refuses
  if it fails or the worktree is dirty). Record surprises with `--note`.
- **Make decisions loudly:** when a small detail is open, the ticket has a
  minor typo or miscount, or there is one sensible default with no obvious
  competing alternative (e.g. a miscounted list or obvious fallback), choose
  it, note `Decided: <case> -> <choice>, because <reason>`, add a focused test
  where useful, and keep moving. Review can push back if it disagrees.
- **Return to `-s to-plan` only for real blockers:** a genuine contradiction,
  a false claim about the codebase, an unverifiable criterion, a consequential
  choice with competing alternatives where guessing risks failing review, or a
  ticket clearly too large for one session (propose a split).
  - Finish reading the ticket and checking the rest of the relevant code before
    bouncing.
  - Write one clear note giving the evidence and the decision needed, commit
    intended partial work, and set `-s to-plan`.
- **External obstacles (`-s blocked`):** write the `--summary` you would want
  to read with zero prior context — what the ticket is for, why it stopped, the
  options if a decision is needed, and your preferred option and why — then set
  `-s blocked`. Never block for time, token, or context budget.
- Leave `human` tickets in `todo`. File unrelated work with `chitty add` (or
  `-c human`, or `chitty suggest PROJECT`) rather than doing it here.
