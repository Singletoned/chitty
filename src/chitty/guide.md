## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Work on one task per session. Start with `chitty show <ID>`.
- Backlog tasks need refinement; promote them to `todo` before taking them on.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick acceptance criteria as you meet them: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`).
- Record anything surprising with `--note`. Set `-s done` when every
  criterion is ticked and the work is verified. Run `chitty fix` to apply
  safe repairs; it fails loudly when a problem remains.
- Found unrelated work? `chitty add` it (`-c human` if it needs a person).
  Don't do it in this session.
