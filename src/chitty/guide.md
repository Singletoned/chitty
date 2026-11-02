## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Put paths, globs, commands, IDs and code in backticks in titles, descriptions,
  criteria and notes.
- Work on one task per session. Start with `chitty inbox --pull`, then `chitty show <ID>`.
- Backlog tasks need refinement; promote them to `todo` before taking them on.
- Use a task's optional `parent` field to group flat task IDs under one goal.
- Unless your own instructions say otherwise, work in a branch in a worktree at
  `.worktrees/` in the repository root. In a worktree, use `autocommit = true`
  or commit after every Chitty write, so other branches can see task state.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick acceptance criteria as you meet them: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`).
- Record anything surprising with `--note`. When work is ready, set `-s review`.
  Never review a ticket you worked on: review promptly, rather than at
  merge-request time. Pass it with `-s done --note "Reviewed: ..."`; fail it
  with `-s doing --note "reason"`. If the work is on a branch, the reviewer who
  passes it merges it into `main` and removes the branch and its worktree.
  Create new tickets for out-of-scope findings.
  The third failed review sets `blocked` and owner `human` instead; leave it
  for a person to unblock.
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
