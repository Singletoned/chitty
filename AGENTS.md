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
- Releases: bump `version` in `pyproject.toml`, commit, then push a tag
  `v<version>`. `.github/workflows/release.yml` checks, builds and publishes
  to PyPI by trusted publishing (environment `pypi`).
- Any change that existing repos only pick up by re-running `chitty init`
  (the managed guide block, `chitty.toml` template or upgrades, inbox
  registration) must bump `version` in `pyproject.toml`, at least at patch
  level, in the same change. The version recorded in `chitty.toml` is how
  other repos learn that `init` needs re-running (TASK-52).

## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Work on one task per session. Start with `chitty pull`, then `chitty show <ID>`.
- Backlog tasks need refinement; promote them to `todo` before taking them on.
- Use a task's optional `parent` field to group flat task IDs under one goal.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick acceptance criteria as you meet them: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`).
- Record anything surprising with `--note`. When work is ready, set `-s review`.
  Never review a ticket you worked on: review promptly, rather than at
  merge-request time. Pass it with `-s done --note "Reviewed: ..."`; fail it
  with `-s doing --note "reason"`. Create new tickets for out-of-scope findings.
- Set `-s done` when every criterion is ticked and the work is verified; write
  `--summary` with the handoff, verification, and follow-ups. Run `chitty fix`
  to apply safe repairs; it fails loudly when a problem remains.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tasks in one batch. The default moves them to `archive/`; with
  `archive = "delete"`, Git history retains the record instead.
- End commits for task work with `Task: TASK-N` lines so `git log --grep TASK-N`
  finds the ticket's code. This is a convention; no hook enforces it.
- When work cannot proceed, set `-s blocked --note "reason"` and move on; do
  not pick up blocked work. If a person must act outside the repo, add a
  `-c human` task and depend on it.
- Found unrelated work? `chitty add` it (`-c human` if it needs a person).
  Suggest work for another project without touching its checkout using
  `chitty suggest PROJECT "title" -d "why"`.
  Don't do it in this session.
