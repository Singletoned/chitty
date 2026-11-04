## Chitty planning

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Put paths, globs, commands, IDs, and code in backticks in task titles,
  descriptions, criteria, and notes.
- Write tickets that a fresh agent can complete and another can verify: make
  criteria executable, state scope and out-of-scope work, make decisions,
  point to relevant files and callers, and keep one outcome to one to three
  criteria. About five criteria is the limit; split larger work.
- Keep a new ticket in `backlog` until its cold read findings have outcomes;
  then promote it to `todo`. Use its optional `parent` field to group flat IDs.
- Cold-read every ticket, even a small one: a fresh, cheaper agent reads only
  the ticket and referenced code, then reports done meaning, likely files,
  open decisions, unverified behaviour, unhandled states, and wrong claims.
  Record every finding's outcome in a ticket note: fix it or reject it with a
  specific reason. Ask whether odd existing behaviour is a bug before writing
  around it. Split rather than exceed about five criteria.
- Do not cold-read a ticket you were given to work on or review; it is not your
  planning step.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tickets in one batch.
