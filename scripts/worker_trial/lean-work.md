## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`.

Your job in this session is to implement the ticket and set it to `review`.

- Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Start with `chitty show <ID>`, then write your approach with `chitty edit <ID> --plan`.
- Work inside the ticket's worktree. Tests may create temp directories, and you
  may read other branches through Git or `chitty`.
- Commit code and tests in small logical commits. Chitty commits ticket-file
  edits itself.
- Where the ticket leaves a detail open, choose the simplest choice that fits
  the existing code, note `Decided: <case> -> <choice>, because <reason>`, and
  carry on.
- For a test the ticket says must fail without the change, run it before the
  change and note the result.
- When done, `chitty edit <ID> -s review --summary ...`. It runs the configured
  check and refuses if it fails or the worktree has uncommitted files; fix and
  retry.
- Only if the ticket cannot be implemented as written (two requirements
  contradict, or a claim about the code is false and the right fix is not
  clear), commit what you have and set `-s to-plan` with one note giving the
  evidence and the decision needed. Finding no defect is never a reason to
  return a ticket.
- Set `-s blocked` only for an obstacle outside the repository that a person
  must remove. Time, size and context are never obstacles.
- For unrelated work you find, use `chitty add`; do not do it here.
