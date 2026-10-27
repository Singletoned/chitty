# Agents

Chitty is a markdown-native task tracker. `PLAN.md` is the design; read it
before changing behaviour, and update it when a decision changes.

- `make install` once (Python deps including the `mcp` extra, and the pinned
  prettier used by the round-trip tests).
- `make check` (ruff, pyright, unittest) before every commit. `make format`
  to fix formatting.
- Tests use `unittest` and write real files in temp dirs; no filesystem
  mocking. The formatter tests fail, never skip, if prettier or mdformat is
  missing.
- `cli.py` and `mcp.py` stay thin: behaviour lives in `store.py` and
  `model.py` so the two front ends cannot diverge.
- Releases: bump `version` in `pyproject.toml`, commit, then push a tag
  `v<version>`. `.github/workflows/release.yml` checks, builds and publishes
  to PyPI by trusted publishing (environment `pypi`).

## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Work on one task per session. Start with `chitty show <ID>`.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick acceptance criteria as you meet them: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`).
- Record anything surprising with `--note`. Set `-s done` when every
  criterion is ticked and the work is verified.
- When blocked, set `-s blocked --note "reason"`, do not pick the task back
  up, and move on. If a person must act outside the repo, add a `-c human`
  ticket and depend on it.
- Found unrelated work? `chitty add` it (`-c human` if it needs a person).
  Don't do it in this session.
