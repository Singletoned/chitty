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
  criteria. About five criteria is the limit; split larger work. Split a ticket when one criterion collects more than about five separate checks.
- Keep a new ticket in `backlog` until you start writing it. Move it to
  `-s planning` while you write it, to `-s cold-read` while a reader works on
  it, back to `-s planning` to record the outcomes, then to `-s todo`. Use its
  optional `parent` field to group flat IDs.
- For every read of a ticket, use the same fixed list of mutants (breaks the tests should catch), extending it only with survivors you fixed.
- Cold-read every ticket, even a small one. If it adds a module, tell its worker to first create it with the names the tests import, each raising `NotImplementedError`, so tests fail independently rather than at import. If it changes code, a fresh agent on a cheap model, close to the one that will do the work, implements it from the ticket alone in a throwaway worktree, and runs its tests with and without the fix. If there is nothing to run, a stronger model reads the ticket and referenced code instead. Either way, the reader reports done meaning, likely files, open decisions, unverified behaviour, unhandled states, and wrong claims. Fix or reject each finding in the ticket text, and give the outcomes in your reply, not in a ticket note. Ask whether odd existing behaviour is a bug before writing around it. Split rather than exceed about five criteria.
- A read that only probed does not make a ticket ready; read it again. Only an implementing read whose tests failed first does. Repeat the cold read after fixing a serious finding, until a read finds none: fixes are a source of new faults.
- Compare each decision in the description with the criteria, because workers
  test what criteria name. Say which test must fail without the fix, because a
  nearby test may already pass.
- Start the reader with the output of `chitty guide cold-read <ID>`, which holds
  its worktree, setup, cleanup and report steps. Add the code most at risk and
  what you doubt. A reader keeps an implementing read under
  `refs/cold-read/<ID>/<n>`; `git for-each-ref refs/cold-read` lists them.
  When a read implements the current ticket text and has no unresolved serious
  findings, add a ticket note as a possible starting point for the worker:
  the ticket's own paths, with their starting-point contents available via
  `git show <ref>:<path>`. Tell the worker to check it against
  the current criteria, not trust it. Delete refs from reads against superseded
  ticket text with `git update-ref -d refs/cold-read/<ID>/<n>`.
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
