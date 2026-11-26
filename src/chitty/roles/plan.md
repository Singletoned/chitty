## Chitty planning

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

Optimise for less human work first, then cost-effective simplicity (automation
> agent > human).

Label a ticket `untestable` when no test or check can show it is done (wording
in guides, docs, prompts, or content). Set its owner to `untestable` too and
skip the cold read. Describe the change and why it is needed; criteria are
optional. Agents read guides and prompts in every session, so a ticket adding
guide or prompt text says what it cuts to make room, or why they should grow.

- Put paths, globs, commands, IDs, and code in backticks in titles,
  descriptions, criteria, and notes. Pass text with backticks or apostrophes
  through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for
  stdin. Cite another project's ticket with its name first, for example
  `other TASK-4`.
- Write the ticket you would want to receive — short, simple, and easy for a
  human to read:
  - One outcome, 1–3 executable criteria, stated scope and out-of-scope, files
    and callers named. Split above 5 criteria (`chitty check` warns) or when a
    ticket is getting long.
  - Prefer the simplest design that is easy to extend later (complexity is
    expensive to maintain and cheap to add later). Ground input contracts in
    the real source (schema, callers, sample data) and prefer boundary
    validation to defensive error handling — loud early failures are cheap to
    fix later.
  - Rewrite descriptions cleanly so the ticket holds current truth only, and
    clear resolved notes with `--set-notes ''` before `todo` (Git keeps the
    history).
- Keep a new ticket in `backlog` until you work on it. Move it to `-s planning`
  while writing, `-s cold-read` for its cold read, back to `-s planning` to
  settle findings, then `-s todo`. Change status in the same edit as the text
  it depends on. Use `parent` to group flat IDs.
- Cold-read every ticket. If a change is too small to justify a ticket and cold
  read, do it directly (e.g. on a `hotfix/` branch) rather than ticketing it.
- Plan one ticket at a time. Check every claim about code, commands, tests, or
  other tickets against the source as you write it, and run `chitty check` on
  the ticket file before starting a reader.
- Start a fresh cheap-model reader with `chitty guide cold-read <ID>`, naming
  what you doubt.
- Cap cold reads at **1–2 rounds**: one read is enough if it finds no real
  blockers; run a second only after substantive edits. If a second read still
  finds serious problems, simplify, narrow, or split instead of patching again.
- Resolve reader findings by simplifying, narrowing the contract, or fixing
  real blockers — prefer changes that make the ticket shorter. Record outcomes
  in your reply rather than in a ticket note.
- Make each criterion fail without the change. Mark tests of kept behaviour
  after `Regression tests:` (they must pass, and need not fail without the
  change). If a ticket adds a new module, tell the worker to stub its exported
  names so tests fail independently rather than at import.
- Specify property tests by default: state the property, what inputs or state
  vary, and the repository's property-testing tool, leaving generator recipes
  and fixture wiring to the worker. Give a one-line reason when no property
  suits (fixed text, small fixed set listed and tested, external processes with
  no pure core, or code removal covered by existing tests).
<!-- property-signals -->
- Where logic can be a pure function, name it as an internal surface so tests
  can call it directly.
- A worker cannot verify a criterion needing a real `chitty run` or agent
  session; make that a separate `-c human` ticket that depends on this one.
- Check tickets mentioned by `chitty edit -s todo`. If a ticket relies on a
  contract an unfinished ticket is building, keep it in `planning` with a note
  naming that ticket and re-check once it lands (`depends_on` alone is enough
  for plain ordering).
- Skip cold-reading a ticket given to you to work on or review. Run
  `chitty archive` with no ID before preparing a merge request.
