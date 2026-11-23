## Chitty planning

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

Label a ticket `untestable` when it can't be tested: no test or check can show
it is done, and a reviewer could only compare it with its own criteria. Wording
in guides, docs and prompts, and content writing, are usually untestable. Set
its owner to `untestable` too, so the runner leaves it alone, and skip the cold
read. Describe the change and why it is needed; criteria are optional. Agents
read the guides and prompts in every session, so a ticket that adds text to
agent guides or prompts says what it cuts to make room, or why they should
grow.

- Put paths, globs, commands, IDs, and code in backticks in task titles,
  descriptions, criteria, and notes.
- Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Write tickets that a fresh agent can complete and another can verify: make
  criteria executable, state scope and out-of-scope work, make decisions,
  point to relevant files and callers, and keep one outcome to one to three
  criteria. Err on the side of splitting: a ticket that seems too small is not
  a problem. `chitty check` warns above five criteria; split larger work. Split a ticket
  when one criterion collects more than about five separate checks.
- Keep a new ticket in `backlog` until you start writing it. Move it to
  `-s planning` while you write it, to `-s cold-read` for its cold read, back to `-s planning` to record outcomes, then to `-s todo`. Use
  its optional `parent` field to group flat IDs.
- Cold-read every ticket, even a small one. A fresh agent on a cheap model
  close to the worker reads the ticket and the named code and documents, then
  reports without changing the checkout. If a ticket adds a module, tell its
  worker to first create it with the names the tests import, each raising
  `NotImplementedError`, so tests fail independently rather than at import.
- When the code a ticket tests already exists, a stub cannot show the tests
  fail without the change. List plausible wrong versions of the code instead,
  such as a dropped condition or a swapped choice. For example-based tests, ask
  the worker to commit each wrong version as a test asserting it fails; where
  that is impractical, ask for a run recorded in a note, and say why. For
  property tests, run the generators against each wrong version while planning
  and fix any that let one pass; the worker re-runs them once against each and
  notes the result. These wrong versions are not committed.
- When the code already exists, run each specified generator recipe against
  it before the cold read, with many cases, and check the expected answers
  agree. A disagreement is a wrong recipe or a bug; settle which.
- Build distractor values, such as similar names a lookup must ignore, from the
  drawn value itself, so they can never equal it by chance.
- Check every claim about code, commands, tests or other tickets against the
  source as you write it, not from memory or a summary; otherwise readers spend
  their rounds on your fixes. Run `chitty check` on the ticket file and fix what
  it reports before starting a reader.
- Plan one ticket at a time: write, read and settle it before starting the
  next. Fixes written for several tickets at once drift from the code.
- After a fix that changes what a worker builds, cold-read the ticket again,
  even when the reader suggested the fix and tried it itself. Move a ticket to
  `todo` only after a read that finds nothing serious. If a third read still
  finds serious problems, split the ticket rather than patching it.
- Ask of each criterion: could it pass with nothing built? If so, name the case
  that fails today, and say which test must fail without the fix.
- In the original planning session, perform a sufficiency read on the current
  ticket text, the named code and documents, and the reader report. Inspect
  each criterion individually and the ticket as a whole: could a plausible
  minimal implementation satisfy the criteria yet reasonably fail a good
  review? For each gap, give a concrete counterexample, relevant inputs or
  state, a distinguishing test and observable result, and proposed criterion
  wording. Prefer a general property over accumulating examples. Do not invent
  speculative features; relate the gap to the problem and agreed scope. Ask
  whether odd existing behaviour is a bug before writing around it.
- Before moving to `todo`, resolve every reader finding and sufficiency gap:
  strengthen the ticket, split it, or explicitly reject the finding as out of
  scope. Write requirements needed to reject the implementation into the ticket,
  not just the planning conversation. Give the outcomes in your reply, not in a
  ticket note. Split rather than exceed about five criteria. The expected route
  for a problem the read missed is a return to planning by its worker or
  reviewer. A stronger reader remains optional for uncertainty or repeated
  work–review failures, not mandatory.
- Specify property tests by default. Compare each decision in the description
  with the criteria, because workers test what criteria name. For each
  behaviour, write the property and what the test generates: the inputs and
  the state the behaviour depends on, such as files present, branches and
  config. For example, "for any criteria list and valid N, only criterion N
  changes", or "for any set of directories, each on disk, only on another
  branch, or both, `show` finds every ticket".
- Name the repository's property-testing tool. Generated means many inputs
  drawn by that tool, not a few hand-picked cases. If the repository has no
  such tool, say whether the ticket adds one.
- When a behaviour has no property, give the reason in one line. Valid
  reasons: fixed text with no input, such as a docs-only change; a small fixed
  set, with every member listed in the ticket and each one tested; behaviour
  that needs real external processes, with why no pure core can be taken out
  of it and given properties; or a change that only removes code, with the
  existing tests that cover what remains.
- Say which test must fail without the fix, because a nearby test may already
  pass.
<!-- property-signals -->
- Where behaviour can be a pure function, taking values and returning values
  with no file, network or clock access inside it, have the ticket name that
  function and state its properties: it is far easier to test. A function,
  module or internal API (such as a facade) the ticket names is an internal
  surface and part of its spec, so its tests may call it directly.
- Start the reader with the output of `chitty guide cold-read <ID>`. Add the
  code most at risk and what you doubt.
- A worker cannot verify a criterion needing a real `chitty run` or agent
  session, and must not start one. Give that check to a person: a separate
  `-c human` ticket that depends on this one.
- `chitty edit -s todo` lists the tickets a ticket mentions: check that its claims about them still hold.
- If a ticket's text relies on something an unfinished ticket is building,
  such as a function, file, format or setting, keep it in `planning` with a
  note naming that ticket. When that ticket is done, compare this one with
  what actually landed, cold-read it again, then move it to `todo`. If a
  ticket only has to land after another and describes nothing of its work,
  `depends_on` is enough and it can go to `todo` now.
- Change a ticket's status in the same edit command as the text it depends
  on, so a rejected edit cannot move the ticket on.
- Do not cold-read a ticket you were given to work on or review; it is not your
  planning step.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tickets in one batch.
