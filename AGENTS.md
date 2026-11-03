# Agents

Chitty is a markdown-native task tracker. `PLAN.md` is the design; read it
before changing behaviour, and update it when a decision changes.

- `make install` once (Python deps including the `mcp` extra, and the pinned
  prettier used by the round-trip tests).
- `make check` (ruff, pyright, unittest) before every commit. `make format`
  to fix formatting.
- Tests use `unittest` and write real files in temp dirs; no filesystem
  mocking. Tests that use the inbox must inherit `RepoTestCase`, which assigns
  a temporary `XDG_DATA_HOME` so they never touch the real inbox. The formatter
  tests fail, never skip, if prettier or mdformat is missing.
- `cli.py` and `mcp.py` stay thin: behaviour lives in `store.py` and
  `model.py` so the two front ends cannot diverge.
- Cold-read every ticket before it reaches `todo`, or before work starts if it
  is already there: a fresh session or subagent that did not write the ticket,
  on a cheaper model, reads only the ticket and the code it points at, and
  reports what done means, the files it would change, decisions left open,
  stated behaviour no criterion verifies, unhandled starting states, and claims
  that are wrong. The author fixes the ticket and records in a note what was
  adopted or rejected. See `PLAN.md`, "Pipeline and feedback".
- Releases: bump `__version__` in `src/chitty/__init__.py`, commit, then push a
  tag `v<version>`. `.github/workflows/release.yml` checks, builds and publishes
  to PyPI by trusted publishing (environment `pypi`).
- Any change that existing repos only pick up by re-running `chitty init`
  (the managed guide block, `chitty.toml` template or upgrades, inbox
  registration) must bump `__version__` in `src/chitty/__init__.py`, at least at patch
  level, in the same change. The version recorded in `chitty.toml` is how
  other repos learn that `init` needs re-running (TASK-52).

## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Put paths, globs, commands, IDs and code in backticks in titles, descriptions,
  criteria and notes.
- Work on one task per session. Start with `chitty inbox --pull`, then `chitty show <ID>`.
- Backlog tasks need refinement; promote them to `todo` before taking them on.
- Use a task's optional `parent` field to group flat task IDs under one goal.
- Unless your own instructions say otherwise, create a branch and worktree at
  `.worktrees/` in the repository root from `main` for each new ticket; never
  implement in the main checkout. Resume the existing worktree for a `doing`
  ticket. Run the repository's setup command in a new worktree before coding so
  it creates that worktree's environment. Commit the `doing` claim on its
  branch before implementation starts, and use `autocommit = true` or commit
  after every Chitty write so other branches can see task state. Run ticket
  writes from the branch holding its latest committed version; Chitty refuses
  to route a write across branches and tells you where to run it.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick a criterion only after verifying it: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`). Re-check every criterion before setting
  `-s review`.
- Record anything surprising with `--note`. When work is ready, set `-s review`.
  Never review a ticket you worked on: review promptly in the ticket's branch
  worktree, rather than at merge-request time. Review every criterion; list
  every failure in one note and `--uncheck` each failed criterion. Pass it with
  `-s done --note "Reviewed: ..."`; fail it with `-s doing --note "reason"`.
  On a pass, merge the branch into `main`, then remove the branch and its
  worktree. Create new tickets for out-of-scope findings. The third failed
  review sets `blocked` and owner `human` instead; leave it for a person to
  unblock.
- Set `-s done` when every criterion is ticked and the work is verified; write
  `--summary` with the handoff, verification, and follow-ups. Run `chitty fix`
  to apply safe repairs; it fails loudly when a problem remains.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tasks in one batch. The default moves them to `archive/`; with
  `archive = "delete"`, Git history retains the record instead.
- End commits for task work with `Task: <ID>` lines using the ticket's own ID
  (for example, `Task: TASK-12`) so `git log --grep <ID>` finds a ticket's
  code. This is a convention; no hook enforces it.
- When a question has a sensible default that is cheap to change later, choose
  it and carry on instead of blocking. Record the choice and why with `--note`
  for the reviewer, and comment the code where the default applies, saying how
  and why it was chosen. Block only when the choice is costly to reverse or
  needs a person.
- When work cannot proceed, set `-s blocked --note "reason"` and move on; do
  not pick up blocked work. If a person must act outside the repo, add a
  `-c human` task and depend on it. Leave `human` tasks in `todo` for people;
  never pick them up or block them.
- Found unrelated work? `chitty add` it (`-c human` if it needs a person).
  Suggest work for another project without touching its checkout using
  `chitty suggest PROJECT "title" -d "why"`.
  Don't do it in this session.
