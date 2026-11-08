## Chitty planning

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Put paths, globs, commands, IDs, and code in backticks in task titles,
  descriptions, criteria, and notes. When you write a literal single `*` in
  Markdown, escape it or enclose the pattern in backticks, for example
  `files/*.jpg`.
- Backticks run commands inside double-quoted shell arguments, so pass such text
  in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
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
- Repeat the cold read after fixing a serious finding, until a read finds none:
  fixes are a source of new faults.
- Compare each decision in the description with the criteria, because workers
  test what criteria name. Say which test must fail without the fix, because a
  nearby test may already pass.
- Start the reader with the output of `chitty guide cold-read <ID>`, which holds
  its worktree, setup, cleanup and report steps. Add the code most at risk and
  what you doubt. A reader keeps an implementing read under
  `refs/cold-read/<ID>/<n>`; `git for-each-ref refs/cold-read` lists them.
- Ask of each criterion: could it pass with nothing built? If so, name the case
  that fails today, and have the worker record that the test failed first.
- A worker cannot verify a criterion needing a real `chitty run` or agent
  session, and must not start one. Give that check to a person: a separate
  `-c human` ticket that depends on this one.
- Re-check claims about other tickets just before promoting, because they can
  land during the read.
- Do not cold-read a ticket you were given to work on or review; it is not your
  planning step.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tickets in one batch.
