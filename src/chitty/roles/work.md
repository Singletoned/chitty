## Chitty work

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Work on one ticket per session. Start with `chitty inbox --pull`, then
  `chitty show <ID>`.
- Before writing code, write your approach with `chitty edit <ID> --plan`.
  Wait for approval if the human asked for it.
- Tick a criterion only after verifying it: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`). Re-check every criterion before setting
  `review`.
- Record anything surprising with `--note`. When implementation is ready, run
  `chitty fix`, write `--summary` with handoff, verification, and follow-ups,
  then set `-s review`.
- End task-work commits with `Task: <ID>` using that ticket's ID, so
  `git log --grep <ID>` finds them.
- When a ticket asks for a regression test, see it fail without the fix, by
  running it before you write the fix or with the fix reverted, and say so in
  a note. If it passes without the fix, it proves nothing: change the test
  until it fails without the fix. If the ticket itself is wrong, because
  following it would break something or a claim in it is false, do not work
  around it. That is a person's decision, however cheap the fix looks: note
  what you found and set `-s blocked`. An unclear detail with a cheap default
  is not this: choose it, as below.
- For a cheap-to-reverse default, choose it, note the choice and why for the
  reviewer, and comment the code where it applies. Block only for a costly
  reversal or a person decision.
- When blocked, note the problem, who can resolve it, and what is needed; then
  set `-s blocked`. Do not work blocked tickets. Leave `human` tickets in
  `todo`; never pick them up or block them.
- Found unrelated work? Use `chitty add` (`-c human` if a person must act), or
  `chitty suggest PROJECT` for another project. Do not do it in this session.
