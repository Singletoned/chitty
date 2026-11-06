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
- Cold-read every ticket, even a small one. If it changes code, a fresh agent on
  a cheap model, close to the one that will do the work, implements it from the
  ticket alone in a throwaway worktree, and runs its tests with and without the
  fix. If there is nothing to run, a stronger model reads the ticket and
  referenced code instead. Either way, the reader reports done meaning, likely
  files, open decisions, unverified behaviour, unhandled states, and wrong
  claims. Record every finding's outcome in a ticket note: fix it or reject it
  with a specific reason. Ask whether odd existing behaviour is a bug before
  writing around it. Split rather than exceed about five criteria.
- Start an implementing read with `git worktree add --detach .worktrees/read-<ID>`
  and the repository's setup command, not on a branch, because Chitty reads
  tickets from every branch. Run the reader with `VIRTUAL_ENV` and
  `UV_PROJECT_ENVIRONMENT` unset, or a shared install ends up pointing at a
  worktree about to be deleted. The reader runs no Chitty writes and leaves
  `chitty/` unchanged. It commits its own work and, from inside the worktree,
  keeps it with `git update-ref refs/cold-read/<ID>/<n> HEAD`, where `<n>` is the
  next number free for that ticket, starting at 1, then runs `git worktree
  remove --force .worktrees/read-<ID>`. `git for-each-ref refs/cold-read` lists
  kept reads.
- Ask of each criterion: could it pass with nothing built? If so, name the case
  that fails today, and have the worker record that the test failed first.
- A worker cannot verify a criterion needing a real `chitty run` or agent
  session, and must not start one. Give that check to a person: a separate
  `-c human` ticket that depends on this one.
- Give the cold reader the ticket ID, the code most at risk and what you doubt.
  Ask it to try behaviour where it can rather than assume, and to report each
  finding with file, line, why it matters and the exact wording to change.
- Re-check claims about other tickets just before promoting, because they can
  land during the read.
- Do not cold-read a ticket you were given to work on or review; it is not your
  planning step.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tickets in one batch.
